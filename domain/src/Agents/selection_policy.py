import json
import os
import numpy as np
import ollama
from sklearn.metrics.pairwise import cosine_similarity


class ToolSelector:
    def __init__(
        self,
        tools_schema,
        embd_model_name,
        freq_path,
        top_n=3,
        top_freq_n=3,
        alpha=0.2,
        decay=0.98,
        init_freq=0.1
    ):
        self.tools_schema = tools_schema
        self.tool_map = {t["name"]: t for t in tools_schema}
        self.EMBD_MODEL_NAME = embd_model_name

        self.top_n = top_n
        self.top_freq_n = top_freq_n
        self.alpha = alpha
        self.decay = decay
        self.init_freq = init_freq

        self.freq_path = freq_path
        self.tool_freq = self._load_frequency()

        for name in self.tool_map:
            self.tool_freq.setdefault(name, self.init_freq)

    # ------------------ Frequency memory ------------------

    def _load_frequency(self):
        # If file does not exist → create it
        if not os.path.exists(self.freq_path):
            with open(self.freq_path, "w") as f:
                json.dump({}, f)
            return {}

        # If file exists → try loading
        try:
            with open(self.freq_path, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)

        except json.JSONDecodeError:
            # Corrupted file → reset
            with open(self.freq_path, "w") as f:
                json.dump({}, f)
            return {}


    def save(self):
        for k, v in self.tool_freq.items():
            self.tool_freq[k] = max(0.0, min(1.0, float(v)))

        tmp = self.freq_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.tool_freq, f, indent=2)

        os.replace(tmp, self.freq_path)

    def update_frequency(self, tool_name):
        freq = self.tool_freq.get(tool_name, self.init_freq)
        freq *= self.decay
        freq = self.alpha * 1.0 + (1 - self.alpha) * freq
        freq = min(1.0, max(0.0, round(freq, 4)))
        self.tool_freq[tool_name] = freq

    # ------------------ Selection methods ------------------

    def select_by_embedding(self, query, k=None):
        """
        Select top-k tools purely by embedding similarity.
        """
        k = k or self.top_n

        tools_with_desc = [t for t in self.tools_schema if t.get("description")]
        if not tools_with_desc:
            return []

        query_emb = ollama.embed(
            model=self.EMBD_MODEL_NAME,
            input=query
        ).embeddings[0]

        tool_descs = [t["description"] for t in tools_with_desc]
        tool_embs = ollama.embed(
            model=self.EMBD_MODEL_NAME,
            input=tool_descs
        ).embeddings

        scores = cosine_similarity(
            np.array(query_emb).reshape(1, -1),
            np.array(tool_embs)
        )[0]

        ranked_idx = np.argsort(scores)[::-1][:k]
        return [tools_with_desc[i] for i in ranked_idx]

    def select_by_frequency(self, k=None, exclude=None):
        """
        Select top-k tools purely by learned frequency.
        """
        k = k or self.top_freq_n
        exclude = exclude or set()

        ranked = sorted(
            [(name, freq) for name, freq in self.tool_freq.items()
            if name not in exclude],
            key=lambda x: x[1],
            reverse=True
        )

        return [self.tool_map[name] for name, _ in ranked[:k]]
    
    def expand_embedding_budget(self, step=2):
        self.top_n = min(
            self.top_n + step,
            len(self.tool_map)
        )

    # ------------------ Policy layer ------------------

    def select_tools(self, query, policy="hybrid"):
        """
        policy:
        - 'embedding'
        - 'frequency'
        - 'hybrid'
        """

        if policy == "embedding":
            return self.select_by_embedding(query)

        if policy == "frequency":
            return self.select_by_frequency()

        if policy == "hybrid":
            emb_tools = self.select_by_embedding(query)
            emb_names = {t["name"] for t in emb_tools}

            freq_tools = self.select_by_frequency(exclude=emb_names)
            return emb_tools + freq_tools

        raise ValueError(f"Unknown selection policy: {policy}")


if __name__ == "__main__":

    # ------------------ Dummy tools ------------------

    tools_schema = [
        {
            "name": "get_weather",
            "description": "Get current weather of a city"
        },
        {
            "name": "get_time",
            "description": "Get current local time of a city"
        },
        {
            "name": "add",
            "description": "Add two numbers"
        },
        {
            "name": "multiply",
            "description": "Multiply two numbers"
        }
    ]

    # ------------------ Frequency storage ------------------

    FREQ_FILE = "tool_freq.json"

    if not os.path.exists(FREQ_FILE):
        with open(FREQ_FILE, "w") as f:
            json.dump({}, f)

    # ------------------ Initialize selector ------------------

    selector = ToolSelector(
        tools_schema=tools_schema,
        embd_model_name="nomic-embed-text",  # or any embedding model you have
        freq_path=FREQ_FILE,
        top_n=2,
        top_freq_n=2
    )

    # ------------------ Run selections ------------------

    query = "What is the weather in Delhi?"

    print("\n🔹 Query:", query)

    print("\n🔹 Embedding-based selection:")
    emb_tools = selector.select_by_embedding(query)
    for t in emb_tools:
        print("  -", t["name"])

    print("\n🔹 Frequency-based selection:")
    freq_tools = selector.select_by_frequency()
    for t in freq_tools:
        print("  -", t["name"])

    print("\n🔹 Hybrid selection:")
    hybrid_tools = selector.select_tools(query, policy="hybrid")
    for t in hybrid_tools:
        print("  -", t["name"])

    # ------------------ Simulate usage update ------------------

    print("\n🔹 Updating frequency for: get_weather")
    selector.update_frequency("get_weather")
    selector.save()

    print("\n🔹 Updated frequency memory:")
    print(json.dumps(selector.tool_freq, indent=2))
