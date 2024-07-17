export HF_HOME=/nas/ucb/constantinweisser/cache/
perspective="3_3"
accelerate launch --config_file accelerate_config.yaml src/train_hh_pm/train_pm_personalization.py  \
    --output_dir="models/llama_${perspective}_trainonperso_grm_1epochs3" \
    --perspective=${perspective} \
    --model_name=Ray2333/GRM-llama3-8B-sftreg \
    --tokenizer_name=sfairXC/FsfairX-LLaMA3-RM-v0.1   \
    --per_device_train_batch_size=32 \
    --per_device_eval_batch_size=16 \
    --num_train_epochs=1 \
    --gradient_accumulation_steps=1 \
    --gradient_checkpointing=True \
    --learning_rate=5e-5 \
    --report_to="none" \
    --remove_unused_columns=False \
    --optim="adamw_torch" \
    --logging_steps=1 \
    --eval_strategy="steps" \
    --eval_steps=0.2 \
    --max_length=2048 \
    --LoRA=True \
    --LoRA_r=8 \
    --LoRA_alpha=32 \
    --LoRA_dropout=0.1 \
    --lr_scheduler_type="cosine"