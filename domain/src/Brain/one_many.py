import re
from typing import List, Dict

class MultiAnswerHeuristic:
    def __init__(self):
        # Multi-answer cues
        self.multi_keywords = [
            "list", "names", "types", "examples", "all", "top", "best",
            "various", "different", "multiple", "several", "many", "few",
            "kinds", "categories", "groups", "forms", "sorts", "varieties",
            "compare", "contrast", "alternatives", "options", "versions", "models",
            "show me", "give me", "tell me all", "enumerate", "summarize"
        ]

        self.multi_wh_patterns = [
            r"\b(who are|what are|which are|where are|when are|how are)\b",
            r"\b(how many|give me all|show me all|name all|list all|find all)\b",
            r"\b(can you list|could you list|tell me the names of|show me the)\b",
            r"\b(different kinds of|different types of|various types of)\b",
            r"\b(examples of|instances of|cases of)\b",
            r"\b(both|either.*or|all.*that|any.*that)\b",
            r"\b(which\s+\w+s)\b",            # Which countries, planets
            r"\b(what\s+\w+s)\b",             # What rivers, benefits
            r"\b(name\s+\w+s)\b",             # Name planets, rivers
            r"\b(list\s+\w+s)\b",             # List databases
        ]

        # Time expressions (imply multiple possible items)
        self.time_indicators = [
            "today", "tomorrow", "yesterday", "this week", "next week",
            "this month", "next month", "this year", "next year"
        ]

        # Strong single indicators
        self.single_indicators = [
            r"\b(the\s+main|the\s+primary|the\s+most\s+important|the\s+best)\b",
            r"\b(who\s+is|what\s+is|which\s+is|where\s+is|when\s+is|how\s+is)\b",
            r"\b(only|just|single|one)\b"
        ]

        # Fixed universal lists that should always be multi-answer
        self.fixed_lists = [
            "planets", "continents", "days of the week", "months", 
            "periodic table elements", "oceans", "colors of the rainbow"
        ]

    def is_plural(self, query: str) -> bool:
        """Detects if the main noun is plural (quick heuristic)."""
        words = query.lower().split()
        return any(w.endswith("s") for w in words if len(w) > 3)

    def expects_multiple_answers(self, query: str) -> bool:
        """Return True if query expects multiple answers, else False."""
        q = query.lower().strip()

        # Fixed-list override → always multi
        for fixed in self.fixed_lists:
            if fixed in q:
                return True

        # If strong single indicator → return False
        if any(re.search(p, q) for p in self.single_indicators):
            return False

        # If query contains time expressions + plural noun → likely multiple
        if any(t in q for t in self.time_indicators) and self.is_plural(q):
            return True

        # "any X" where X is plural → multiple
        if re.search(r"\bany\s+\w+s\b", q):
            return True

        # Multi keywords or patterns → return True
        if any(kw in q for kw in self.multi_keywords):
            return True
        if any(re.search(p, q) for p in self.multi_wh_patterns):
            return True

        return False

    # def analyze_batch(self, queries: List[str]) -> Dict[str, bool]:
    #     return {q: self.expects_multiple_answers(q) for q in queries}




# ---- Test Cases ----
def run_tests():
    detector = MultiAnswerHeuristic()
    
    test_queries = [
        # --- Single-answer expected (False) ---
        "Who discovered radioactivity?",
        "What is the capital of France?",
        "Who is the CEO of Tesla?",
        "When was the first iPhone released?",
        "What is the main ingredient in bread?",
        "Which planet is closest to the Sun?",
        "What is the value of Pi up to 2 decimal places?",
        "Who wrote Hamlet?",
        "Which programming language is used for Android apps?",
        "What is the largest mammal on Earth?",
        "Name the primary advantage of using Python",
        
        # --- Multiple-answers expected (True) ---
        "List the scientists who contributed to quantum mechanics",
        "Which countries are in the EU?",
        "What are the top 5 movies of 2023?",
        "Give me examples of programming languages",
        "Tell me about different types of databases",
        "What are the benefits of regular exercise?",
        "Name the planets in the solar system",
        "Show me all prime numbers under 20",
        "What are the disadvantages of fossil fuels?",
        "List the rivers in India",
        "What are the components of a computer system?",
        "Tell me the names of World War II allies",
        "What are some uses of artificial intelligence?",
        "List both options for file storage",
        "Give 3 examples of renewable energy sources",
        "What are the first 5 elements of the periodic table?",
        "is there any mettings today"
    ]
    
    print("=== Multi-Answer Detection (Robust Version) ===\n")
    # results = detector.analyze_batch(test_queries)
    # for q, ans in results.items():
    #     print(f"{q} → {ans}")

if __name__ == "__main__":
    run_tests()
