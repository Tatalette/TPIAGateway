# ai/train.py
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq,
)
from datasets import Dataset
from ai.data_loader import load_aceob_data, prepare_code_pairs

# Configuration
MODEL_NAME = "/home/Archene/Dev/models/codet5-small"  # chemin local   # Changé
OUTPUT_DIR = "./models/codebert-optimizer"
BATCH_SIZE = 4
EPOCHS = 3
MAX_LENGTH = 512
SAMPLE_SIZE = 200

def tokenize_function(examples, tokenizer):
    inputs = tokenizer(
        examples["source"],
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH,
        return_tensors=None
    )
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            examples["target"],
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors=None
        )
    inputs["labels"] = labels["input_ids"]
    return inputs

def main():
    # Charger les données
    print("Chargement des données...")
    data = load_aceob_data(split="train", sample_size=SAMPLE_SIZE)  
    sources, targets = prepare_code_pairs(data)
    dataset = Dataset.from_dict({"source": sources, "target": targets})
    dataset = dataset.train_test_split(test_size=0.1)
    train_dataset = dataset["train"]
    eval_dataset = dataset["test"]
    print(f"Train: {len(train_dataset)} exemples, Eval: {len(eval_dataset)}")

    # Charger tokenizer et modèle
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    # Tokenisation
    tokenized_train = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=train_dataset.column_names
    )
    tokenized_eval = eval_dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=eval_dataset.column_names
    )

    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # Arguments d'entraînement
    training_args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=5e-5,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        weight_decay=0.01,
        num_train_epochs=EPOCHS,
        predict_with_generate=True,
        logging_dir="./logs",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_eval,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )

    # Entraînement
    trainer.train()

    # Sauvegarde finale
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

if __name__ == "__main__":
    main()