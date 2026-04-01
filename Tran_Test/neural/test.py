# import json
# import torch
# from transformers import DistilBertTokenizerFast
# from neural import MultiTaskClassifier, MemoryDataset  # your model & dataset classes
# from sklearn.metrics import accuracy_score
# from safetensors.torch import load_file

# # ------------------------
# # Device
# # ------------------------
# device = "mps" if torch.backends.mps.is_available() else "cpu"
# print("Using device:", device)

# # ------------------------
# # Load dataset
# # ------------------------
# with open("labeled_dataset.json", "r") as f:
#     dataset = json.load(f)

# split_idx = int(0.9 * len(dataset))
# test_data = dataset[split_idx:]

# # ------------------------
# # Load tokenizer
# # ------------------------
# tokenizer = DistilBertTokenizerFast.from_pretrained("./multi_task_model")

# # ------------------------
# # Prepare test dataset
# # ------------------------
# test_dataset = MemoryDataset(test_data, tokenizer)

# # ------------------------
# # Load model
# # ------------------------
# model = MultiTaskClassifier()
# model.load_state_dict(torch.load("./multi_task_model/model.safetensors", map_location=device))
# model.to(device)
# model.eval()

# # ------------------------
# # Evaluation
# # ------------------------
# all_attention_preds, all_memory_preds, all_answer_preds = [], [], []
# all_attention_labels, all_memory_labels, all_answer_labels = [], [], []

# for sample in test_dataset:
#     input_ids = sample["input_ids"].unsqueeze(0).to(device)
#     attention_mask = sample["attention_mask"].unsqueeze(0).to(device)

#     with torch.no_grad():
#         outputs = model(input_ids=input_ids, attention_mask=attention_mask)

#     logits_attention, logits_memory, logits_answer = outputs["logits"]

#     all_attention_preds.append(torch.argmax(logits_attention, dim=1).item())
#     all_memory_preds.append(torch.argmax(logits_memory, dim=1).item())
#     all_answer_preds.append(torch.argmax(logits_answer, dim=1).item())

#     all_attention_labels.append(sample["labels"]["attention"].item())
#     all_memory_labels.append(sample["labels"]["memory"].item())
#     all_answer_labels.append(sample["labels"]["answer"].item())

# # ------------------------
# # Print accuracies
# # ------------------------
# print("Attention accuracy:", accuracy_score(all_attention_labels, all_attention_preds))
# print("Memory accuracy:", accuracy_score(all_memory_labels, all_memory_preds))
# print("Answer accuracy:", accuracy_score(all_answer_labels, all_answer_preds))


# attention_labels = ["memory_in", "memory_out", "cur"] (0, 1, 2) 
# memory_labels = ["STM", "LTM", "none"] (0, 1, 2) 
# answer_labels = ["single", "multiple", "none"] (0, 1, 2) this is what it look like

# import json
# import torch
# import torch.nn as nn
# from torch.utils.data import Dataset
# from transformers import DistilBertTokenizerFast
# import numpy as np
# from sklearn.metrics import accuracy_score
# from safetensors.torch import load_file
# from neural import MultiTaskClassifier  # your model class

# # ======================
# # Device setup
# # ======================
# device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
# print("Using device:", device)

# # ======================
# # Load dataset
# # ======================
# with open("labeled_dataset.json", "r") as f:
#     dataset = json.load(f)

# split_idx = int(0.9 * len(dataset))
# test_data = dataset[split_idx:]

# # ======================
# # Dataset class
# # ======================
# class MemoryDataset(Dataset):
#     def __init__(self, data, tokenizer, max_len=128):
#         self.data = data
#         self.tokenizer = tokenizer
#         self.max_len = max_len

#     def __len__(self):
#         return len(self.data)

#     def __getitem__(self, idx):
#         text, att, mem, ans = self.data[idx]
#         enc = self.tokenizer(
#             text,
#             truncation=True,
#             padding="max_length",
#             max_length=self.max_len,
#             return_tensors="pt"
#         )
#         return {
#             "input_ids": enc["input_ids"].squeeze(0),
#             "attention_mask": enc["attention_mask"].squeeze(0),
#             "labels": {
#                 "attention": torch.tensor(att, dtype=torch.long),
#                 "memory": torch.tensor(mem, dtype=torch.long),
#                 "answer": torch.tensor(ans, dtype=torch.long),
#             }
#         }

# # ======================
# # Tokenizer
# # ======================
# tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
# test_dataset = MemoryDataset(test_data, tokenizer)

# # ======================
# # Load model
# # ======================
# model = MultiTaskClassifier().to(device)
# state_dict = load_file("./multi_task_model/model.safetensors")
# model.load_state_dict(state_dict)
# model.eval()

# # ======================
# # Evaluation
# # ======================
# all_attention_preds = []
# all_memory_preds = []
# all_answer_preds = []

# all_attention_labels = []
# all_memory_labels = []
# all_answer_labels = []

# for sample in test_dataset:
#     input_ids = sample["input_ids"].unsqueeze(0).to(device)
#     attention_mask = sample["attention_mask"].unsqueeze(0).to(device)
#     labels = sample["labels"]

#     with torch.no_grad():
#         outputs = model(input_ids=input_ids, attention_mask=attention_mask)

#     logits_attention, logits_memory, logits_answer = outputs["logits"]

#     all_attention_preds.append(torch.argmax(logits_attention, dim=1).item())
#     all_memory_preds.append(torch.argmax(logits_memory, dim=1).item())
#     all_answer_preds.append(torch.argmax(logits_answer, dim=1).item())

#     all_attention_labels.append(labels["attention"].item())
#     all_memory_labels.append(labels["memory"].item())
#     all_answer_labels.append(labels["answer"].item())

# print("Attention accuracy:", accuracy_score(all_attention_labels, all_attention_preds))
# print("Memory accuracy:", accuracy_score(all_memory_labels, all_memory_preds))
# print("Answer accuracy:", accuracy_score(all_answer_labels, all_answer_preds))


import json
import torch
from torch.utils.data import Dataset
from transformers import DistilBertTokenizerFast
from sklearn.metrics import accuracy_score
from safetensors.torch import load_file
from train import MultiTaskClassifier  # your updated model class with emotion
from pathlib import Path


base_dir = Path(__file__).parent.parent.parent 
data_dir = base_dir/"data"


output_dir = data_dir / "results"


model_dir = data_dir/"Models"
model_saved = model_dir/"multi_task_model_with_emotion"

#train_data_dir = Path(__file__).parent.parent / "Data"
dataset_path = Path(__file__).parent/"Data"/ "router_dataset_with_embeddings.json"


# ======================
# Device setup
# ======================
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("Using device:", device)

# ======================
# Load dataset with emotion embeddings
# Each sample: [text, attention, memory, answer, emotion_vector]
# ======================
with open(dataset_path, "r") as f:
    dataset = json.load(f)

split_idx = int(0.9 * len(dataset))
test_data = dataset[split_idx:]

# ======================
# Dataset class
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
            "emotion": torch.tensor(emo_vec, dtype=torch.float),
            "labels": {
                "attention": torch.tensor(att, dtype=torch.long),
                "memory": torch.tensor(mem, dtype=torch.long),
                "answer": torch.tensor(ans, dtype=torch.long),
            }
        }

# ======================
# Tokenizer & Dataset
# ======================
tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
test_dataset = MemoryDataset(test_data, tokenizer)

# ======================
# Load model
# ======================
model = MultiTaskClassifier().to(device)
state_dict = load_file(f"{model_saved}/model.safetensors")
model.load_state_dict(state_dict)
model.eval()

# ======================
# Evaluation
# ======================
all_attention_preds = []
all_memory_preds = []
all_answer_preds = []

all_attention_labels = []
all_memory_labels = []
all_answer_labels = []

for sample in test_dataset:
    input_ids = sample["input_ids"].unsqueeze(0).to(device)
    attention_mask = sample["attention_mask"].unsqueeze(0).to(device)
    emotion = sample["emotion"].unsqueeze(0).to(device)  # new
    labels = sample["labels"]

    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, emotion=emotion)

    logits_attention, logits_memory, logits_answer = outputs["logits"]

    all_attention_preds.append(torch.argmax(logits_attention, dim=1).item())
    all_memory_preds.append(torch.argmax(logits_memory, dim=1).item())
    all_answer_preds.append(torch.argmax(logits_answer, dim=1).item())

    all_attention_labels.append(labels["attention"].item())
    all_memory_labels.append(labels["memory"].item())
    all_answer_labels.append(labels["answer"].item())

print("Attention accuracy:", accuracy_score(all_attention_labels, all_attention_preds))
print("Memory accuracy:", accuracy_score(all_memory_labels, all_memory_preds))
print("Answer accuracy:", accuracy_score(all_answer_labels, all_answer_preds))
