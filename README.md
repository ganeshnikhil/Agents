# Cognitive Digital Twin

## Abstract

The **Cognitive Digital Twin** is a fully local, privacy-preserving Personal AI Memory system designed to model human-like cognition at an individual level. Unlike conventional digital assistants that only store and retrieve information, this system can **understand context, reason over past experiences, track emotional state, and autonomously act on user intent**.

At its core, the Cognitive Digital Twin combines a **multi-head fine-tuned DistilBERT routing model**, a **dual-memory architecture (Short-Term and Long-Term Memory)**, and an **agentic execution layer** capable of tool use, planning, and code execution. A **26-dimensional emotion vector** augments every interaction, enabling deeper personalization and emotionally aligned memory retrieval. The result is a digital system that behaves less like a chatbot and more like a cognitive companion—capable of remembering, deciding, and acting in a human-like way.

---

## What Problem Does This Solve?

Current digital assistants suffer from three major limitations:

1. **No true memory separation** – short-lived context and long-term facts are often mixed or forgotten.
2. **Lack of agency** – they cannot autonomously plan, use tools, or execute multi-step tasks.
3. **Weak contextual and emotional understanding** – user intent and emotional tone are often ignored.

The Cognitive Digital Twin addresses these gaps by introducing a **single unified routing model** that decides:

* whether to **store**, **retrieve**, or **act** on a query,
* which **memory system** to use (STM or LTM), and
* what **answer format** is required.

This architecture bridges the gap between simple AI automation and true cognitive support.

---

## High-Level Architecture

### Multi-head attention Router (current implimentation).
```
User Query
   ↓
Multi-Head Distilled BERT (Router)
   ↓
Hippocampus Multi-Task Router
   ├── Attention Head (Operation)
   │     └─ ["memory_in", "memory_out", "cur"]
   ├── Memory Head (Mode)
   │     └─ ["STM", "LTM", "none"]
   └── Answer Head (Response Type)
         └─ ["single", "multiple", "none"]

Flow:
- Query → encoded by DistilBERT → concatenated with emotion vector → fed to multi-task heads
- Each head predicts one of its respective labels
- Routing decision can use all 3 outputs together for hierarchical reasoning/execution
```

### MOE (mixture of experts) based router (Future plans).
```
User Query
   ↓
Level-1: Mode → [STM, LTM, Tool, Think]
   ├── STM
   │     ├── memory_in
   │     └── memory_out
   ├── LTM
   │     ├── memory_in
   │     └── memory_out
   ├── Tool
   │     ├── code_agent
   │     └── search_agent
   └── Think
         ├── simple_reason
         ├── reason_with_tools
         ├── reason_with_stm
         └── reason_with_ltm
```


### Router Heads

The policy model predicts three decisions in a **single forward pass**:

* **Attention Head**: `memory_in | memory_out | cur`

  * Store memory, retrieve memory, or execute agentic action
* **Memory Head**: `STM | LTM | none`

  * Selects the appropriate memory system
* **Answer Head**: `single | multiple | none`

  * Guides retrieval strategy and reranking

This routing mechanism functions as a digital analogue of the **human hippocampus**.

---

## Memory System Design

### Short-Term Memory (STM)

* Stored as lightweight **JSON files**
* Time-decay based (1–2 day retention)
* Similarity-based deduplication
* Optimized for recent, working-context information

### Long-Term Memory (LTM)

* Implemented using **Quadrant vector database (Dockerized)**
* Stores persistent personal facts and experiences
* Retrieval uses similarity + temporal scoring
* Optional reranker for high-precision, single-answer queries

---

## Emotion-Aware Personalization

Each query is augmented with a **26-dimensional emotion vector**, trained jointly with the routing model. This allows the system to:

* Retrieve memories that match emotional tone
* Improve personalization and alignment
* Prioritize emotionally significant events

Emotion is not just cosmetic—it actively improves memory relevance and decision quality.

---

## Agentic Capabilities

When the router predicts `cur`, the system enters **agentic mode**, enabling autonomous task execution beyond simple question-answering.

### Tiered Local Reasoning

* **Gemma 4B**: Low-latency, non-reasoning or conversational tasks
* **Qwen 3**: High-reasoning, planning, and complex multi-step execution

All inference runs **fully locally via Ollama**, preserving privacy and reducing latency.

### Tool Selection Policy

The **Tool Selection Policy** determines the most suitable function to execute for a given user query by combining **semantic relevance** with **historical usage patterns**, as defined in the project report.

Once the routing model predicts `cur`, indicating that the query requires action beyond memory retrieval or text generation, the system activates the tool selection mechanism.

#### Core Principles

1. **Semantic Relevance**
   Each available tool is represented by a textual description. The user query is embedded and compared against these tool embeddings using similarity search. Tools with the highest semantic similarity to the query are shortlisted as candidates.

2. **Historical Usage (Decayed Frequency)**
   The system maintains a lightweight usage history of tools. Each successful invocation contributes to a frequency score that **decays over time**, ensuring that recent and consistently effective tools are favored without permanently biasing the system.

#### Hybrid Selection Strategy

The final tool choice is made using a **hybrid strategy**:

* **Step 1: Similarity-First Filtering**
  Tools are ranked by embedding similarity to ensure relevance and correctness.

* **Step 2: Usage-Based Reinforcement**
  Among the top candidates, tools with higher decayed usage scores are preferred, reinforcing functions that have historically produced successful outcomes.

This approach balances:

* **Accuracy** – selecting tools that best match the semantic intent
* **Adaptability** – learning from past executions and improving over time

#### Execution Guarantees

* Tool selection is triggered **only when `cur` is predicted**
* The policy is **data-driven**, not rule-based
* No single tool can dominate permanently due to decay
* Selected tools operate within sandboxed, logged environments

This policy enables the Cognitive Digital Twin to behave like a human decision-maker—choosing actions based not only on understanding the current problem, but also on experience gained from prior successes.

### Android Debug Bridge (ADB) Tool
ADB is included as an optional agent tool for Android task execution. It is triggered only when the router predicts cur and integrates seamlessly with the existing Tool Selection Policy, requiring no changes to memory, routing, or reasoning architecture.
Capabilities: app launch/close, UI interaction (tap, swipe, text), device state queries, and simple workflow automation.
All ADB actions run locally, are sandboxed, and fully logged.

---

## Key Contributions

* **Multi-Head DistilBERT Router** for simultaneous action, memory, and answer prediction
* **Hippocampus-inspired routing layer** for cognitive decision-making
* **Dual-memory system** mirroring human STM/LTM
* **Emotion-integrated cognition** using a 26D emotion vector
* **Fully local, privacy-first architecture** with agentic execution

---

## Setup

```bash
git clone https://github.com/ganeshnikhil/MEMORY-TWIN.git
cd MEMORY-TWIN
```

### install ollama in mac
```bash
brew install ollama
ollama --version
```

### install ollama in windows
```bash
Go to: https://ollama.com/download
Download the Windows .exe installer
```

### install ollama in linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

### install models
```bash
ollama pull gemma3:4b
ollama pull qwen3:4b
ollama pull nomic-embed-text:latest
ollama list
```

### setup vector qudrant db
```bash
docker run -d \               
  --name qdrant \
  -p 6335:6333 \
  -p 6336:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \  
```
### create virtual enviroment

### macos/linux
```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### windows 
```bash
:: Create a virtual environment
python -m venv venv

:: Activate the virtual environment
venv\Scripts\activate

:: Upgrade pip
pip install --upgrade pip

:: Install dependencies
pip install -r requirements.txt
```

### Install dependencies:

```bash
pip install -r requirements.txt
```

Prepare memory storage:

```bash
mkdir -p ./data/memory_store/shortterm
```

Start Quadrant (for LTM) and Ollama models as configured.

---

## Quick Start

```python
from main import DigitalTwin

twin = DigitalTwin(
    model_path="./data/Models/multi_task_model_with_emotion",
    non_reasoning_model="gemma4b:4b",
    reasoning_model="qwen3:4b",
    temperature=0.0,
)

response = twin.process_query(
    "Remember my appointment tomorrow at 2 PM",
    agent="AssistantBot"
)

print(response["response"])
```

Run the UI:

```bash
streamlit run ui.py
```

---

## Evaluation Highlights

* **Memory Routing Accuracy**: 97.46%
* **Agentic Action Detection (`cur`)**: 95.49%
* **Answer Format Prediction**: 90.70%

The results confirm reliable cognitive routing and effective memory-agent integration.

---

## Why This Matters

The Cognitive Digital Twin demonstrates that **true personal AI memory is feasible today**—without cloud dependency. It moves beyond chat-based assistants toward **human-centered cognitive systems** that remember, reason, and act.

This project lays the groundwork for future **personalized, autonomous, and emotionally aware AI companions**.

---

## License

MIT License

## Acknowledgements

* Hugging Face Transformers
* Ollama
* Quadrant
* Streamlit
