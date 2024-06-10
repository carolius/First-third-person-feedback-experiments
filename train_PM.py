import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
from trl import RewardTrainer
from peft import LoraConfig, get_peft_model
from datasets import load_dataset, Dataset

def main():
    PM_path = "../MORLAIF/data/PM_LoRAs/gemma-2b_CAI/final"
    save_path = "PMs/gemma-2b_CAI/"
    dataset_path = "datasets/sycophancy_fact_fix.jsonl"
    num_proc = 4
    dataset = load_dataset('json', data_files=dataset_path)
    train_dataset = Dataset.from_dict(dataset['train'][:300])
    test_dataset = Dataset.from_dict(dataset['train'][300:])

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(PM_path)
    preference_model = AutoModelForSequenceClassification.from_pretrained(PM_path, num_labels=1)
    
    # Load and configure LoRA
    lora_config = LoraConfig.from_pretrained(PM_path)
    preference_model = get_peft_model(preference_model, lora_config)

    def preprocess_func(examples):
        question = examples['prompt'] + " " + examples['question']
        if examples["high_reward_answer"] == "A":
            answer_chosen = examples['answerA']
            answer_rejected = examples['answerB']
        else:
            answer_chosen = examples['answerB']
            answer_rejected = examples['answerA']
        
        tokenized_chosen = tokenizer("Human: " + question + "\nAssistant: " + answer_chosen, max_length=512, truncation=True)
        tokenized_rejected = tokenizer("Human: " + question + "\nAssistant: " + answer_rejected, max_length=512, truncation=True)

        d = {'input_ids_chosen': tokenized_chosen['input_ids'],
             'attention_mask_chosen': tokenized_chosen['attention_mask'],
             'input_ids_rejected': tokenized_rejected['input_ids'],
             'attention_mask_rejected': tokenized_rejected['attention_mask']}
        return d

    train_dataset = train_dataset.map(preprocess_func, batched=False, num_proc=num_proc)
    test_dataset = test_dataset.map(preprocess_func, batched=False, num_proc=num_proc)
    print(train_dataset)

    training_args = TrainingArguments(
        output_dir=save_path,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        num_train_epochs=3,
        weight_decay=0.01,
        bf16=True, 
    )

    trainer = RewardTrainer(
        model=preference_model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=tokenizer,
    )
    print("Training PM")
    trainer.train()
    
    # Save the entire model, including the adapter
    trainer.save_model(save_path)
    tokenizer.save_pretrained(save_path)

if __name__ == "__main__":
    main()
