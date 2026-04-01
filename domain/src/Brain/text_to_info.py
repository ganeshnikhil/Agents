from langchain_ollama import ChatOllama
from ..FUNCTION.Tools.get_env import EnvManager

class AIResponder:
    def __init__(self, model_name=None):
        self.model = model_name or EnvManager.load_variable("Text_to_info_model")
        self.temperature = 0.3

    def ai_response(self, prompt: str, max_token: int = 2000) -> str:
        """Handle creative prompts like jokes or stories."""
        try:
            llm = ChatOllama(
                model=self.model,
                temperature=self.temperature,
                max_token=max_token
            )

            messages = [
                {"role": "system", "content": "You are an intelligent AI system. Understand the user Query carefully and provide the most relevant Answer."},
                {"role": "user", "content": str(prompt)}
            ]

            response = llm.invoke(messages)
            return response.content

        except Exception as e:
            print(f"An error occurred: {e}")
            return "Error occurred while processing your request."

def send_to_ai(prompt):
    AI = AIResponder()
    return AI.ai_response(prompt)

# Usage Example:
# ai_responder = AIResponder()
# result = ai_responder.send_to_ai("Tell me a joke.")
# print(result)
