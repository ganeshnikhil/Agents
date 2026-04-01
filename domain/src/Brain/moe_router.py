import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
import random

# =====================
# DEVICE SETUP
# =====================
ROUTER_DEVICE = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
ENCODER_DEVICE = "cpu"

print(f"Router device: {ROUTER_DEVICE}")
print(f"Encoder device: {ENCODER_DEVICE}")

# =====================
# LEVEL 1: MODES
# =====================
MODES = ["stm", "ltm", "tool", "think"]
MODE2ID = {m: i for i, m in enumerate(MODES)}
ID2MODE = {i: m for m, i in MODE2ID.items()}

# =====================
# LEVEL 2: SUB-AGENTS / OPERATIONS
# =====================
SUB_AGENTS = {
    "stm": ["memory_in", "memory_out"],
    "ltm": ["memory_in", "memory_out"],
    "tool": ["code_agent", "search_agent"],
    "think": ["simple_reason", "reason_with_tools", "reason_with_stm", "reason_with_ltm"]
}

SUB2ID = {mode: {sub: i for i, sub in enumerate(SUB_AGENTS[mode])} for mode in SUB_AGENTS}
ID2SUB = {mode: {i: sub for sub, i in SUB2ID[mode].items()} for mode in SUB_AGENTS}

# =====================
# DATASET
# =====================
class HierarchicalDataset(Dataset):
    def __init__(self, samples):
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]

# =====================
# ROUTERS
# =====================
class ModeRouter(nn.Module):
    def __init__(self, embed_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.ReLU(),
            nn.Linear(128, len(MODES))
        )

    def forward(self, x):
        return self.net(x)

class SubRouter(nn.Module):
    def __init__(self, embed_dim, num_ops):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.ReLU(),
            nn.Linear(128, num_ops)
        )

    def forward(self, x):
        return self.net(x)

# =====================
# LARGE LABELED DATASET
# =====================
def build_large_dataset():
    data = []

    # STM → memory_in / memory_out
    stm_in = [
        "remember my name", "store this info", "save my preferences", "remember my birthday",
        "keep my login settings", "remember my favorite language", "store session tokens",
        "save my project progress", "remember today's date", "store my to-do list"
    ]
    stm_out = [
        "fetch my saved settings", "get my last saved preferences", "read my stored data",
        "retrieve my session tokens", "load my project progress", "read my to-do list",
        "fetch birthday info", "get favorite language", "load login settings", "read stored preferences"
    ]

    for q in stm_in:
        data.append((q, MODE2ID["stm"], SUB2ID["stm"]["memory_in"]))
    for q in stm_out:
        data.append((q, MODE2ID["stm"], SUB2ID["stm"]["memory_out"]))

    # LTM → memory_in / memory_out
    ltm_in = [
        "save research article", "store vector of document", "add knowledge to memory",
        "record new information", "store embeddings of papers", "archive research data",
        "add document to vector db", "save long-term data", "store ai research info", "add learning material"
    ]
    ltm_out = [
        "find latest research", "retrieve vector embeddings", "get previous documents",
        "search knowledge base", "fetch stored papers", "retrieve long-term memory",
        "get archived research", "find stored vectors", "retrieve ai knowledge", "search learning materials"
    ]
    for q in ltm_in:
        data.append((q, MODE2ID["ltm"], SUB2ID["ltm"]["memory_in"]))
    for q in ltm_out:
        data.append((q, MODE2ID["ltm"], SUB2ID["ltm"]["memory_out"]))

    # Tool → code_agent / search_agent
    code_q = [
        "write python quicksort", "implement binary search", "write a neural network from scratch",
        "code linked list in java", "write fastapi backend", "implement sorting algorithm",
        "build a chat application", "code binary tree in c++", "write flask api example", "implement graph algorithm"
    ]
    search_q = [
        "search latest ai news", "search for sentence transformer repo", "find best laptops in 2025",
        "look up transformer architecture", "search github for projects", "find python tutorials",
        "search for reinforcement learning papers", "find docker tutorial", "search ML research articles",
        "look up cloud GPU benchmarks"
    ]
    for q in code_q:
        data.append((q, MODE2ID["tool"], SUB2ID["tool"]["code_agent"]))
    for q in search_q:
        data.append((q, MODE2ID["tool"], SUB2ID["tool"]["search_agent"]))

    # Think → reasoning
    simple_reason_q = [
        "explain attention mechanism", "why does overfitting happen", "how does backpropagation work",
        "explain bias variance tradeoff", "why transformers outperform rnn", "why vanishing gradient occurs",
        "explain supervised vs unsupervised learning", "how does gradient descent converge",
        "why moe models scale well", "explain self-attention"
    ]
    reason_tools_q = [
        "reason using code tools", "analyze using search engine", "solve problem with code execution",
        "plan using helper functions", "debug using tool chain", "perform calculation using python",
        "automate task using scripts", "predict using simulation tools", "generate result using utilities",
        "use tools to infer answer"
    ]
    reason_stm_q = [
        "reason using stm memory", "analyze using stored preferences", "solve using session data",
        "derive answer using user memory", "compute using remembered info", "infer using recent memory",
        "plan using previous stored info", "analyze task using STM", "use memory_in for reasoning",
        "reference saved user context"
    ]
    reason_ltm_q = [
        "reason using ltm memory", "analyze using long-term knowledge", "solve using vector db",
        "infer using previous research", "compute using archived data", "derive solution using LTM",
        "use past learning for reasoning", "reference LTM knowledge base", "search historical data for inference",
        "use embeddings for reasoning"
    ]
    for q in simple_reason_q:
        data.append((q, MODE2ID["think"], SUB2ID["think"]["simple_reason"]))
    for q in reason_tools_q:
        data.append((q, MODE2ID["think"], SUB2ID["think"]["reason_with_tools"]))
    for q in reason_stm_q:
        data.append((q, MODE2ID["think"], SUB2ID["think"]["reason_with_stm"]))
    for q in reason_ltm_q:
        data.append((q, MODE2ID["think"], SUB2ID["think"]["reason_with_ltm"]))

    random.shuffle(data)
    return data

# =====================
# ENCODER
# =====================
encoder = SentenceTransformer("all-MiniLM-L6-v2", device=ENCODER_DEVICE)
EMBED_DIM = encoder.get_sentence_embedding_dimension()

# =====================
# ROUTERS
# =====================
mode_router = ModeRouter(EMBED_DIM).to(ROUTER_DEVICE)
stm_router = SubRouter(EMBED_DIM, len(SUB_AGENTS["stm"])).to(ROUTER_DEVICE)
ltm_router = SubRouter(EMBED_DIM, len(SUB_AGENTS["ltm"])).to(ROUTER_DEVICE)
tool_router = SubRouter(EMBED_DIM, len(SUB_AGENTS["tool"])).to(ROUTER_DEVICE)
think_router = SubRouter(EMBED_DIM, len(SUB_AGENTS["think"])).to(ROUTER_DEVICE)

# =====================
# TRAINING SETUP
# =====================
dataset = HierarchicalDataset(build_large_dataset())
loader = DataLoader(dataset, batch_size=8, shuffle=True)

mode_optimizer = optim.Adam(mode_router.parameters(), lr=1e-3)
stm_optimizer = optim.Adam(stm_router.parameters(), lr=1e-3)
ltm_optimizer = optim.Adam(ltm_router.parameters(), lr=1e-3)
tool_optimizer = optim.Adam(tool_router.parameters(), lr=1e-3)
think_optimizer = optim.Adam(think_router.parameters(), lr=1e-3)

criterion = nn.CrossEntropyLoss()

# =====================
# TRAINING LOOP
# =====================
print("\n--- TRAINING STARTED ---\n")
EPOCHS = 15
for epoch in range(EPOCHS):
    total_loss = 0.0
    for queries, mode_labels, sub_labels in loader:
        mode_labels = mode_labels.to(ROUTER_DEVICE)
        sub_labels = sub_labels.to(ROUTER_DEVICE)

        with torch.no_grad():
            embeddings = encoder.encode(list(queries), convert_to_tensor=True, device=ENCODER_DEVICE)
        embeddings = embeddings.detach().to(ROUTER_DEVICE)

        # Level 1: Mode
        mode_logits = mode_router(embeddings)
        mode_loss = criterion(mode_logits, mode_labels)

        # Level 2: Sub-agent router
        sub_loss = 0
        for mode_idx, router, mode_name in [
            (MODE2ID["stm"], stm_router, "stm"),
            (MODE2ID["ltm"], ltm_router, "ltm"),
            (MODE2ID["tool"], tool_router, "tool"),
            (MODE2ID["think"], think_router, "think")
        ]:
            idxs = (mode_labels == mode_idx).nonzero(as_tuple=True)[0]
            if len(idxs) == 0:
                continue
            sub_logits = router(embeddings[idxs])
            sub_loss += criterion(sub_logits, sub_labels[idxs])

        loss = mode_loss + sub_loss

        mode_optimizer.zero_grad()
        stm_optimizer.zero_grad()
        ltm_optimizer.zero_grad()
        tool_optimizer.zero_grad()
        think_optimizer.zero_grad()

        loss.backward()

        mode_optimizer.step()
        stm_optimizer.step()
        ltm_optimizer.step()
        tool_optimizer.step()
        think_optimizer.step()

        total_loss += loss.item()

    print(f"Epoch [{epoch+1}/{EPOCHS}] | Loss: {total_loss:.4f}")

# =====================
# INFERENCE
# =====================
def hierarchical_route(query: str):
    with torch.no_grad():
        emb = encoder.encode(query, convert_to_tensor=True, device=ENCODER_DEVICE).unsqueeze(0)
        emb = emb.to(ROUTER_DEVICE)

        mode_logits = mode_router(emb)
        mode_probs = torch.softmax(mode_logits, dim=-1)
        mode_id = torch.argmax(mode_probs).item()

        if mode_id == MODE2ID["stm"]:
            sub_logits = stm_router(emb)
        elif mode_id == MODE2ID["ltm"]:
            sub_logits = ltm_router(emb)
        elif mode_id == MODE2ID["tool"]:
            sub_logits = tool_router(emb)
        else:
            sub_logits = think_router(emb)

        sub_probs = torch.softmax(sub_logits, dim=-1)
        sub_id = torch.argmax(sub_probs).item()

    return {
        "mode": ID2MODE[mode_id],
        "mode_conf": mode_probs[0, mode_id].item(),
        "sub_agent": ID2SUB[ID2MODE[mode_id]][sub_id],
        "sub_conf": sub_probs[0, sub_id].item()
    }

# =====================
# TEST
# =====================
print("\n--- HIERARCHICAL ROUTER TEST ---\n")
test_queries = [
    "remember my birthday",
    "retrieve vector embeddings",
    "write python quicksort",
    "search latest ai news",
    "reason using stm memory",
    "reason using ltm memory",
    "explain attention mechanism",
    "store vector of document",
    "code linked list in java",
    "reason using tools"
]

for q in test_queries:
    res = hierarchical_route(q)
    print(f"Query: {q}")
    print(f"→ Mode: {res['mode']} | confidence={res['mode_conf']:.2f}")
    print(f"→ Sub-agent/Operation: {res['sub_agent']} | confidence={res['sub_conf']:.2f}\n")


### saving the moe router 
''''
# Save routers
save_path = "./saved_routers.pth"

torch.save({
    "mode_router": mode_router.state_dict(),
    "stm_router": stm_router.state_dict(),
    "ltm_router": ltm_router.state_dict(),
    "tool_router": tool_router.state_dict(),
    "think_router": think_router.state_dict()
}, save_path)

print(f"Routers saved to {save_path}")

'''

### testing the moe route
'''
checkpoint = torch.load("./saved_routers.pth", map_location=ROUTER_DEVICE)

mode_router.load_state_dict(checkpoint["mode_router"])
stm_router.load_state_dict(checkpoint["stm_router"])
ltm_router.load_state_dict(checkpoint["ltm_router"])
tool_router.load_state_dict(checkpoint["tool_router"])
think_router.load_state_dict(checkpoint["think_router"])

mode_router.eval()
stm_router.eval()
ltm_router.eval()
tool_router.eval()
think_router.eval()

print("Routers loaded successfully!")
'''