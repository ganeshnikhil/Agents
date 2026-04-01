
from transformers import pipeline
import json
from pathlib import Path

# ---------------------
# Paths
# ---------------------
data_dir = Path(__file__).parent.parent / "Data"
input_file = data_dir / "labeled_dataset.json"
output_file = data_dir / "router_dataset_with_embeddings.json"

# ---------------------
# Emotion labels
# ---------------------
emotion_labels = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval",
    "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief",
    "joy", "love", "nervousness", "optimism", "pride", "realization",
    "relief", "remorse", "sadness", "surprise", "neutral"
]

# ---------------------
# Load classifier
# ---------------------
classifier = pipeline(
    task="text-classification", 
    model="SamLowe/roberta-base-go_emotions", 
    top_k=None
)

# ---------------------
# Load dataset
# ---------------------
with open(input_file, "r", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"Loaded {len(dataset)} samples")

# ---------------------
# Compute emotion embeddings
# ---------------------
for data in dataset:
    text = data[0]  # assuming dataset is list of lists
    model_outputs = classifier(text)  # returns list[list[dict]]
    
    prob_vector = [0.0] * len(emotion_labels)
    
    for item in model_outputs[0]:   # <-- fix here
        if item["label"] in emotion_labels:
            idx = emotion_labels.index(item["label"])
            prob_vector[idx] = item["score"]
    
    data.append(prob_vector)


# ---------------------
# Save updated dataset
# ---------------------
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=4)

print(f"Saved dataset with emotion embeddings to '{output_file}'")

