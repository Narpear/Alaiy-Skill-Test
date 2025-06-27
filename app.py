# From https://github.com/Dragoy/fluxgym-modal
# Built extra support functions

import subprocess
import os
import modal
from modal import (App, Image, web_server, Secret, Volume)

cuda_version = "12.4.0"
flavor = "devel"
operating_sys = "ubuntu22.04"
tag = f"{cuda_version}-{flavor}-{operating_sys}"

GRADIO_PORT = 7860

volume = Volume.from_name("fluxgym-output", create_if_missing=True)

image = (
    Image.from_registry(f"nvidia/cuda:{tag}", add_python="3.11")
    .apt_install("libgl1", "libglib2.0-0", "git")
    .run_commands("git clone https://github.com/cocktailpeanut/fluxgym.git /root/fluxgym")
    .run_commands("cd /root/fluxgym && pip install -r requirements.txt")
    .run_commands("cd /root/fluxgym && git clone -b sd3 https://github.com/kohya-ss/sd-scripts.git /root/fluxgym/sd-scripts")
    .run_commands("cd /root/fluxgym/sd-scripts && pip install -r requirements.txt")
    .run_commands("rm -rf /root/fluxgym/outputs")
)

app = App(
    "fluxgym-trainer",
    image=image,
    secrets=[Secret.from_name("huggingface-secret")]
)

@app.cls(
    gpu="A100",
    image=image,
    concurrency_limit=1,
    timeout=7200,
    allow_concurrent_inputs=100,
    volumes={"/root/fluxgym/outputs": volume}
)

class FluxGymApp:
    def run_gradio(self):
        os.chdir("/root/fluxgym")
        print("Changed directory to /root/fluxgym")
        os.environ["HF_TOKEN"] = os.environ.get("HUGGINGFACE_SECRET", "")
        os.environ["GRADIO_SERVER_NAME"] = "0.0.0.0"
        os.environ["GRADIO_SERVER_PORT"] = str(GRADIO_PORT)
        os.environ["GRADIO_SERVER_HEARTBEAT_TIMEOUT"] = "7200"
        cmd = "python app.py"
        subprocess.Popen(cmd, shell=True)

    @web_server(GRADIO_PORT, startup_timeout=120)
    def ui(self):
        print("Starting FluxGym application...")
        self.run_gradio()

    @modal.method()
    def list_outputs(self):
        os.chdir("/root/fluxgym/outputs")
        print("📁 Listing files in /root/fluxgym/outputs:")
        print(os.listdir("."))

    @modal.method()
    def inspect_output(self, output_name: str):
        output_path = f"/root/fluxgym/outputs/{output_name}"
        if os.path.exists(output_path):
            print(f"📁 Contents of {output_name}:")
            for root, dirs, files in os.walk(output_path):
                level = root.replace(output_path, '').count(os.sep)
                indent = ' ' * 2 * level
                print(f"{indent}{os.path.basename(root)}/")
                subindent = ' ' * 2 * (level + 1)
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    print(f"{subindent}{file} ({file_size} bytes)")
        else:
            print(f"Output {output_name} not found")

if __name__ == "__main__":
    app.serve()