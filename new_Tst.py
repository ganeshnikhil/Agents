# from backend.app.core.twin import ShortTermMemory

# stm = ShortTermMemory(
#     filepath="./data/memory_store/shorterm/short_term.json",
#     max_entries=50,
#     auto_save=True,
#     session_timeout_hours=24
# )


# ans = stm.search("is there any metting today at 4pm",k=3)
# print(ans)

import os 
from domain.src.Agents.update_agent import RobustAgent
from domain.src.prompts.system_prompts import SYSTEM_PROMPT
from domain.src.FUNCTION.run_function import function_map
from data.tools import CURRENT_ALL_FUNCTIONS


def test_robust_agent(query: str):
    """
    Standalone function to test RobustAgent only.
    Initializes all required dependencies internally
    and runs a single query.
    """

    # --- Models ---
    agentic_non_reasoning_model = "gemma3:4b"
    reasoning_model = "qwen3:4b"
    embedding_model = "nomic-embed-text:latest"

    # --- Paths ---
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    print(PROJECT_ROOT)
    def project_path(*paths):
        return os.path.join(PROJECT_ROOT, *paths)
    
    tools_policy_path = os.path.abspath(
    os.path.join(PROJECT_ROOT, "data/tools_policy/tool_freq.json"))
    
    print(tools_policy_path)
    # --- Initialize RobustAgent ---
    agent = RobustAgent(
        llm_model_name= agentic_non_reasoning_model,
        reason_model_name=reasoning_model,
        embd_model_name=embedding_model,
        tools=function_map,
        tool_schema=CURRENT_ALL_FUNCTIONS,
        sys_prompt=SYSTEM_PROMPT,
        freq_path=tools_policy_path
    )

    # --- Run query ---
    try:
        response = agent.run(query)
        return response
    except Exception as e:
        return f"RobustAgent Error: {e}"


if __name__ == "__main__":
    result = test_robust_agent("Open YouTube and then open GitHub.")
    print(result)
