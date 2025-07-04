accelerate launch \
  --mixed_precision bf16 \
  --num_cpu_threads_per_process 1 \
  sd-scripts/flux_train_network.py \
  --pretrained_model_name_or_path "/root/fluxgym/models/unet/flux1-dev.sft" \
  --clip_l "/root/fluxgym/models/clip/clip_l.safetensors" \
  --t5xxl "/root/fluxgym/models/clip/t5xxl_fp16.safetensors" \
  --ae "/root/fluxgym/models/vae/ae.sft" \
  --cache_latents_to_disk \
  --save_model_as safetensors \
  --sdpa --persistent_data_loader_workers \
  --max_data_loader_n_workers 2 \
  --seed 42 \
  --gradient_checkpointing \
  --mixed_precision bf16 \
  --save_precision bf16 \
  --network_module networks.lora_flux \
  --network_dim 4 \
  --optimizer_type adafactor \
  --optimizer_args "relative_step=False" "scale_parameter=False" "warmup_init=False" \
  --lr_scheduler constant_with_warmup \
  --max_grad_norm 0.0 \--sample_prompts="/root/fluxgym/outputs/abercrombiestylelora/sample_prompts.txt" --sample_every_n_steps="300" \
  --learning_rate 8e-4 \
  --cache_text_encoder_outputs \
  --cache_text_encoder_outputs_to_disk \
  --fp8_base \
  --highvram \
  --max_train_epochs 10 \
  --save_every_n_epochs 2 \
  --dataset_config "/root/fluxgym/outputs/abercrombiestylelora/dataset.toml" \
  --output_dir "/root/fluxgym/outputs/abercrombiestylelora" \
  --output_name abercrombiestylelora \
  --timestep_sampling shift \
  --discrete_flow_shift 3.1582 \
  --model_prediction_type raw \
  --guidance_scale 1 \
  --loss_type l2 \