import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from transformers import DistilBertTokenizerFast, DistilBertModel, Trainer, TrainingArguments
import numpy as np
from sklearn.metrics import accuracy_score
from pathlib import Path


base_dir = Path(__file__).parent.parent.parent 
data_dir = base_dir/"data"


output_dir = data_dir / "results"


model_dir = data_dir/"Models"
dir_to_save = model_dir/"multi_task_model_with_emotion"

#train_data_dir = Path(__file__).parent.parent / "Data"
dataset_path = Path(__file__).parent/"Data"/ "router_dataset_with_embeddings.json"



# ======================
# Device setup
# ======================
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("Using device:", device)

# ======================
# Load dataset (with 28-dim emotion vectors)
# ======================
with open(dataset_path, "r") as f:
    dataset = json.load(f)  # List: [text, attention, memory, answer, emotion_vector]

print(f"Loaded {len(dataset)} samples")

# ======================
# Dataset Class
# ======================
class MemoryDataset(Dataset):
    def __init__(self, data, tokenizer, max_len=128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        text, att, mem, ans, emo_vec = self.data[idx]
        enc = self.tokenizer(
            text,
            truncation=True,
            padding="max_length",
            max_length=self.max_len,
            return_tensors="pt"
        )
        return {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "emotion": torch.tensor(emo_vec, dtype=torch.float),  # 28-dim emotion vector
            "labels": {
                "attention": torch.tensor(att, dtype=torch.long),
                "memory": torch.tensor(mem, dtype=torch.long),
                "answer": torch.tensor(ans, dtype=torch.long),
            }
        }

# ======================
# Multi-task Model (with emotion input)
# ======================
class MultiTaskClassifier(nn.Module):
    def __init__(self, model_name="distilbert-base-uncased", emo_dim=28, emo_proj_dim=32):
        super(MultiTaskClassifier, self).__init__()
        self.encoder = DistilBertModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size

        # Project emotion vector
        self.emotion_proj = nn.Linear(emo_dim, emo_proj_dim)
        self.emotion_dropout = nn.Dropout(0.1)       # dropout layer
        self.emotion_layernorm = nn.LayerNorm(emo_proj_dim)  # layernorm layer
        
        
        # Heads (taking BERT + emotion)
        combined_size = hidden_size + emo_proj_dim
        self.attention_head = nn.Linear(combined_size, 3)
        self.memory_head = nn.Linear(combined_size, 3)
        self.answer_head = nn.Linear(combined_size, 3)

    def forward(self, input_ids, attention_mask, emotion=None, labels=None):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]  # [CLS] token

        # Process emotion vector
        if emotion is not None:
            #emo_emb = F.relu(self.emotion_proj(emotion))
            emo_emb = F.gelu(self.emotion_proj(emotion))
            emo_emb = self.emotion_layernorm(emo_emb)
            emo_emb = self.emotion_dropout(emo_emb)
            combined = torch.cat([pooled_output, emo_emb], dim=1)
        else:
            combined = pooled_output

        logits_attention = self.attention_head(combined)
        logits_memory = self.memory_head(combined)
        logits_answer = self.answer_head(combined)

        loss = None
        if labels is not None:
            loss_fct = nn.CrossEntropyLoss()
            loss_attention = loss_fct(logits_attention, labels["attention"])
            loss_memory = loss_fct(logits_memory, labels["memory"])
            loss_answer = loss_fct(logits_answer, labels["answer"])
            #loss = (loss_attention + loss_memory + loss_answer) / 3
            loss = 0.2*loss_attention + 0.3*loss_memory + 0.5*loss_answer

            #loss = 0.3*loss_attention + 0.3*loss_memory + 0.4*loss_answer

        return {"loss": loss, "logits": (logits_attention, logits_memory, logits_answer)}

# ======================
# Data Collator
# ======================
def collate_fn(batch):
    input_ids = torch.stack([item["input_ids"] for item in batch])
    attention_mask = torch.stack([item["attention_mask"] for item in batch])
    emotion = torch.stack([item["emotion"] for item in batch])
    labels = {
        "attention": torch.stack([item["labels"]["attention"] for item in batch]),
        "memory": torch.stack([item["labels"]["memory"] for item in batch]),
        "answer": torch.stack([item["labels"]["answer"] for item in batch]),
    }
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "emotion": emotion,
        "labels": labels
    }

# ======================
# Trainer Wrapper
# ======================
class MultiTaskTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs, labels=labels)
        loss = outputs["loss"]
        return (loss, outputs) if return_outputs else loss

# ======================
# Metrics
# ======================
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    logits_attention, logits_memory, logits_answer = logits
    labels_attention, labels_memory, labels_answer = labels

    preds_attention = np.argmax(logits_attention, axis=1)
    preds_memory = np.argmax(logits_memory, axis=1)
    preds_answer = np.argmax(logits_answer, axis=1)

    return {
        "accuracy_attention": accuracy_score(labels_attention, preds_attention),
        "accuracy_memory": accuracy_score(labels_memory, preds_memory),
        "accuracy_answer": accuracy_score(labels_answer, preds_answer),
    }

# ======================
# Main Training
# ======================

# ======================
# Main Training (with gradient clipping + LR adjustment)
# ======================
if __name__ == "__main__":
    tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")

    split_idx = int(0.96 * len(dataset))
    train_data, test_data = dataset , dataset[split_idx:]

    train_dataset = MemoryDataset(train_data, tokenizer)
    test_dataset = MemoryDataset(test_data, tokenizer)
    training_args = TrainingArguments(
        output_dir=output_dir,
        save_strategy="epoch",
        learning_rate=4e-5,  # slightly lower initial LR for stable training
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=5,
        weight_decay=0.01,
        warmup_ratio=0.8,
        logging_dir="./logs",
        logging_steps=50,
        save_total_limit=2,
        report_to="none",
    )

    model = MultiTaskClassifier().to(device)

    trainer = MultiTaskTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        data_collator=collate_fn,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    # HuggingFace Trainer automatically applies gradient clipping if max_grad_norm > 0
    trainer.train()

    # ======================
    # Save model
    # ======================
    # Path where you want to save the model
    save_dir = dir_to_save  # relative from Tran_Test/neural
    #os.makedirs(save_dir, exist_ok=True)

    # After training
    trainer.save_model(save_dir)
    tokenizer.save_pretrained(save_dir)