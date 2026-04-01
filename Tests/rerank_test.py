# import ollama
# import numpy as np
# from sklearn.metrics import precision_score, recall_score, f1_score

# # Memory and queries
# memory_items = [
#     "Albert Einstein was a famous physicist.",
#     "Quantum mechanics studies the behavior of particles at microscopic scales.",
#     "Isaac Newton formulated the laws of motion and universal gravitation.",
#     "Relativity describes how space and time are linked for objects moving at constant speeds.",
#     "The Schrödinger equation describes how the quantum state of a physical system changes over time.",
#     "Marie Curie discovered radioactivity.",
#     "The theory of evolution was proposed by Charles Darwin.",
#     "The mitochondrion is known as the powerhouse of the cell.",
#     "Photosynthesis is the process by which plants convert sunlight into energy.",
#     "DNA carries genetic instructions for the development of living organisms.",
#     "The periodic table organizes chemical elements by atomic number.",
#     "Water is composed of hydrogen and oxygen in a 2:1 ratio.",
#     "Alan Turing is considered the father of modern computer science.",
#     "Moore's Law predicts that the number of transistors on a microchip doubles approximately every two years.",
#     "Artificial intelligence is the simulation of human intelligence in machines."
# ]

# queries = [
#     ("Who is Albert Einstein?", "Albert Einstein was a famous physicist."),
#     ("Define quantum mechanics?", "Quantum mechanics studies the behavior of particles at microscopic scales."),
#     ("Tell me about Isaac Newton", "Isaac Newton formulated the laws of motion and universal gravitation."),
#     ("What is relativity?", "Relativity describes how space and time are linked for objects moving at constant speeds."),
#     ("Explain the Schrödinger equation", "The Schrödinger equation describes how the quantum state of a physical system changes over time."),
#     ("Who discovered radioactivity?", "Marie Curie discovered radioactivity."),
# ]

# # ---------- Embedding functions ----------
# def embed_texts(texts, model):
#     embeddings = []
#     for t in texts:
#         response = ollama.embeddings(model=model, prompt=t)
#         embeddings.append(response["embedding"])
#     return np.array(embeddings)

# def cosine_similarity(a, b):
#     a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
#     b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
#     return np.dot(a_norm, b_norm.T)

# # ---------- Reranker function ----------
# def rerank_candidates(query, candidates, reranker_model="qllama/bce-reranker-base_v1:latest"):
#     scored = []
#     for candidate in candidates:
#         # Use reranker as an embedding model (no prompts)
#         query_emb = np.array(ollama.embeddings(model=reranker_model, prompt=query)["embedding"])
#         cand_emb = np.array(ollama.embeddings(model=reranker_model, prompt=[(query,candidate)])["embedding"])
#         # Cosine similarity as score
#         score = np.dot(query_emb, cand_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(cand_emb))
#         scored.append((candidate, score))
#     reranked = sorted(scored, key=lambda x: x[1], reverse=True)
#     print(reranked)
#     return [c for c, s in reranked]

# # ---------- Evaluation ----------
# def evaluate_with_reranker(embed_model, reranker_model, top_k=3):
#     mem_embeds = embed_texts(memory_items, embed_model)
#     query_texts = [q[0] for q in queries]
#     query_embeds = embed_texts(query_texts, embed_model)

#     y_true, y_pred = [], []

#     for i, (query, gt_answer) in enumerate(queries):
#         sims = cosine_similarity(query_embeds[i:i+1], mem_embeds)[0]
#         top_indices = np.argsort(sims)[::-1][:top_k]
#         candidates = [memory_items[idx] for idx in top_indices]

#         # Rerank candidates
#         reranked = rerank_candidates(query, candidates, reranker_model)
#         retrieved = reranked[:top_k]

#         # Metrics
#         retrieved_set = set(retrieved)
#         y_true.append([1 if item == gt_answer else 0 for item in memory_items])
#         y_pred.append([1 if item in retrieved_set else 0 for item in memory_items])

#         print(f"\nQuery: {query}")
#         print(f"Top-{top_k} after reranker: {retrieved}")

#     y_true = np.array(y_true).flatten()
#     y_pred = np.array(y_pred).flatten()

#     precision = precision_score(y_true, y_pred)
#     recall = recall_score(y_true, y_pred)
#     f1 = f1_score(y_true, y_pred)
#     print(f"\nTop-{top_k} Metrics with Reranker for {embed_model}: Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")
#     return precision, recall, f1

# # ---------- Run ----------
# if __name__ == "__main__":
#     embedding_models = ["nomic-embed-text:latest", "mxbai-embed-large:latest"]
#     reranker_model = "qllama/bce-reranker-base_v1:latest"

#     for model in embedding_models:
#         print(f"\n===== Evaluating {model} with reranker =====")
#         evaluate_with_reranker(model, reranker_model, top_k=3)


# import numpy as np
# from ollama import embeddings
# import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM

# # ------------------- Reranker Setup -------------------
# reranker_model_name = "Qwen/Qwen3-Reranker-0.6B"
# tokenizer = AutoTokenizer.from_pretrained(reranker_model_name, padding_side='left')
# reranker_model = AutoModelForCausalLM.from_pretrained(reranker_model_name).eval()

# token_true_id = tokenizer.convert_tokens_to_ids("yes")
# token_false_id = tokenizer.convert_tokens_to_ids("no")

# prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
# suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
# prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
# suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

# def format_instruction(query: str, doc: str) -> str:
#     task = "Given a query, determine how relevant the candidate document is."
#     return f"<Instruct>: {task}\n<Query>: {query}\n<Document>: {doc}"

# def rerank_with_qwen(query, docs):
#     scores = []
#     for doc in docs:
#         text = format_instruction(query, doc)
#         tokens = tokenizer.encode(text, add_special_tokens=False)
#         input_ids = torch.tensor([prefix_tokens + tokens + suffix_tokens])
#         input_ids = input_ids.to(reranker_model.device)

#         with torch.no_grad():
#             logits = reranker_model(input_ids).logits[:, -1, :]
#             true_logit = logits[:, token_true_id]
#             false_logit = logits[:, token_false_id]
#             log_probs = torch.nn.functional.log_softmax(
#                 torch.stack([false_logit, true_logit], dim=1), dim=1
#             )
#             score = log_probs[:, 1].exp().item()
#         scores.append((doc, score))
#     return [doc for doc, _ in sorted(scores, key=lambda x: x[1], reverse=True)], scores


# # ------------------- Embedding Search (No FAISS) -------------------
# def embed_texts_ollama(texts, model="mxbai-embed-large:latest"):
#     return np.array([embeddings(model=model, prompt=t)["embedding"] for t in texts], dtype=np.float32)

# def cosine_similarity(a, b):
#     a = a / np.linalg.norm(a)
#     b = b / np.linalg.norm(b, axis=1, keepdims=True)
#     return np.dot(b, a)

# def retrieve_with_embeddings(query, docs, embed_model):
#     doc_embeddings = embed_texts_ollama(docs, model=embed_model)
#     query_emb = embed_texts_ollama([query], model=embed_model)[0]
#     sims = cosine_similarity(query_emb, doc_embeddings)
#     sorted_idx = np.argsort(sims)[::-1]
#     return [docs[i] for i in sorted_idx], sims[sorted_idx]


# # ------------------- Experiment -------------------
# docs = [
#     "Marie Curie discovered radioactivity.",
#     "Albert Einstein was a famous physicist.",
#     "Isaac Newton formulated the laws of motion and universal gravitation.",
#     "Charles Darwin proposed the theory of evolution.",
#     "Quantum mechanics studies microscopic particles."
# ]

# query = "Who discovered radioactivity?"




# for embed_model in ["mxbai-embed-large:latest", "nomic-embed-text:latest"]:
#     print(f"\n=== Using embedding model: {embed_model} ===")
    
#     # Embedding-only ranking
#     retrieved, sims = retrieve_with_embeddings(query, docs, embed_model)
#     print("\nEmbedding-only ranking:")
#     for doc, score in zip(retrieved, sims):
#         print(f"- {doc} (similarity={score:.4f})")

#     # Embedding + Reranker
#     reranked, rerank_scores = rerank_with_qwen(query, retrieved)
#     print("\nEmbedding + Reranker ranking:")
#     for doc, score in rerank_scores:
#         print(f"- {doc} (rerank_score={score:.4f})")


import numpy as np
from ollama import embeddings
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ------------------- Reranker Setup -------------------
reranker_model_name = "Qwen/Qwen3-Reranker-0.6B"
tokenizer = AutoTokenizer.from_pretrained(reranker_model_name, padding_side='left')
reranker_model = AutoModelForCausalLM.from_pretrained(reranker_model_name).eval()

token_true_id = tokenizer.convert_tokens_to_ids("yes")
token_false_id = tokenizer.convert_tokens_to_ids("no")

prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

def format_instruction(query: str, doc: str) -> str:
    task = "Given a query, determine how relevant the candidate document is."
    return f"<Instruct>: {task}\n<Query>: {query}\n<Document>: {doc}"

def rerank_with_qwen(query, docs):
    scores = []
    for doc in docs:
        text = format_instruction(query, doc)
        tokens = tokenizer.encode(text, add_special_tokens=False)
        input_ids = torch.tensor([prefix_tokens + tokens + suffix_tokens])
        input_ids = input_ids.to(reranker_model.device)

        with torch.no_grad():
            logits = reranker_model(input_ids).logits[:, -1, :]
            true_logit = logits[:, token_true_id]
            false_logit = logits[:, token_false_id]
            log_probs = torch.nn.functional.log_softmax(
                torch.stack([false_logit, true_logit], dim=1), dim=1
            )
            score = log_probs[:, 1].exp().item()
        scores.append((doc, score))
    return [doc for doc, _ in sorted(scores, key=lambda x: x[1], reverse=True)], scores


# ------------------- Embedding Search -------------------
def embed_texts_ollama(texts, model="mxbai-embed-large:latest"):
    return np.array([embeddings(model=model, prompt=t)["embedding"] for t in texts], dtype=np.float32)

def cosine_similarity(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(b, a)

def retrieve_with_embeddings(query, docs, embed_model):
    doc_embeddings = embed_texts_ollama(docs, model=embed_model)
    query_emb = embed_texts_ollama([query], model=embed_model)[0]
    sims = cosine_similarity(query_emb, doc_embeddings)
    sorted_idx = np.argsort(sims)[::-1]
    return [docs[i] for i in sorted_idx], sims[sorted_idx]


# ------------------- Experiment -------------------
docs = [
    "Marie Curie discovered radioactivity.",
    "Albert Einstein was a famous physicist.",
    "Newton was a famous physicist.",
    "Isaac Newton formulated the laws of motion and universal gravitation.",
    "Charles Darwin proposed the theory of evolution.",
    "Quantum mechanics studies microscopic particles.",
    "Photosynthesis converts sunlight into energy.",
    "The mitochondrion is the powerhouse of the cell.",
    "Alan Turing is the father of modern computer science.",
    "Relativity links space and time for moving objects."
]

queries = [
    "Who discovered radioactivity?",
    "Who are famous physicists?",
    "Explain quantum mechanics.",
    "What converts sunlight into energy?",
    "Who is the father of computer science?"
]


for embed_model in ["mxbai-embed-large:latest", "nomic-embed-text:latest"]:
    print(f"\n=== Using embedding model: {embed_model} ===")

    for query in queries:
        print(f"\nQuery: {query}")

        # Embedding-only ranking
        retrieved, sims = retrieve_with_embeddings(query, docs, embed_model)
        print(f"\n{embed_model} Embedding-only ranking:")
        for doc, score in zip(retrieved, sims):
            print(f"- {doc} (similarity={score:.4f})")

        # Embedding + Reranker
        reranked, rerank_scores = rerank_with_qwen(query, retrieved)
        print("\nEmbedding + Reranker ranking:")
        for doc, score in rerank_scores:
            print(f"- {doc} (rerank_score={score:.4f})")

        print("-" * 50)
