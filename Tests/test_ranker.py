import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load Qwen3-Reranker-0.6B model
model_name = "Qwen/Qwen3-Reranker-0.6B"
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
model = AutoModelForCausalLM.from_pretrained(model_name).eval()

# True / False tokens
token_true_id = tokenizer.convert_tokens_to_ids("yes")
token_false_id = tokenizer.convert_tokens_to_ids("no")

# Prefix / Suffix for reranker prompt
prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
prefix_tokens = tokenizer.encode(prefix, add_special_tokens=False)
suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)
max_length = 8192

def format_instruction(query: str, doc: str) -> str:
    task = "Given a query, determine how relevant the candidate document is."
    return f"<Instruct>: {task}\n<Query>: {query}\n<Document>: {doc}"

def reranker_as_embedding(pairs):
    """
    Treats Qwen3-Reranker-0.6B as an embedding model.
    Returns a float score for each (query, candidate) pair.
    """
    scores = []
    for query, doc in pairs:
        text = format_instruction(query, doc)
        tokens = tokenizer.encode(text, add_special_tokens=False)
        input_ids = torch.tensor([prefix_tokens + tokens + suffix_tokens])
        input_ids = input_ids.to(model.device)

        with torch.no_grad():
            logits = model(input_ids).logits[:, -1, :]
            true_logit = logits[:, token_true_id]
            false_logit = logits[:, token_false_id]
            log_probs = torch.nn.functional.log_softmax(torch.stack([false_logit, true_logit], dim=1), dim=1)
            score = log_probs[:, 1].exp().item()  # probability for "yes"
        scores.append(score)
    return scores

# ------------------- Example -------------------
pairs = [
    ("Who discovered radioactivity?", "Marie Curie discovered radioactivity."),
    ("Who discovered radioactivity?", "Albert Einstein was a famous physicist."),
    ("Who discovered radioactivity?", "Isaac Newton formulated the laws of motion and universal gravitation."),
]

scores = reranker_as_embedding(pairs)
reranked = sorted(zip([doc for _, doc in pairs], scores), key=lambda x: x[1], reverse=True)

print("Reranked candidates:")
for doc, score in reranked:
    print(f"- {doc} (score: {score:.4f})")
