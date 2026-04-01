import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

# =========================================================
# 1. DEVICE SETUP (APPLE SILICON SAFE)
# =========================================================

if torch.backends.mps.is_available():
    ROUTER_DEVICE = "mps"
else:
    ROUTER_DEVICE = "cpu"

ENCODER_DEVICE = "cpu"   # sentence-transformers must stay on CPU

print(f"Router device: {ROUTER_DEVICE}")
print(f"Encoder device: {ENCODER_DEVICE}")

# =========================================================
# 2. CONFIG
# =========================================================

EMBED_DIM = 384              # all-MiniLM-L6-v2
NUM_AGENTS = 4
BATCH_SIZE = 8
EPOCHS = 15
LEARNING_RATE = 1e-3

torch.manual_seed(42)

# =========================================================
# 3. AGENT DEFINITIONS
# =========================================================
"""
Agent IDs:
0 → Memory Agent
1 → Search Agent
2 → Reasoning Agent
3 → Code Agent
"""

AGENT_NAMES = {
    0: "memory_agent",
    1: "search_agent",
    2: "reasoning_agent",
    3: "code_agent"
}

# =========================================================
# 4. LARGE LABELED DATASET
# =========================================================

LABELED_DATA: List[Tuple[str, int]] = [

    # ================= MEMORY AGENT =================
    ("remember my name is ganesh", 0),
    ("store this information for later", 0),
    ("save my preferences", 0),
    ("what did i tell you yesterday", 0),
    ("recall my previous conversation", 0),
    ("keep note of my birthday", 0),
    ("remember that i like python", 0),
    ("add this to my memory", 0),
    ("what do you remember about me", 0),
    ("retrieve my past details", 0),

    # ================= SEARCH AGENT =================
    ("search latest ai research papers", 1),
    ("find news about apple stock", 1),
    ("look up information about transformers", 1),
    ("search the web for python tutorials", 1),
    ("find current weather in delhi", 1),
    ("search recent llm agent papers", 1),
    ("get me latest tech news", 1),
    ("find documentation for fastapi", 1),
    ("search stackoverflow for this error", 1),
    ("find blogs on mixture of experts", 1),

    # ================= REASONING AGENT =================
    ("explain backpropagation simply", 2),
    ("why do transformers use attention", 2),
    ("what is the difference between cnn and rnn", 2),
    ("explain gradient descent step by step", 2),
    ("how does reinforcement learning work", 2),
    ("why does overfitting happen", 2),
    ("explain bias variance tradeoff", 2),
    ("how does batch normalization help", 2),
    ("what happens during backpropagation", 2),
    ("explain mixture of experts routing", 2),

    # ================= CODE AGENT =================
    ("write python code for binary search", 3),
    ("fix this bug in my c++ code", 3),
    ("implement linked list in python", 3),
    ("write sql query to find duplicates", 3),
    ("create fastapi backend example", 3),
    ("write a pytorch training loop", 3),
    ("convert this code to javascript", 3),
    ("debug this segmentation fault", 3),
    ("write dockerfile for python app", 3),
    ("implement moe router in pytorch", 3),
]

# =========================================================
# 5. DATASET
# =========================================================

class RouterDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

# =========================================================
# 6. SENTENCE TRANSFORMER ENCODER (FROZEN)
# =========================================================

class SentenceEncoder(nn.Module):
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        super().__init__()
        self.model = SentenceTransformer(model_name, device=ENCODER_DEVICE)

    def forward(self, sentences: List[str]):
        embeddings = self.model.encode(
            sentences,
            convert_to_tensor=True,
            device=ENCODER_DEVICE,
            normalize_embeddings=True
        )
        return embeddings

# =========================================================
# 7. MoE AGENT ROUTER
# =========================================================

class MoERouter(nn.Module):
    def __init__(self, embed_dim: int, num_agents: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embed_dim, 256),
            nn.ReLU(),
            nn.Linear(256, num_agents)
        )

    def forward(self, x):
        return self.net(x)

# =========================================================
# 8. INITIALIZE MODELS
# =========================================================

encoder = SentenceEncoder()
router = MoERouter(EMBED_DIM, NUM_AGENTS).to(ROUTER_DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(router.parameters(), lr=LEARNING_RATE)

dataset = RouterDataset(LABELED_DATA)
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# =========================================================
# 9. TRAINING LOOP (FINAL, WARNING-FREE)
# =========================================================

print("\n--- TRAINING STARTED ---\n")

for epoch in range(EPOCHS):
    total_loss = 0.0

    for queries, agent_labels in loader:
        agent_labels = agent_labels.to(ROUTER_DEVICE)

        with torch.no_grad():
            embeddings = encoder(list(queries))

        embeddings = embeddings.clone().detach().to(ROUTER_DEVICE)

        logits = router(embeddings)
        loss = criterion(logits, agent_labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch [{epoch+1}/{EPOCHS}] | Loss: {total_loss:.4f}")

# =========================================================
# 10. INFERENCE FUNCTION
# =========================================================

def route_query(query: str, temperature: float = 1.0):
    router.eval()

    with torch.no_grad():
        embedding = encoder([query])
        embedding = embedding.clone().detach().to(ROUTER_DEVICE)

        logits = router(embedding) / temperature
        probs = torch.softmax(logits, dim=-1)

        agent_id = torch.argmax(probs, dim=-1).item()
        confidence = probs[0, agent_id].item()

    return AGENT_NAMES[agent_id], confidence

# =========================================================
# 11. TESTING
# =========================================================

print("\n--- ROUTER TEST ---\n")

test_queries = [
    "remember that i use macbook",
    "find latest research on moe models",
    "explain how attention mechanism works",
    "write python code for quicksort",
]

for q in test_queries:
    agent, conf = route_query(q)
    print(f"Query: {q}")
    print(f"→ Routed to: {agent} | confidence={conf:.2f}\n")
