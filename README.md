# Alaiy-Skill-Test

A brand-consistent fashion design generation system using Flux LoRA models to create new clothing designs that match specific brand visual identities.

## Problem Statement

Fashion brands have unique visual identities (H&M looks different from Zudio/Zara) even within the same category. In fast-fashion, design teams need to generate brand-consistent clothing designs rapidly without lengthy design or approval cycles.

## Solution

This design engine can:
- Understand and replicate the visual language of specific brands and categories
- Create new design ideas from text prompts or prompt + reference image combinations
- Generate designs that are visually aligned with the target brand

**Supported Generation Types:**
- Text → Image (prompt-based design generation)
- Text + Image → Image (style transfer with brand consistency)

## Supported Brands

Currently trained LoRA models available for:
- **Abercrombie & Fitch** - [Download LoRA](https://huggingface.co/Narpear/abercrombiestylelora)
- **Chubbies Shorts** - [Download LoRA](https://huggingface.co/Narpear/chubbiesstylelora)

## Quick Start

### 1. Data Scraping

Navigate to the brand-specific dataset folder and run the scraping pipeline:

```{bash}
# For Abercrombie & Fitch
cd Dataset_final/ANF

# Step 1: Scrape product URLs, image links, and descriptions
python scraper.py

# Step 2: Download images from scraped links
python img_downloader.py
```
Note: Follow the same process for Chubbies Shorts using the corresponding files in the Chubbies folder.


### 2. LoRA Training

Train your custom LoRA model using FluxGym:

```{bash}
modal serve app.py
```

This opens FluxGym where you can:

- Load your scraped images
- Set base model parameters
- Configure hyperparameters
- Train the LoRA model
- Export as .safetensors file



### 3. ComfyUI Setup

Set up ComfyUI for design generation:

1. Clone the Modal examples repository:
```{bash}
git clone https://github.com/modal-labs/modal-examples
```

Navigate to their hf_download function in /06_gpu_and_ml/comfyui/comfyapp.py add add this additional code there to use additional models and model-parts
```{python}
    # Download Flux Dev base model
    flux_model = hf_hub_download(
        repo_id="black-forest-labs/FLUX.1-dev",
        filename="flux1-dev.safetensors",
        cache_dir="/cache",
        token=HF_TOKEN,
    )
    subprocess.run(
        f"ln -s {flux_model} /root/comfy/ComfyUI/models/checkpoints/flux1-dev.safetensors",
        shell=True, check=True,
    )

    # Download Abercrombie LoRA
    abercrombie_lora = hf_hub_download(
        repo_id="Narpear/abercrombiestylelora",
        filename="abercrombiestylelora.safetensors",
        cache_dir="/cache",
        token=HF_TOKEN,
    )
    subprocess.run(
        f"ln -s {abercrombie_lora} /root/comfy/ComfyUI/models/loras/abercrombiestylelora.safetensors",
        shell=True, check=True,
    )

    # Download Chubbies LoRA
    chubbies_lora = hf_hub_download(
        repo_id="Narpear/chubbiesstylelora",
        filename="chubbiesstylelora.safetensors",
        cache_dir="/cache",
        token=HF_TOKEN,
    )
    subprocess.run(
        f"ln -s {chubbies_lora} /root/comfy/ComfyUI/models/loras/chubbiesstylelora.safetensors",
        shell=True, check=True,
    )

    # Download T5-XXL text encoder (required for Flux)
    t5_model = hf_hub_download(
        repo_id="comfyanonymous/flux_text_encoders",
        filename="t5xxl_fp16.safetensors",
        cache_dir="/cache",
        token=HF_TOKEN,
    )
    subprocess.run(
        f"ln -s {t5_model} /root/comfy/ComfyUI/models/text_encoders/t5xxl_fp16.safetensors",
        shell=True, check=True,
    )

    # Download CLIP-L text encoder (required for Flux)
    clip_l_model = hf_hub_download(
        repo_id="comfyanonymous/flux_text_encoders",
        filename="clip_l.safetensors",
        cache_dir="/cache",
        token=HF_TOKEN,
    )
    subprocess.run(
        f"ln -s {clip_l_model} /root/comfy/ComfyUI/models/text_encoders/clip_l.safetensors",
        shell=True, check=True,
    )

    # Download Flux VAE
    flux_vae = hf_hub_download(
        repo_id="black-forest-labs/FLUX.1-dev",
        filename="ae.safetensors",
        cache_dir="/cache",
        token=HF_TOKEN,
    )
    subprocess.run(
        f"ln -s {flux_vae} /root/comfy/ComfyUI/models/vae/ae.safetensors",
        shell=True, check=True,
    )
```

Navigate to the parent folder and run 
```{bash}
modal serve comfyapp.py
```

This opens up ComfyUI on the web, where you can setup the workflow (you can pick from the Workflows folder in this repository) and run the inputs through the model.

### Training and Testing

Training details can be found here - https://docs.google.com/document/d/1z1MBli8yX5czprHs_akj4uwm7qUqGneVYiSQpE2Dm5U/edit?tab=t.0

Testing details and outputs can be found here (this has multiple examples of everything!) - https://docs.google.com/document/d/1x7zCrUw26WZjhMh95F9AHVYRvkrLBztpFTQuo_ucdws/edit?tab=t.0



