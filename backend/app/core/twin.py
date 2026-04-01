import logging
from domain.src.memory.short_term import ShortTermMemory
from domain.src.memory.long_term import LongTermMemory
from domain.src.memory.working_memory import WorkingMemory
from domain.src.Brain.one_many import MultiAnswerHeuristic
from domain.src.Brain.re_ranker import QwenReranker , RERANKER
from domain.src.Brain.main_router import Hippocampus
from domain.src.Agents.update_agent import RobustAgent
import ollama
from datetime import datetime 
import os 
from typing import Union, Dict, Any, List
from data.tools import CURRENT_ALL_FUNCTIONS
from domain.src.FUNCTION.run_function import function_map
from domain.src.prompts.system_prompts import SYSTEM_PROMPT

#uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
# ========================
# Logging Configuration
# ========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ========================
# Label Definitions
# ========================
ATTENTION_LABELS = ["memory_in", "memory_out", "cur"]
MEMORY_LABELS = ["STM", "LTM", "none"]
ANSWER_LABELS = ["single", "multiple", "none"]

# ========================
# Main Class
# ========================


import os

# Get the project root dynamically
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

def project_path(*paths):
    """Return an absolute path relative to project root."""
    return os.path.join(PROJECT_ROOT, *paths)


class DigitalTwin:
    def __init__(
        self,
        model_path: str = "./data/Models/multi_task_model_with_emotion",
        agentic_non_reasoning_model: str = "gemma3:4b",
        reasoning_model: str = "qwen3:4b",
        non_reasoning_model = "granite4:3b",
        Embeeding_model = "nomic-embed-text:latest",
        tools_policy_path = "./data/tools_policy/tool_freq.json",
        freq_path: str = "./data/frequency_lists",
        temperature: float = 0.0
    ):
        """Initialize the DigitalTwin with memory subsystems and model routing."""
        self.agentic_non_reasoning_model = agentic_non_reasoning_model
        self.non_reasoning_model = non_reasoning_model
        self.reasoning_model = reasoning_model
        self.Embeeding_model = Embeeding_model
        self.temperature = temperature
        self.freq_path = tools_policy_path

        self.Agent = RobustAgent(self.agentic_non_reasoning_model, self.reasoning_model, self.Embeeding_model,function_map,CURRENT_ALL_FUNCTIONS,SYSTEM_PROMPT,project_path(self.freq_path))
        # Initialize core components
        self.router = Hippocampus(project_path("data/Models/multi_task_model_with_emotion"))
        self.Rernaker = RERANKER()

        # Ensure directories exist
        os.makedirs("./data/memory_store/shorterm", exist_ok=True)
        os.makedirs("./data/memory_store/working", exist_ok=True)
        self.stm_path = os.path.abspath("./data/memory_store/shorterm/short_term.json")
        self.stm = ShortTermMemory(
            filepath=project_path("data/memory_store/shorterm/short_term.json"),
            max_entries=50,
            auto_save=True,
            session_timeout_hours=24
        )

        self.ltm = LongTermMemory()

        self.working_memory = WorkingMemory(
            file_path=project_path("data/memory_store/working/working_memory.json")
        )

    # ========================
    # Helper Functions
    # ========================
    
    def get_emotion_dict(self , msg):
        return self.router.get_emotion_vector(msg)
    
    
    def _generate_timestamp_id(self) -> str:
        """Generate a unique timestamp-based ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

    def _extract_ollama_response(self, response: Any) -> str:
        """Safely extract response text from Ollama output."""
        if hasattr(response, "response"):
            return response.response
        elif isinstance(response, dict) and "response" in response:
            return response["response"]
        return str(response)
    
    def delete_ltm_memories(self):
        self.ltm.delete_all_memories()
        
    # ========================
    # Memory Operations
    # ========================
    def memory_in_response(self, user: str) -> Union[str, Dict[str, str]]:
        """Generate a reformulated memory entry for a given user query."""
        try:
            response = ollama.generate(
                model=self.non_reasoning_model,
                prompt=(
                    f"You have memory storage capability. "
                    f"Do not give suggestions or instructions. "
                    f"Simply rewrite this query meaningfully in under 30 words: {user}"
                ),
                options={"temperature": self.temperature, "num_predict": 50}
            )
            return self._extract_ollama_response(response)
        except Exception as e:
            logger.error(f"Error in memory_in_response: {e}")
            return {"error": str(e)}

    def memory_out_response(self, user: str, result: List[Any], num_predict: int = 200) -> str:
        """Generate a meaningful answer using retrieved memory context."""
        if not result:
            return "I couldn't find relevant information in memory for this query."

        try:
            context = "\n".join(str(r) for r in result)
            prompt = (
                f"You have access to the following memory context:\n{context}\n\n"
                f"Using only this context, answer the query below clearly and meaningfully.\n"
                f"Query: {user}\nAnswer:"
            )

            response = ollama.generate(
                model=self.non_reasoning_model,
                prompt=prompt,
                options={"temperature": self.temperature, "num_predict": num_predict}
            )

            return self._extract_ollama_response(response)

        except Exception as e:
            logger.error(f"Error in memory_out_response: {e}")
            return f"[Error generating memory_out response: {e}]"

    def cur_response(self, user: str) -> Union[str, Dict[str, str]]:
        """Process a direct query without using memory."""
        try:
            response = self.Agent.run(user)
            if response:
                return response
            else:
                return "Done"
        except Exception as e:
            return f"Error :  {e}"
        

    # ========================
    # Query Processing
    # ========================
    def process_query(self, user: str, agent: str) -> Dict[str, Any]:
        """
        Main orchestration function that routes the query to appropriate memory operations.
        Returns a structured response dict.
        """
        timestamp_id = self._generate_timestamp_id()

        try:
            # Route memory using hippocampus
            mem_in_out, mem_type, single_multi = self.router.route_memory(user)
            logger.info(f"Routing → Operation: {mem_in_out}, Memory: {mem_type}, Answer Type: {single_multi}")

            response_text = ""

            # --- Memory In ---
            if mem_in_out == "memory_in":
                response_text = self.memory_in_response(user)
                memory_entry = {
                    "timestamp_id": timestamp_id,
                    "agent": agent,
                    "user": user,
                    "assistant": str(response_text)
                }

                if mem_type == "STM":
                    self.stm.add(memory_entry)
                elif mem_type == "LTM":
                    self.ltm.add_memory_with_similarity_check(memory_entry)

            # --- Memory Out ---
            elif mem_in_out == "memory_out":
                if mem_type == "STM":
                    results = self.stm.search(user, k=5)
                elif mem_type == "LTM":
                    results = self.ltm.search_memory(user, limit=5)
                else:
                    results = []

                if single_multi == "single" and results:
                    try:
                        best_doc, _ = self.Rernaker.reranker(user, results)
                        results = [best_doc] if best_doc else []
                    except Exception as e:
                        logger.warning(f"Reranker failed: {e}")

                response_text = self.memory_out_response(user, results)

            # --- Direct Current Query ---
            elif mem_in_out == "cur":
                response_text = self.cur_response(user)

            else:
                logger.error(f"Unknown operation detected: {mem_in_out}, {mem_type}, {single_multi}")
                response_text = "Unrecognized operation type."

            # --- Save to Working Memory ---
            self.working_memory.write({
                "timestamp_id": timestamp_id,
                "agent": agent,
                "user": user,
                "assistant": str(response_text)
            })

            # ✅ Return in unified structured format
            return {
                "status": "success",
                "operation": mem_in_out,
                "memory_type": mem_type,
                "answer":single_multi,
                "response": str(response_text),
                "timestamp_id": timestamp_id
            }

        except Exception as e:
            logger.error(f"Error in process_query: {e}")
            return {
                "status": "error",
                "operation": "unknown",
                "memory_type": "unknown",
                "answer":"unknown",
                "response": f"[Error: {e}]",
                "timestamp_id": timestamp_id
            }





# #---------------------------------------------

# class CognitiveDigitalTwin:
#     def __init__(self, non_reasoning_model="gemma3:4b", reasoning_model="qwen3:4b", temperature=0):
#         self.non_reasoning_model = non_reasoning_model
#         self.reasoning_model = reasoning_model
#         self.temperature = temperature

#         # Memory routers
#         self.mem_in_out = AnteriorCingulateCortex(
#             model=non_reasoning_model,
#             temperature=temperature,
#             prompt_path="./src/prompts/memory_prompts/mem_in_out.txt"
#         )
#         self.single_multi = MultiAnswerHeuristic()
#         self.Reranker = QwenReranker()
#         self.hippocampus_in = Hippocampus(
#             model=non_reasoning_model,
#             temperature=temperature,
#             prompt_path="./src/prompts/memory_prompts/memory_in.txt"
#         )
#         self.hippocampus_out = Hippocampus(
#             model=non_reasoning_model,
#             temperature=temperature,
#             prompt_path="./src/prompts/memory_prompts/memory_out.txt"
#         )

#         # Memory storage
#         self.stm = ShortTermMemory(
#             filepath="./data/memory_store/shorterm/short_term.json",
#             max_entries=50,
#             auto_save=True,
#             session_timeout_hours=24
#         )
#         self.ltm = LongTermMemory()
#         self.working_memory = WorkingMemory(
#             file_path="./data/memory_store/working/working_memory.json"
#         )

#     def _generate_timestamp_id(self) -> str:
#         return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

#     # ======================================================
#     # PROCESS QUERY (returns unified response)
#     # ======================================================
#     def process_query(self, user: str, agent: str):
#         response = {
#             "status": "error",
#             "operation": None,
#             "memory_type": None,
#             "response": None,
#             "timestamp_id": self._generate_timestamp_id(),
#         }

#         try:
#             decision = self.mem_in_out.gateway_router(user)
#             operation = decision.get("operation")
#             response["operation"] = operation

#             # --- MEMORY IN ---
#             if operation == "memory_in":
#                 mem_type = self.hippocampus_in.gateway_router(user).get("memory_type")
#                 rewritten = self.memory_in_response(user)

#                 entry = {
#                     "timestamp_id": response["timestamp_id"],
#                     "agent": agent,
#                     "user": user,
#                     "assistant": rewritten.get("response", rewritten),
#                 }

#                 if mem_type == "STM":
#                     self.stm.add(entry)
#                 elif mem_type == "LTM":
#                     self.ltm.add_memory_with_similarity_check(entry)

#                 response.update({
#                     "status": "success",
#                     "memory_type": mem_type,
#                     "response": f"Memory successfully stored in {mem_type}.",
#                 })

#             # --- MEMORY OUT ---
#             elif operation == "memory_out":
#                 mem_type = self.hippocampus_out.gateway_router(user).get("memory_type")

#                 if mem_type == "STM":
#                     results = self.stm.search(user, k=5)
#                 elif mem_type == "LTM":
#                     results = self.ltm.search_memory(user, limit=5)
#                 else:
#                     results = []

#                 if self.single_multi.expects_multiple_answers(user):
#                     #best_doc, _ = self.Reranker.rerank([(user, ans) for ans in results])
                    
#                     try:
#                         # Ensure text-only input
#                         text_results = [str(r) for r in results]
#                         best_doc, _ = self.Rernaker.reranker(user, text_results)
#                         results = [best_doc] if best_doc else []
#                     except Exception as e:
#                         logger.warning(f"Reranker failed: {e}")

#                     #results = [best_doc] if best_doc else []

#                 mem_out = self.memory_out_response(user, results)
#                 response.update({
#                     "status": "success",
#                     "memory_type": mem_type,
#                     "response": mem_out.get("response", mem_out),
#                 })

#             # --- CUR OPERATION (direct reasoning) ---
#             elif operation == "cur":
#                 cur = self.cur_response(user)
#                 response.update({
#                     "status": "success",
#                     "memory_type": None,
#                     "response": cur.get("response", cur),
#                 })

#             else:
#                 response.update({
#                     "status": "error",
#                     "response": "Unrecognized operation",
#                 })

#             # --- SAVE TO WORKING MEMORY ---
#             self.working_memory.write({
#                 "timestamp_id": response["timestamp_id"],
#                 "agent": agent,
#                 "user": user,
#                 "assistant": response["response"],
#             })

#         except Exception as e:
#             logger.error(f"Error in process_query: {e}")
#             response.update({
#                 "status": "error",
#                 "response": str(e),
#             })

#         return response

#     # ======================================================
#     # DIRECT RESPONSE METHODS (all return dict)
#     # ======================================================
#     def cur_response(self, user):
#         try:
#             result = ollama.generate(
#                 model=self.reasoning_model,
#                 prompt=user,
#                 options={"temperature": self.temperature},
#             )
#             text = result.response if hasattr(result, "response") else str(result)
#             return {"status": "success", "response": text}
#         except Exception as e:
#             logger.error(f"Error in cur_response: {e}")
#             return {"status": "error", "response": str(e)}

#     def memory_in_response(self, user):
#         try:
#             result = ollama.generate(
#                 model=self.non_reasoning_model,
#                 prompt=(
#                     "You have memory storage capability. "
#                     "Do not give suggestions or instructions. "
#                     f"Rewrite this query meaningfully in under 30 words: {user}"
#                 ),
#                 options={"temperature": self.temperature, "num_predict": 50},
#             )
#             text = result.response if hasattr(result, "response") else str(result)
#             return {"status": "success", "response": text}
#         except Exception as e:
#             logger.error(f"Error in memory_in_response: {e}")
#             return {"status": "error", "response": str(e)}

#     def memory_out_response(self, user, result, num_predict=200):
#         try:
#             prompt = (
#                 f"You have access to the following memory context:\n{result}\n\n"
#                 f"Using only this context, answer the query below clearly.\n"
#                 f"Query: {user}\n"
#                 f"Answer concisely and relevantly."
#             )

#             result = ollama.generate(
#                 model=self.non_reasoning_model,
#                 prompt=prompt,
#                 options={"temperature": self.temperature, "num_predict": num_predict},
#             )
#             text = result.response if hasattr(result, "response") else str(result)
#             return {"status": "success", "response": text}
#         except Exception as e:
#             logger.error(f"Error in memory_out_response: {e}")
#             return {"status": "error", "response": str(e)}




# def _generate_timestamp_id() -> str:
#     """Generate timestamp ID in the specified format."""
#     return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]



# if __name__ == "__main__":
#     #twin = CognitiveDigitalTwin()
    
#     twin = DigitalTwin()
    
#     # ---------- STM store ----------
#     # print("\n--- STM Store Test ---")
#     # stm_test_queries = [
#     #     "Remember my meeting at 2 PM",
#     #     "Remember my grocery list: milk, eggs, bread",
#     #     "Remember my favorite color is blue"
#     # ]
#     # for i, q in enumerate(stm_test_queries):
#     #     print(twin.process_query(q,"AssistantBot"))

#     # ---------- LTM store ----------
#     # print("\n--- LTM Store Test ---")
#     #twin.delete_ltm_memories()
#     ltm_test_queries = [
#         "My friends are Rohan and Hardik",
#         "I love playing chess on weekends",
#         "I want to learn Python and Machine Learning"
#     ]
#     for i, q in enumerate(ltm_test_queries):
#         print(twin.process_query(q, "AssistantBot"))

#     # # ---------- CUR computation (direct reasoning) ----------
#     # print("\n--- CUR Computation Test ---")
#     # cur_test_queries = [
#     #     "What is 25 * 47?",
#     #     "Who wrote Hamlet?",
#     #     "Convert 100 Celsius to Fahrenheit"
#     # ]
#     # for q in cur_test_queries:
#     #     ts_id = _generate_timestamp_id()
#     #     print(f"Query: {q}")
#     #     print(f"Answer: {twin.process_query(q, ts_id, 'AssistantBot')}\n")

#     # # ---------- STM retrieval ----------
#     # print("\n--- STM Retrieval Test ---")
#     # stm_retrieve_queries = [
#     #     "When is my meeting?",
#     #     "What is my grocery list?",
#     #     "What is my favorite color?"
#     # ]
#     # for q in stm_retrieve_queries:
#     #     ts_id = _generate_timestamp_id()
#     #     print(f"Query: {q}")
#     #     print(f"Answer: {twin.process_query(q, ts_id, 'AssistantBot')}\n")

#     # # ---------- LTM retrieval ----------
#     # print("\n--- LTM Retrieval Test ---")
#     # ltm_retrieve_queries = [
#     #     "Who are my friends?",
#     #     "What hobbies do I have?",
#     #     "What do I want to learn?"
#     # ]
#     # for q in ltm_retrieve_queries:
#     #     ts_id = _generate_timestamp_id()
#     #     print(f"Query: {q}")
#     #     print(f"Answer: {twin.process_query(q, ts_id, 'AssistantBot')}\n")

#     # # ---------- Multi-answer check + reranker ----------
#     # print("\n--- Multi-answer + Reranker Test ---")
#     # multi_queries = [
#     #     "List the scientists who contributed to quantum mechanics",
#     #     "Give examples of programming languages",
#     #     "What are the top 5 movies of 2023"
#     # ]
#     # for q in multi_queries:
#     #     ts_id = _generate_timestamp_id()
#     #     print(f"Query: {q}")
#     #     print(f"Answer: {twin.process_query(q, ts_id, 'AssistantBot')}\n")
