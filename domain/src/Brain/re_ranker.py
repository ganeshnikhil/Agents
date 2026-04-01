import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import CrossEncoder


class RERANKER:
    def __init__(self, model_name="mixedbread-ai/mxbai-rerank-xsmall-v1"):
        self.model_name = model_name
        self.model = CrossEncoder(self.model_name)

    def reranker(self, query, documents):
        # Ensure all documents are plain strings
        clean_docs = []
        for doc in documents:
            if isinstance(doc, str):
                clean_docs.append(doc)
            elif isinstance(doc, dict):
                # Common case: doc from memory store, with text under 'text' or 'content'
                clean_docs.append(doc.get("text") or doc.get("content") or str(doc))
            else:
                clean_docs.append(str(doc))
        
        if not clean_docs:
            raise ValueError("No valid text documents provided for reranking.")
        
        # Perform reranking
        results = self.model.rank(query, clean_docs, return_documents=True, top_k=1 ,  show_progress_bar=False, batch_size=32)
        return results[0].get("text"), results[0].get("score")

                
class QwenReranker:
    def __init__(self, model_name="Qwen/Qwen3-Reranker-0.6B"):
        # Load model & tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side='left')
        self.model = AutoModelForCausalLM.from_pretrained(model_name).eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

        # Yes/No token IDs
        self.token_true_id = self.tokenizer.convert_tokens_to_ids("yes")
        self.token_false_id = self.tokenizer.convert_tokens_to_ids("no")

        # Prefix and suffix tokens
        self.prefix = "<|im_start|>system\nJudge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\".<|im_end|>\n<|im_start|>user\n"
        self.suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        self.prefix_tokens = self.tokenizer.encode(self.prefix, add_special_tokens=False)
        self.suffix_tokens = self.tokenizer.encode(self.suffix, add_special_tokens=False)

    def format_instruction(self, query: str, doc: str) -> str:
        task = "Given a query, determine how relevant the candidate document is."
        return f"<Instruct>: {task}\n<Query>: {query}\n<Document>: {doc}"

    def rerank(self, query_doc_list):
        """
        Args:
            query_doc_list: List of tuples [(query, doc1), (query, doc2), ...]
        Returns:
            best_doc: The document with highest relevance score
            scores: List of tuples [(doc, score), ...] sorted by score desc
        """
        scores = []
        for query, doc in query_doc_list:
            text = self.format_instruction(query, doc)
            tokens = self.tokenizer.encode(text, add_special_tokens=False)
            input_ids = torch.tensor([self.prefix_tokens + tokens + self.suffix_tokens]).to(self.device)

            with torch.no_grad():
                logits = self.model(input_ids).logits[:, -1, :]
                true_logit = logits[:, self.token_true_id]
                false_logit = logits[:, self.token_false_id]
                log_probs = torch.nn.functional.log_softmax(
                    torch.stack([false_logit, true_logit], dim=1), dim=1
                )
                score = log_probs[:, 1].exp().item()  # probability of "yes"
            scores.append((doc, score))

        # Sort descending by score
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        best_doc = sorted_scores[0][0] if sorted_scores else None
        return best_doc, sorted_scores


# ---- Example Usage ----
if __name__ == "__main__":
    #reranker = QwenReranker()
    rernak = RERANKER()
    #Bgeranker = BgeReranker()
    # query_doc_list = [
    #     ("Who discovered radioactivity?", "Marie Curie was the first woman to study radioactivity."),
    #     ("Who discovered radioactivity?", "Albert Einstein developed the theory of relativity."),
    #     ("Who discovered radioactivity?", "Isaac Newton formulated the laws of motion.")
    # ]
    
    # best_doc, scores = reranker.rerank(query_doc_list)
    
    #best_d , sco = BgeReranker.rerank(query_doc_list)
    # print(best_d , sco)
    
    # print("Best Document:", best_doc)
    # print("All Scores:", scores)
    
    query = "Who discovered radioactivity? "
    documents = ["Marie Curie was the first woman to study radioactivity." ,  "Albert Einstein developed the theory of relativity." , "Isaac Newton formulated the laws of motion."]
    best_doc , score = rernak.reranker(query , documents)
    print("Best Document:", best_doc)
    print("All Scores:", score)
