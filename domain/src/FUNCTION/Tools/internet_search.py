from ...Brain.text_to_info import send_to_ai
from duckduckgo_search import DDGS

class DuckGoSearch:
    def __init__(self, query: str):
        self.query = query

    def search_query(self) -> str:
        """Search the provided query on DuckDuckGo for quick information."""
        results = DDGS().text(self.query, max_results=3)
        results_body = [info.get("body", "").strip() for info in results if info.get("body")]
        full_result = "\n".join(results_body)
        
        return full_result

    def generate_answer(self, search_results: str) -> str:
        """Generate an answer based on search results using AI."""
        prompt = (
            "Analyze the following search results carefully and extract the most relevant information."
            "Provide a concise and accurate answer to the given query."
            "\n\n=== Search Results ===\n"
            f"{search_results}\n"
            "=====================\n"
            f"Query: {self.query}\n"
            "Your Response:"
        )
        answer = send_to_ai(prompt)
        return answer

    def execute_search(self) -> str:
        """Execute the DuckDuckGo search and get the response."""
        search_results = self.search_query()
        answer = self.generate_answer(search_results)
        return answer


def duckgo_search(query:str) -> str:
    duck_search = DuckGoSearch(query)
    answer = duck_search.execute_search()
    return answer
