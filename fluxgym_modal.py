import modal
from pathlib import Path

# Create a Modal app
app = modal.App("fluxgym-simple")

# Build FluxGym image from source (more reliable)
fluxgym_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "wget", "curl", "build-essential")
    .pip_install(
        "torch>=2.0.0",
        "torchvision",
        "transformers>=4.25.0",
        "diffusers>=0.21.0",
        "accelerate>=0.20.0",
        "datasets",
        "gradio>=4.0.0",
        "huggingface-hub",
        "safetensors>=0.3.1",
        "peft>=0.4.0",
        "bitsandbytes",
        "opencv-python",
        "pillow",
        "numpy",
        "tqdm",
        "wandb",
        "tensorboard",
        "omegaconf",
        "prodigyopt",
        "lycoris-lora"
    )
    .run_commands(
        "git clone https://github.com/cocktailpeanut/fluxgym.git /fluxgym",
        "cd /fluxgym && git clone -b sd3 https://github.com/kohya-ss/sd-scripts",
        "cd /fluxgym/sd-scripts && pip install -r requirements.txt",
    )
)

# Create a volume for persistent storage
volume = modal.Volume.from_name("fluxgym-data", create_if_missing=True)

# Secret for Hugging Face (needed for Flux model)
huggingface_secret = modal.Secret.from_name(
    "huggingface-secret", 
    required_keys=["HF_TOKEN"]
)

@app.function(
    image=fluxgym_image,
    gpu="A100-40GB",
    volumes={"/data": volume},
    secrets=[huggingface_secret],
    timeout=7200,  # 2 hours
)
@modal.asgi_app()
def fluxgym_gradio():
    """
    Run FluxGym as a Gradio app on Modal
    """
    import gradio as gr
    import os
    import sys
    import subprocess
    from pathlib import Path
    
    # Add FluxGym to Python path
    sys.path.insert(0, "/fluxgym")
    
    # Set environment variables
    os.environ["HF_HOME"] = "/data/huggingface"
    os.environ["TORCH_HOME"] = "/data/torch"
    
    # Create necessary directories
    Path("/data/models").mkdir(exist_ok=True)
    Path("/data/datasets").mkdir(exist_ok=True)
    Path("/data/outputs").mkdir(exist_ok=True)
    
    def train_flux_lora(
        dataset_folder,
        model_name="black-forest-labs/FLUX.1-dev",
        trigger_word="ohwx",
        max_train_steps=1000,
        learning_rate=1e-4,
        rank=16,
        alpha=16,
        resolution=512,
        batch_size=1,
        progress=gr.Progress()
    ):
        """Train Flux LoRA with FluxGym backend"""
        try:
            progress(0, desc="Starting training...")
            
            # Prepare training command
            cmd = [
                "python", "/fluxgym/sd-scripts/flux_train_network.py",
                f"--pretrained_model_name_or_path={model_name}",
                f"--dataset_config=/data/config.toml",
                f"--output_dir=/data/outputs",
                f"--output_name=flux_lora_{trigger_word}",
                f"--max_train_steps={max_train_steps}",
                f"--learning_rate={learning_rate}",
                f"--network_dim={rank}",
                f"--network_alpha={alpha}",
                f"--resolution={resolution}",
                f"--train_batch_size={batch_size}",
                "--network_module=networks.lora",
                "--mixed_precision=bf16",
                "--save_precision=bf16",
                "--cache_latents",
                "--optimizer_type=AdamW8bit",
                "--max_data_loader_n_workers=8",
                "--bucket_reso_steps=64",
                "--bucket_no_upscale",
                "--noise_offset=0.0357",
            ]
            
            progress(0.1, desc="Initializing training process...")
            
            # Run training
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="/fluxgym")
            
            if result.returncode == 0:
                progress(1.0, desc="Training completed successfully!")
                return f"✅ Training completed!\n\nOutput:\n{result.stdout}"
            else:
                return f"❌ Training failed!\n\nError:\n{result.stderr}"
                
        except Exception as e:
            return f"❌ Error during training: {str(e)}"
    
    def list_models():
        """List available trained models"""
        output_dir = Path("/data/outputs")
        if output_dir.exists():
            models = list(output_dir.glob("*.safetensors"))
            return [model.name for model in models]
        return []
    
    # Create Gradio interface
    with gr.Blocks(title="FluxGym on Modal", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🚀 FluxGym on Modal")
        gr.Markdown("Train Flux LoRAs in the cloud with high-end GPUs!")
        
        with gr.Tab("Training"):
            with gr.Row():
                with gr.Column():
                    dataset_input = gr.Textbox(
                        label="Dataset Path",
                        placeholder="/data/datasets/my_dataset",
                        info="Path to your training images"
                    )
                    trigger_word = gr.Textbox(
                        label="Trigger Word",
                        value="ohwx",
                        info="Word to trigger your concept"
                    )
                    model_name = gr.Dropdown(
                        choices=[
                            "black-forest-labs/FLUX.1-dev",
                            "black-forest-labs/FLUX.1-schnell"
                        ],
                        value="black-forest-labs/FLUX.1-dev",
                        label="Base Model"
                    )
                
                with gr.Column():
                    max_steps = gr.Slider(
                        minimum=100,
                        maximum=5000,
                        value=1000,
                        step=100,
                        label="Max Training Steps"
                    )
                    learning_rate = gr.Slider(
                        minimum=1e-6,
                        maximum=1e-3,
                        value=1e-4,
                        step=1e-6,
                        label="Learning Rate"
                    )
                    rank = gr.Slider(
                        minimum=4,
                        maximum=128,
                        value=16,
                        step=4,
                        label="LoRA Rank"
                    )
            
            train_btn = gr.Button("🚀 Start Training", variant="primary", size="lg")
            output = gr.Textbox(label="Training Output", lines=10)
            
            train_btn.click(
                fn=train_flux_lora,
                inputs=[dataset_input, model_name, trigger_word, max_steps, learning_rate, rank],
                outputs=output
            )
        
        with gr.Tab("Models"):
            gr.Markdown("### Trained Models")
            refresh_btn = gr.Button("🔄 Refresh List")
            model_list = gr.Dataframe(headers=["Model Name"], label="Available Models")
            
            refresh_btn.click(
                fn=lambda: [[model] for model in list_models()],
                outputs=model_list
            )
        
        with gr.Tab("Upload Dataset"):
            gr.Markdown("### Upload Training Images")
            gr.Markdown("Upload 10-20 images of your subject for training")
            
            file_upload = gr.File(
                file_count="multiple",
                file_types=["image"],
                label="Training Images"
            )
            
            def save_uploaded_files(files):
                if not files:
                    return "No files uploaded"
                
                upload_dir = Path("/data/datasets/uploaded")
                upload_dir.mkdir(parents=True, exist_ok=True)
                
                saved_files = []
                for file in files:
                    if file is not None:
                        # Copy file to dataset directory
                        import shutil
                        dest = upload_dir / Path(file.orig_name).name
                        shutil.copy2(file.name, dest)
                        saved_files.append(dest.name)
                
                return f"✅ Saved {len(saved_files)} files to /data/datasets/uploaded/"
            
            upload_btn = gr.Button("💾 Save Dataset")
            upload_output = gr.Textbox(label="Upload Status")
            
            upload_btn.click(
                fn=save_uploaded_files,
                inputs=file_upload,
                outputs=upload_output
            )
    
    return demo

# Simple training function that can be called directly
@app.function(
    image=fluxgym_image,
    gpu="A100-40GB",
    volumes={"/data": volume},
    secrets=[huggingface_secret],
    timeout=7200
)
def train_lora_direct(
    dataset_path: str,
    trigger_word: str = "ohwx",
    steps: int = 1000,
    learning_rate: float = 1e-4
):
    """Direct training function without UI"""
    import subprocess
    import os
    
    os.environ["HF_TOKEN"] = os.environ.get("HF_TOKEN", "")
    
    cmd = [
        "python", "/fluxgym/sd-scripts/flux_train_network.py",
        f"--pretrained_model_name_or_path=black-forest-labs/FLUX.1-dev",
        f"--train_data_dir={dataset_path}",
        f"--output_dir=/data/outputs",
        f"--output_name=flux_lora_{trigger_word}",
        f"--max_train_steps={steps}",
        f"--learning_rate={learning_rate}",
        "--network_module=networks.lora",
        "--network_dim=16",
        "--network_alpha=16",
        "--resolution=512",
        "--train_batch_size=1",
        "--mixed_precision=bf16",
        "--save_precision=bf16",
        "--cache_latents",
        "--optimizer_type=AdamW8bit",
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr if result.returncode != 0 else None
    }

# Deployment commands
@app.local_entrypoint()
def deploy():
    print("🚀 Deploying FluxGym on Modal...")
    print("After deployment, you'll get a URL to access the FluxGym interface")
    print("Make sure you have set up your HuggingFace token as a Modal secret:")
    print("modal secret create huggingface-secret HF_TOKEN=your_token_here")

@app.local_entrypoint()
def serve():
    print("🧪 Running FluxGym in development mode...")
    print("This will give you a temporary URL for testing")