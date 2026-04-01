# import ollama
# import numpy as np
# import re


# def clean_score(text: str) -> float:
#     """Extract a numeric score (0-1) from Ollama reranker response."""
#     match = re.findall(r"[-+]?\d*\.\d+|\d+", text)
#     if match:
#         try:
#             val = float(match[-1])
#             return max(0.0, min(1.0, val))  # clamp between 0 and 1
#         except ValueError:
#             return 0.0
#     return 0.0


# def reranker_as_embeddings(pairs, model="fanyx/Qwen3-Reranker-0.6B-Q8_0"):
#     """
#     Use Qwen3-Reranker as if it were an embedding model.
#     Each (query, doc) pair returns a 1D vector [score].
#     """
#     results = []
#     for query, doc in pairs:
#         prompt = f"""
# You are a reranker. Judge how relevant the document is to the query.
# Respond only with a number between 0 (irrelevant) and 1 (perfect match).

# <Query>: {query}
# <Document>: {doc}
# Relevance:
# """
#         response = ollama.embeddings(model=model, prompt=prompt)
#         # Reranker won't output embeddings, so fallback: extract score from text
#         raw = response.get("embedding", []) or response.get("message", {}).get("content", "")
#         if isinstance(raw, list):  # in case it returns dummy embedding
#             score = float(raw[0]) if raw else 0.0
#         else:
#             score = clean_score(str(raw))
#         results.append([score])  # wrap as vector
#     return np.array(results, dtype=np.float32)


# # ------------------- Example -------------------
# docs = [
#     "Marie Curie discovered radioactivity.",
#     "Albert Einstein was a famous physicist.",
#     "Isaac Newton formulated the laws of motion and universal gravitation.",
#     "Charles Darwin proposed the theory of evolution.",
#     "Quantum mechanics studies microscopic particles."
# ]

# query = "Who discovered radioactivity?"
# pairs = [(query, doc) for doc in docs]

# scores = reranker_as_embeddings(pairs).flatten()

# # Sort results by score
# sorted_idx = np.argsort(scores)[::-1]
# reranked_docs = [docs[i] for i in sorted_idx]

# print(f"Query: {query}\n")
# print("Reranker-as-Embeddings ranking:")
# for doc, score in zip(reranked_docs, scores[sorted_idx]):
#     print(f"- {doc} (score={score:.4f})")

import ollama

model = 'fanyx/Qwen3-Reranker-0.6B-Q8_0'

query = "Who discovered radioactivity?"
candidates = [
    "Marie Curie discovered radioactivity.",
    "Albert Einstein was a famous physicist.",
    "Isaac Newton formulated the laws of motion and universal gravitation.",
    "Charles Darwin proposed the theory of evolution."
]

# Build a prompt
prompt = "Rank the following documents by relevance to the query. Output as 'score | document':\n"
for doc in candidates:
    prompt += f"Document: {doc}\n"
prompt += f"Query: {query}\n"

# Send to Ollama
response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

# Access the text correctly
# Option 1: If response is a Message object
print(response.message.content)

# Option 2: If using newer version with .text attribute (some versions)
# print(response.text)
