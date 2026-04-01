"""
Benchmark: Compare embeddinggemma vs nomic-embed-text for memory retrieval
Using Ollama to generate embeddings
"""

# import ollama
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.preprocessing import normalize

# # -----------------------------
# # Example Queries & Memory
# # -----------------------------
# queries = ["Who is Albert Einstein?", "Define quantum mechanics?"]
# memory_items = [
#     "Albert Einstein was a famous physicist.",
#     "Quantum mechanics studies the behavior of particles at microscopic scales.",
#     "Isaac Newton formulated the laws of motion."
# ]

# # Ground truth mapping (which memory items are relevant for each query)
# ground_truth_memory = [
#     [0],  # Query 0 -> memory_items[0]
#     [1],  # Query 1 -> memory_items[1]
# ]

# # -----------------------------
# # Helper Functions
# # -----------------------------
# def get_embeddings(text_list, model_name):
#     """
#     Generate embeddings using Ollama
#     """
#     embeddings = []
#     for text in text_list:
#         response = ollama.embeddings(model=model_name, prompt=text)
#         # Ollama embeddings return a list of floats
#         embeddings.append(response.embedding)
#     embeddings = np.array(embeddings)
#     return normalize(embeddings)  # Normalize for cosine similarity

# def retrieve_top_k(query_emb, memory_emb, k=1):
#     """
#     Retrieve top-k nearest neighbors using cosine similarity
#     """
#     sims = cosine_similarity(query_emb, memory_emb)
#     top_k = np.argsort(-sims, axis=1)[:, :k]  # descending order
#     return top_k

# def compute_precision_recall_f1(results_idx, ground_truth):
#     """
#     Compute simple precision, recall, F1 at top-1
#     """
#     precisions, recalls, f1s = [], [], []
#     for i, retrieved in enumerate(results_idx):
#         retrieved_set = set(retrieved)
#         relevant_set = set(ground_truth[i])
#         tp = len(retrieved_set & relevant_set)
#         precision = tp / max(len(retrieved_set), 1)
#         recall = tp / max(len(relevant_set), 1)
#         f1 = 2 * precision * recall / max(precision + recall, 1e-8)
#         precisions.append(precision)
#         recalls.append(recall)
#         f1s.append(f1)
#     return np.mean(precisions), np.mean(recalls), np.mean(f1s)

# # -----------------------------
# # Run Benchmark
# # -----------------------------
# embedding_models = ["embeddinggemma:latest", "nomic-embed-text:latest"]

# for model_name in embedding_models:
#     print(f"\n=== Testing embeddings with model: {model_name} ===")
    
#     # Generate embeddings
#     memory_emb = get_embeddings(memory_items, model_name)
#     query_emb = get_embeddings(queries, model_name)
    
#     # Retrieve nearest memory item
#     results_idx = retrieve_top_k(query_emb, memory_emb, k=1)
    
#     # Compute metrics
#     precision, recall, f1 = compute_precision_recall_f1(results_idx, ground_truth_memory)
#     print(f"Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
    
#     # Optional: Show retrieved results
#     for i, idx in enumerate(results_idx):
#         print(f"Query: {queries[i]}")
#         print(f"Retrieved Memory: {memory_items[idx[0]]}")


"""
Extended Embedding Benchmark: Top-1 and Top-3 Retrieval
Using Ollama embeddings for embeddinggemma and nomic-embed-text
"""

# import ollama
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.preprocessing import normalize

# # -----------------------------
# # Example Queries & Large Memory
# # -----------------------------
# queries = [
#     "Who is Albert Einstein?",
#     "Define quantum mechanics?",
#     "Tell me about Isaac Newton",
#     "What is relativity?",
#     "Explain the Schrödinger equation"
# ]

# memory_items = [
#     "Albert Einstein was a famous physicist.",
#     "Quantum mechanics studies the behavior of particles at microscopic scales.",
#     "Isaac Newton formulated the laws of motion and universal gravitation.",
#     "Relativity describes how space and time are linked for objects moving at constant speeds.",
#     "The Schrödinger equation describes how the quantum state of a physical system changes over time.",
#     "Marie Curie discovered radioactivity.",
#     "Nikola Tesla developed alternating current.",
#     "The theory of evolution was proposed by Charles Darwin.",
#     "Photosynthesis converts light energy into chemical energy in plants.",
#     "The human heart pumps blood through the circulatory system."
# ]

# # Ground truth mapping (index of relevant memory item for each query)
# ground_truth_memory = [
#     [0],
#     [1],
#     [2],
#     [3],
#     [4]
# ]

# # -----------------------------
# # Helper Functions
# # -----------------------------
# def get_embeddings(text_list, model_name):
#     embeddings = []
#     for text in text_list:
#         response = ollama.embeddings(model=model_name, prompt=text)
#         embeddings.append(response.embedding)
#     embeddings = np.array(embeddings)
#     return normalize(embeddings)

# def retrieve_top_k(query_emb, memory_emb, k=3):
#     sims = cosine_similarity(query_emb, memory_emb)
#     top_k = np.argsort(-sims, axis=1)[:, :k]
#     return top_k

# def compute_precision_recall_f1(results_idx, ground_truth):
#     precisions, recalls, f1s = [], [], []
#     for i, retrieved in enumerate(results_idx):
#         retrieved_set = set(retrieved)
#         relevant_set = set(ground_truth[i])
#         tp = len(retrieved_set & relevant_set)
#         precision = tp / max(len(retrieved_set), 1)
#         recall = tp / max(len(relevant_set), 1)
#         f1 = 2 * precision * recall / max(precision + recall, 1e-8)
#         precisions.append(precision)
#         recalls.append(recall)
#         f1s.append(f1)
#     return np.mean(precisions), np.mean(recalls), np.mean(f1s)

# # -----------------------------
# # Run Benchmark for both models
# # -----------------------------
# embedding_models = ["embeddinggemma:latest", "nomic-embed-text:latest"]

# for model_name in embedding_models:
#     print(f"\n=== Testing embeddings with model: {model_name} ===")
    
#     memory_emb = get_embeddings(memory_items, model_name)
#     query_emb = get_embeddings(queries, model_name)
    
#     for k in [1, 3]:
#         results_idx = retrieve_top_k(query_emb, memory_emb, k=k)
#         precision, recall, f1 = compute_precision_recall_f1(results_idx, ground_truth_memory)
#         print(f"\nTop-{k} Retrieval Metrics:")
#         print(f"Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
        
#         # Optional: Show retrieved items per query
#         for i, idx in enumerate(results_idx):
#             retrieved_items = [memory_items[j] for j in idx]
#             print(f"Query: {queries[i]}")
#             print(f"Retrieved Top-{k}: {retrieved_items}")


"""
Automated Retrieval Benchmark Table
Computes Top-1 and Top-3 metrics for multiple embedding models using Ollama
"""

# import ollama
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.preprocessing import normalize
# from tabulate import tabulate  # pip3 install tabulate

# # -----------------------------
# # Queries and Memory Items
# # -----------------------------
# queries = [
#     "Who is Albert Einstein?",
#     "Define quantum mechanics?",
#     "Tell me about Isaac Newton",
#     "What is relativity?",
#     "Explain the Schrödinger equation"
# ]

# memory_items = [
#     "Albert Einstein was a famous physicist.",
#     "Quantum mechanics studies the behavior of particles at microscopic scales.",
#     "Isaac Newton formulated the laws of motion and universal gravitation.",
#     "Relativity describes how space and time are linked for objects moving at constant speeds.",
#     "The Schrödinger equation describes how the quantum state of a physical system changes over time.",
#     "Marie Curie discovered radioactivity.",
#     "Nikola Tesla developed alternating current.",
#     "The theory of evolution was proposed by Charles Darwin.",
#     "Photosynthesis converts light energy into chemical energy in plants.",
#     "The human heart pumps blood through the circulatory system."
# ]

# ground_truth_memory = [
#     [0],  # Who is Albert Einstein? -> memory_items[0]
#     [1],  # Define quantum mechanics? -> memory_items[1]
#     [2],  # Isaac Newton -> memory_items[2]
#     [3],  # What is relativity? -> memory_items[3]
#     [4],  # Schrödinger equation -> memory_items[4]
# ]

# # -----------------------------
# # Helper Functions
# # -----------------------------
# def get_embeddings(text_list, model_name):
#     embeddings = []
#     for text in text_list:
#         response = ollama.embeddings(model=model_name, prompt=text)
#         embeddings.append(response.embedding)
#     embeddings = np.array(embeddings)
#     return normalize(embeddings)

# def retrieve_top_k(query_emb, memory_emb, k=3):
#     sims = cosine_similarity(query_emb, memory_emb)
#     top_k = np.argsort(-sims, axis=1)[:, :k]
#     return top_k

# def compute_precision_recall_f1(results_idx, ground_truth):
#     precisions, recalls, f1s = [], [], []
#     for i, retrieved in enumerate(results_idx):
#         retrieved_set = set(retrieved)
#         relevant_set = set(ground_truth[i])
#         tp = len(retrieved_set & relevant_set)
#         precision = tp / max(len(retrieved_set), 1)
#         recall = tp / max(len(relevant_set), 1)
#         f1 = 2 * precision * recall / max(precision + recall, 1e-8)
#         precisions.append(precision)
#         recalls.append(recall)
#         f1s.append(f1)
#     return np.mean(precisions), np.mean(recalls), np.mean(f1s)

# # -----------------------------
# # Run Benchmark
# # -----------------------------
# embedding_models = ["embeddinggemma:latest", "nomic-embed-text:latest"]
# top_k_values = [1, 3]

# table_rows = []

# for model_name in embedding_models:
#     memory_emb = get_embeddings(memory_items, model_name)
#     query_emb = get_embeddings(queries, model_name)
    
#     for k in top_k_values:
#         results_idx = retrieve_top_k(query_emb, memory_emb, k=k)
#         precision, recall, f1 = compute_precision_recall_f1(results_idx, ground_truth_memory)
#         table_rows.append([model_name, k, round(precision,3), round(recall,3), round(f1,3)])

# # -----------------------------
# # Print Table
# # -----------------------------
# headers = ["Embedding Model", "Top-K", "Precision", "Recall", "F1"]
# print(tabulate(table_rows, headers=headers, tablefmt="grid"))
import ollama
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

# -------------------------
# Memory items (toy dataset)
# -------------------------
memory_items = [
    "Meeting with HR at 10 AM",
    "Team standup at 9 AM",
    "Doctor appointment at 6 PM",
    "Albert Einstein was a famous physicist.",
    "Quantum mechanics studies the behavior of particles at microscopic scales.",
    "Meeting with client at 3 PM",
    "Lunch with Sarah at 1 PM",
]

# Queries with **multiple possible correct answers**
queries = [
    # Single-answer case
    ("Who is Albert Einstein?", ["Albert Einstein was a famous physicist."]),
    
    # Multi-answer case
    ("Is there any meeting today?", [
        "Meeting with HR at 10 AM",
        "Team standup at 9 AM",
        "Meeting with client at 3 PM"
    ]),
    
    # Another single-answer case
    ("Define quantum mechanics?", [
        "Quantum mechanics studies the behavior of particles at microscopic scales."
    ]),
]

# -------------------------
# Embedding helper functions
# -------------------------
def embed_texts(texts, model):
    """Generate embeddings using Ollama"""
    embeddings = []
    for t in texts:
        response = ollama.embeddings(model=model, prompt=t)
        embeddings.append(response["embedding"])
    return np.array(embeddings)

def cosine_similarity(a, b):
    """Cosine similarity between vectors"""
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(a_norm, b_norm.T)

# -------------------------
# Evaluation
# -------------------------
def evaluate_model(model_name, top_k=3):
    print(f"\n=== Testing embeddings with model: {model_name} ===")

    mem_embeds = embed_texts(memory_items, model_name)
    query_texts = [q[0] for q in queries]
    query_embeds = embed_texts(query_texts, model_name)

    all_precisions, all_recalls, all_f1s = [], [], []
    coverage_hits = 0

    for i, (query, gt_answers) in enumerate(queries):
        sims = cosine_similarity(query_embeds[i:i+1], mem_embeds)[0]
        top_indices = np.argsort(sims)[::-1][:top_k]
        retrieved = [memory_items[idx] for idx in top_indices]

        print(f"\nQuery: {query}")
        print(f"Retrieved Top-{top_k}: {retrieved}")
        print(f"Ground truth: {gt_answers}")

        # Binary relevance vectors
        y_true = [1 if item in gt_answers else 0 for item in memory_items]
        y_pred = [1 if item in retrieved else 0 for item in memory_items]

        # Metrics
        p = precision_score(y_true, y_pred)
        r = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        all_precisions.append(p)
        all_recalls.append(r)
        all_f1s.append(f1)

        # Coverage: at least one correct retrieved
        if any(item in retrieved for item in gt_answers):
            coverage_hits += 1

    # Averages
    precision = np.mean(all_precisions)
    recall = np.mean(all_recalls)
    f1 = np.mean(all_f1s)
    coverage = coverage_hits / len(queries)

    print(f"\nTop-{top_k} Retrieval Metrics for {model_name}:")
    print(f"Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}, Coverage: {coverage:.3f}")
    return precision, recall, f1, coverage


if __name__ == "__main__":
    models = ["nomic-embed-text:latest", "mxbai-embed-large"]
    results = []
    for model in models:
        results.append((model + " Top-3", *evaluate_model(model, top_k=3)))

    # Summary
    print("\n=== Summary Table ===")
    print(f"{'Model':35} {'Precision':<10} {'Recall':<10} {'F1':<10} {'Coverage':<10}")
    for model, precision, recall, f1, coverage in results:
        print(f"{model:35} {precision:<10.3f} {recall:<10.3f} {f1:<10.3f} {coverage:<10.3f}")
