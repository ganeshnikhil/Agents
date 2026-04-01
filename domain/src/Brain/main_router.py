
from transformers import pipeline, DistilBertTokenizerFast, DistilBertModel
import torch
import torch.nn as nn
import torch.nn.functional as F
import logging
from safetensors.torch import load_file



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMOTION_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval",
    "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief",
    "joy", "love", "nervousness", "optimism", "pride", "realization",
    "relief", "remorse", "sadness", "surprise", "neutral"
]

ATTENTION_LABELS = ["memory_in", "memory_out", "cur"]
MEMORY_LABELS = ["STM", "LTM", "none"]
ANSWER_LABELS = ["single", "multiple", "none"]



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


class Hippocampus:
    def __init__(self, Model_path , Bert_model_name="distilbert-base-uncased",sentiment_model_name="SamLowe/roberta-base-go_emotions"):
        self.Model_path = Model_path
        self.Bert_model_name = Bert_model_name
        self.sentiment_model_name = sentiment_model_name
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.emotion_vector = None 
        self.tokenizer = DistilBertTokenizerFast.from_pretrained(self.Bert_model_name)
        self.model = MultiTaskClassifier().to(self.device)
        state_dict = load_file(f"{self.Model_path}/model.safetensors")
        self.model.load_state_dict(state_dict)
        self.model.eval()


    def probablity_emotion_vector(self, text):
        classifier = pipeline(task="text-classification",model=self.sentiment_model_name, top_k=None)
        outputs = classifier(text)
        self.emotion_vector = outputs[0]
        prob_vector = [
            next((item["score"] for item in outputs[0] if item["label"] == emo), 0.0)
            for emo in EMOTION_LABELS
        ]
        return prob_vector
    
    
    def get_emotion_vector(self, text):
        if self.emotion_vector:
            emotion_dict = {item["label"] : item["score"] for item in self.emotion_vector}
            return emotion_dict
        
        classifier = pipeline(task="text-classification",model=self.sentiment_model_name, top_k=None)
        outputs = classifier(text)
        emotion_dict = {item["label"] : item["score"] for item in outputs[0]}
        return emotion_dict
    
    def route_memory(self, text):
        emotion_vector = self.probablity_emotion_vector(text)
        inputs = self.tokenizer(
            text, truncation=True, padding="max_length", max_length=128, return_tensors="pt"
        ).to(self.device)

        emotion_tensor = torch.tensor([emotion_vector], dtype=torch.float).to(self.device)

        with torch.no_grad():
            outputs = self.model(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                emotion=emotion_tensor
            )

        logits_attention, logits_memory, logits_answer = outputs["logits"]
        
        print(logits_attention)
        print(torch.argmax(logits_attention, dim=1).item())
        attention_pred = ATTENTION_LABELS[torch.argmax(logits_attention, dim=1).item()]
        memory_pred = MEMORY_LABELS[torch.argmax(logits_memory, dim=1).item()]
        answer_pred = ANSWER_LABELS[torch.argmax(logits_answer, dim=1).item()]

        return attention_pred, memory_pred, answer_pred


if __name__ == "__main__":
    #/Users/ganeshnikhil/Memory-Twin/data/Models
    hipp = Hippocampus(Model_path="/Users/ganeshnikhil/Memory-Twin/data/Models/multi_task_model_with_emotion")
    att, mem, ans = hipp.route_memory("I want to fuck you to night")
    print(att, mem, ans) 
