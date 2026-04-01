import torch  # used
import re     # used
import json   # used
import ollama # used
from typing import Dict, Any, List # used
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM # used
# Prefer relative import when used as a package, but fall back to direct import
try:
    from .selection_policy import ToolSelector  # type: ignore
except Exception:
    from selection_policy import ToolSelector 
from json_repair import repair_json


# =========================
# Response Parsing
# =========================
class ResponseParser:
    @staticmethod
    def _log_repair(original: str, repaired: str):
        """Helper to track what the parser is fixing in the background."""
        if original.strip() != repaired.strip():
            print("\n[DEBUG] 🛠️ JSON Repair Triggered:")
            print(f"  RAW: {original[:100]}...") # Print first 100 chars
            print(f"  FIXED: {repaired[:100]}...")
            print("-" * 30)
    
    @staticmethod
    def extract_balanced_json(text: str) -> str | None:
        start = text.find("{")
        if start == -1:
            return None

        brace_count = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    return text[start:i + 1]

        return None

    @staticmethod
    def extract_thought(response: str) -> str:
        patterns = [
            r"```Thought\n(.*?)```",
            r"```thought\n(.*?)```",
            r"###\s*Thought\s*\n(.*?)(?=###|Action|```|$)",
            r"\[THOUGHT\]\s*(.*?)(?=\[|```|$)",
            r"Thought:\s*(.*?)(?=Action|Final Answer|```|$)",
        ]
        for p in patterns:
            m = re.search(p, response, re.DOTALL | re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return ""
    
    
    @staticmethod
    def extract_action(text: str):
        if not text:
            return None

        # 🔍 Locate Action section
        m = re.search(r"\bAction\b", text, re.IGNORECASE)

        search_region = text[m.end():] if m else text

        # ✅ Extract balanced JSON ONLY from action region
        json_block = ResponseParser.extract_balanced_json(search_region)
        if not json_block:
            return None

        # 🛠 Repair JSON
        repaired_str = repair_json(json_block)
        ResponseParser._log_repair(json_block, repaired_str)

        try:
            obj = json.loads(repaired_str)
            if isinstance(obj, dict) and "name" in obj:
                return obj
        except Exception as e:
            print(f"[ERROR] Action JSON parsing failed: {e}")

        return None
    
    
    # @staticmethod
    # def extract_result(response: str):
    #     if not response:
    #         return None

    #     # Primary: explicit Result block (what the prompt enforces)
    #     m = re.search(
    #         r"```Result\s*\n(.*?)```",
    #         response,
    #         re.DOTALL | re.IGNORECASE
    #     )
    #     if m:
    #         return m.group(1).strip()

    #     # Fallback: no reliable structure → return everything
    #     # (better wrong format than lost meaning)
    #     return response.strip()

    @staticmethod
    def extract_result(response: str):
        patterns = [
            r"```Result\n(.*?)```",
            r"Final Answer:\s*(.*?)(?=```|$)",
            r"\[FINAL ANSWER\]\s*(.*?)(?=\[|$)",
            r"###\s*Final Answer\s*\n(.*)",
        ]
        for p in patterns:
            m = re.search(p, response, re.DOTALL | re.IGNORECASE)
            if m:
                return m.group(1).strip()
        
        if "Final Answer:" in response:
            return response.split("Final Answer:")[-1].strip()
        return None

    @staticmethod
    def flag_json_parser(raw_output: str) -> dict:
        try:
            # ✅ Use balanced JSON extraction
            json_block = ResponseParser.extract_balanced_json(raw_output)
            if not json_block:
                return {"flag": False}

            # ✅ Repair JSON (LLM-safe)
            repaired_str = repair_json(json_block)

            # Optional debug logging (safe to keep)
            ResponseParser._log_repair(json_block, repaired_str)

            obj = json.loads(repaired_str)

            if isinstance(obj, dict) and "flag" in obj:
                val = obj["flag"]
                if isinstance(val, str):
                    return {"flag": val.lower() == "true"}
                return {"flag": bool(val)}

        except Exception as e:
            print(f"[ERROR] flag_json_parser failed: {e}")

        return {"flag": False}


# =========================
# Memory
# =========================
class MemoryManager:
    def __init__(self, summarizer_model="sshleifer/distilbart-cnn-12-6", min_length = 20, summarize_every: int = 10):
        self.history: List[Dict[str, Any]] = []
        self.reflexion: List[str] = []
        self.summaries: List[str] = []
        self.summarize_every = summarize_every
        self.model_name = summarizer_model
        # Lazy/protected loading: model may be large or unavailable in some envs
        self.tokenizer = None
        self.model = None
        self.device = self.get_cuda_device()
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name).to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"[WARN] Could not load summarization model '{self.model_name}': {e}")
            self.tokenizer = None
            self.model = None
        self.RAW_CONTEXT_STEPS = 3
        self.MAX_SUMMARIES = 5
        # ✅ ADD THIS
        self.total_steps = 0
        self.min_length = min_length

    
    def get_cuda_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"



    def add_step(self, thought, action, observation):
        self.history.append({
            "thought": thought,
            "action": action,
            "observation": observation
        })
        self.total_steps += 1
        if self.total_steps % self.summarize_every == 0:
            self.summarize_history(force=True)

    def add_reflexion(self, note: str):
        self.reflexion.append(note)
        if len(self.reflexion) > 3:
            self.reflexion.pop(0)

    def prepend_reflexion(self) -> str:
        if not self.reflexion:
            return ""
        return "Previous mistakes to avoid:\n" + "\n".join(
            f"- {r}" for r in self.reflexion
        ) + "\n\n"

    def prepend_summaries(self) -> str:
        if not self.summaries:
            return ""
        return "Previous summary:\n" + "\n".join(self.summaries) + "\n\n"

    
    def summarize(self, text: str) -> str:
        
        
        if not self.model or not self.tokenizer or len(text) < 40:
            return text
        
        input_text = text
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=1024
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        input_len = inputs["input_ids"].shape[1]

        min_len = min(self.min_length, max(10, input_len // 6))
        max_length = min(max(32, input_len // 2), 128)

        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs["input_ids"],
                min_length=min_len,
                max_length=max_length,
                num_beams=4,
                early_stopping=True
            )

        return self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        ).strip()

    def summarize_history(self, mode="combined" , force=False):
        """
        mode:
        - 'per_step' : summarize each (thought, action, observation) separately
        - 'combined' : summarize all old steps together
        """
        
        if not force and len(self.history) <= self.RAW_CONTEXT_STEPS:
            return


        old = self.history[:-self.RAW_CONTEXT_STEPS]
        recent = self.history[-self.RAW_CONTEXT_STEPS:]

        summaries = []

        if mode == "per_step":
            # 🔹 Summarize each step independently
            for i, mem in enumerate(old, 1):
                
                if not any(mem.get(k) for k in ("thought", "action", "observation")):
                    continue

                text = (
                    "Summarize this agent step concisely.\n"
                    f"Thought: {mem.get('thought', '')}\n"
                    f"Action: {mem.get('action', '')}\n"
                    f"Observation: {mem.get('observation', '')}\n"
                )
                
                compressed_content = self.summarize(text)

                summaries.append({
                    "type": "step_summary",
                    "step": i,
                    "content": compressed_content.strip()
                })

        elif mode == "combined":
            # 🔹 Summarize all steps together
            text = "Summarize the following agent history concisely:\n\n"

            for i, mem in enumerate(old, 1):
                
                if not any(mem.get(k) for k in ("thought", "action", "observation")):
                    continue
                text += (
                    f"Step {i}:\n"
                    f"Thought: {mem.get('thought', '')}\n"
                    f"Action: {mem.get('action', '')}\n"
                    f"Observation: {mem.get('observation', '')}\n\n"
                )
            
            compressed_content = self.summarize(text)
            summaries.append({
                "type": "combined_summary",
                "content": compressed_content.strip()
            })

        else:
            raise ValueError("mode must be 'per_step' or 'combined'")

        # Store summaries
        self.summaries.extend(s["content"] for s in summaries)

        # 🔒 Cap summaries to avoid context explosion
        self.summaries = self.summaries[-self.MAX_SUMMARIES:]

        # Keep only recent history
        self.history = recent



    def build_context(self) -> str:
        ctx = self.prepend_reflexion() + self.prepend_summaries()
        for h in self.history[-self.RAW_CONTEXT_STEPS:]:
            if h.get("thought"):
                ctx += f"Thought:\n{h['thought']}\n"
            if h.get("action"):
                ctx += f"Action:\n{json.dumps(h['action'])}\n"
            if h.get("observation"):
                ctx += f"Observation:\n{h['observation']}\n"
        return ctx


# =========================
# Tool Execution
# =========================

class ToolExecutor:
    def __init__(self, tools: Dict[str, Any], tool_schema: List[Dict[str, Any]], selector: ToolSelector):
        self.tools = tools
        self.schema = {t["name"]: t for t in tool_schema}
        self.selector = selector
        self.executed = set()

    def validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        if "name" not in action:
            raise ValueError("Action missing 'name'")

        tool_name = action["name"]
        args = action.get("arguments", {})

        if tool_name not in self.schema:
            raise ValueError(f"Unknown tool: {tool_name}")

        expected_args = self.schema[tool_name]["arguments"]

        def convert_type(value, v_type):
            v_type = v_type.strip().lower()
            value_str = str(value).strip()

            if v_type in ("string", "str"):
                return value_str
            if v_type in ("int", "integer"):
                m = re.search(r"-?\d+", value_str)
                if not m:
                    raise ValueError("Expected int")
                return int(m.group())
            if v_type == "float":
                m = re.search(r"-?\d+(?:\.\d+)?", value_str)
                if not m:
                    raise ValueError("Expected float")
                return float(m.group())
            if v_type == "bool":
                if value_str.lower() in ("true", "1", "yes"):
                    return True
                if value_str.lower() in ("false", "0", "no"):
                    return False
                raise ValueError("Expected bool")

            raise ValueError(f"Unknown type '{v_type}'")

        clean_args = {}
        for k, v_type in expected_args.items():
            if k not in args:
                raise ValueError(f"Missing argument '{k}' for tool '{tool_name}'")
            clean_args[k] = convert_type(args[k], v_type)

        extra = set(args) - set(expected_args)
        if extra:
            print(f"[Warning] Ignoring unexpected arguments for {tool_name}: {extra}")

        return {
            "name": tool_name,
            "arguments": clean_args
        }
        
        
    def execute_tool(self, action: Dict[str, Any]) -> Dict[str, Any]:

        if not isinstance(action, dict):
            raise ValueError("Action must be a dict")

        clean_action = self.validate_action(action)

        dedup_key = (
            clean_action["name"],
            json.dumps(clean_action["arguments"], sort_keys=True)
        )

        if dedup_key in self.executed:
            raise ValueError(f"Duplicate tool call: {dedup_key}")

        self.executed.add(dedup_key)

        try:
            if clean_action["name"] not in self.tools:
                raise ValueError("Tool not implemented")

            result = self.tools[clean_action["name"]](**clean_action["arguments"])
        except Exception as e:
            raise ValueError(f"Tool execution failed: {e}")

        self.selector.update_frequency(clean_action["name"])

        return {
            "action": clean_action,
            "observation": str(result)
        }


# =========================
# Verification
# =========================
class Verifier:
    def __init__(self, reason_model_name: str):
        self.reason_model_name = reason_model_name

    def critic_check(self, observation):
        if not observation or "error" in str(observation).lower():
            return {"verdict": "retry", "reason": "Tool execution failed"}
        return {"verdict": "continue"}
    
    
    
    def build_tool_summary(self, history) -> str:
        """
        Create a concise factual summary of tool usage for verification.
        """
        if not history:
            return "No tools were used."

        lines = []
        for i, step in enumerate(history, 1):
            action = step.get("action")
            observation = step.get("observation")

            if action:
                name = action.get("name", "unknown_tool")
                args = action.get("arguments", {})
                obs = observation if observation else "No observation"

                lines.append(
                    f"- {name} : {obs}"
                )

        return "\n".join(lines) if lines else "No tools were used."

    def verify(self, task, history, output):

        used_tool = any(step.get("action") for step in history)
        success = any(
            step.get("observation") and "error" not in str(step["observation"]).lower()
            for step in history
        )

        if used_tool and not success:
            return False
        
        tool_summary = self.build_tool_summary(history)

        prompt = f"""
You are a STRICT COMPLETENESS CHECKER.

Your job is NOT to judge accuracy, quality, or reasoning.

ONLY verify whether ALL REQUIRED METRICS for the task
were OBTAINED EITHER:
- via tool execution, OR
- stated in the final output.

USER TASK:
{task}

TOOL EXECUTION SUMMARY (FACTUAL, AUTHORITATIVE):
{tool_summary}

AGENT'S FINAL OUTPUT:
{output}

COMPLETENESS RULES:
- If a required metric appears in TOOL EXECUTION SUMMARY,
  it is considered SATISFIED even if not repeated in the final output.
- Do NOT judge correctness or usefulness.
- Do NOT penalize missing explanations or comparisons.
- Only check presence of required metrics.

Return STRICT JSON ONLY:
```json
{{
  "flag": true or false
}}
"""
        response = ollama.chat(
            model=self.reason_model_name,
            messages=[
                {"role": "system", "content": "You are a fair evaluator. Judge if the work adequately addresses the task."},
                {"role": "user", "content":prompt}
            ],
            options={"temperature": 0.0}
        )
        
        flag = ResponseParser.flag_json_parser(response["message"]["content"])
        return str(flag.get("flag")).lower() == "true"


# =========================
# Agent
# =========================
class RobustAgent:
    def __init__(
        self,
        llm_model_name,
        reason_model_name,
        embd_model_name,
        tools,
        tool_schema,
        sys_prompt,
        freq_path,
        summarizer_model_name = "facebook/bart-large-cnn"
    ):
        self.llm_model_name = llm_model_name
        self.summarizer_model_name = summarizer_model_name
        self.sys_prompt = sys_prompt
        self.parser = ResponseParser()
        self.memory = MemoryManager(summarizer_model_name)
        self.verifier = Verifier(reason_model_name)

        self.tool_selector = ToolSelector(
            tools_schema=tool_schema,
            embd_model_name=embd_model_name,
            freq_path=freq_path,
        )
        self.executor = ToolExecutor(tools, tool_schema, self.tool_selector)

    def run(self, task, max_steps=10, max_retries=3):
        
        self.memory.total_steps = 0  # new task
        for retry in range(max_retries):
            print(f"[RETRY {retry + 1}]")
            self.executor.executed.clear()
            self.memory.history.clear()
            
            if retry == 0:
                self.memory.reflexion.clear()
                self.memory.summaries.clear()

            # self.memory.reflexion.clear()
            # self.memory.summaries.clear()

            tools = self.tool_selector.select_tools(
                task, policy="hybrid" if retry == 0 else "embedding"
            )

            for step in range(max_steps):
                
                prompt = (
                    self.memory.build_context()
                    + f"\nUSER TASK:\n{task}\n"
                )
                
                try:
                    response = ollama.chat(
                        model=self.llm_model_name,
                        messages=[
                            {"role": "system", "content": self.sys_prompt.format(tool_map=tools)},
                            {"role": "user", "content": prompt},
                        ],
                        options={"temperature": 0.0},
                    )
                    
                    
                    text = response["message"]["content"]
                    
                    
                    thought = self.parser.extract_thought(text)
                    action = self.parser.extract_action(text)
                    
                except Exception as e:
                    self.memory.add_reflexion(f"LLM failure: {e}")
                    break
                
                
                if action:
                    print(f"ACTION\n{action}")
                    try:
                        action_result = self.executor.execute_tool(action)
                        clean_action = action_result["action"]
                        obs = action_result["observation"]
                        print(f"OBSERVATION\n{obs}")
                    except ValueError as e:
                        self.memory.add_step(
                            thought,
                            action,
                            f"Tool execution failed: {e}"
                        )
                        self.memory.add_reflexion(str(e))
                        continue

                    self.memory.add_step(thought, clean_action, obs)
                    verdict = self.verifier.critic_check(obs)
                    if verdict["verdict"] == "retry":
                        self.memory.add_reflexion(verdict["reason"])
                        continue
                else:
                    self.memory.add_step(thought, None, "No tool used")

                final = self.parser.extract_result(text)
                
                
                if final:
                    print(f"FINAL\n{final}")
                    if self.verifier.verify(task, self.memory.history, final):
                        self.tool_selector.save()
                        print(f"Result verified successfully")
                        return final
                    self.tool_selector.expand_embedding_budget()
                    break

        return None






# --- Disaster Tools (Dummy Functions) ---
def predict_earthquake(region: str):
    # dummy function - returns fake probability
    return f"Predicted earthquake chance in {region}: 12%"

def flood_alert(city: str):
    # dummy function - returns dummy alert level
    return f"Flood alert for {city}: MODERATE"

def wildfire_risk(area: str):
    # dummy function - returns dummy risk score
    return f"Wildfire risk in {area}: HIGH"

def cyclone_path(name: str):
    # dummy function - returns fake cyclone path
    return f"Cyclone {name} expected path: Ocean → Coast → Inland"

def drought_index(state: str):
    # dummy function - returns dummy drought index
    return f"Drought index for {state}: 45 (Moderate Drought)"

# Tool registry
tools = {
    "predict_earthquake": predict_earthquake,
    "flood_alert": flood_alert,
    "wildfire_risk": wildfire_risk,
    "cyclone_path": cyclone_path,
    "drought_index": drought_index
}

# Tool map (meta info)
tool_map = [
    {"name":"predict_earthquake","description":"predict earthquake probability in a region","arguments":{"region":"STRING"}},
    {"name":"flood_alert","description":"check flood alert level for a city","arguments":{"city":"STRING"}},
    {"name":"wildfire_risk","description":"assess wildfire risk in an area","arguments":{"area":"STRING"}},
    {"name":"cyclone_path","description":"predict cyclone movement path","arguments":{"name":"STRING"}},
    {"name":"drought_index","description":"get drought index for a state","arguments":{"state":"STRING"}}
]





SYSTEM_PROMPT = """
You are an AI agent specializing in Disaster Management.  
Your job is to analyze disaster-related queries using Available tools.  

### Reasoning Loop
Follow this sequence:

1. Thought:Explain your reasoning and explicitly choose which tool is needed next.
   - If all required data is already collected → skip Action and proceed immediately to Result block.  
   - Only describe reasoning here, do NOT call any tool.  

2. Action (optional): Only call a tool if you **do not yet have the data you need**.  
   - Output a JSON_BLOB with a SINGLE tool call.  
   - Use only the tools listed in TOOLS.  
   - Wrap the JSON_BLOB in triple backticks.  

3. Observation: After each Action, you will receive the exact tool output. Use it in your next Thought.  

Repeat Thought → optional Action → Observation → Thought ... until all required information is collected.  
Once all reasoning is complete → skip Action entirely → output Result immediately.  

---

### CRITICAL RULES
- Tools are ONLY for retrieving raw disaster data.  
- Never use tools for reasoning, comparison, or summarization — do these in Thought/Result.  
- Do NOT call the same tool twice for the same input; reuse Observations.  
- If tool output is empty, malformed, or unusable, do not retry. Move to final Result with what you have.  
- The final result must be wrapped exactly in a ```Result``` block. No extra text.  

---

### AVAILABLE TOOLS
{tool_map}

---

### OUTPUT FORMAT (Strict):  

```Thought
<your reasoning in natural language>
```

```Action
{{
  "name": "<tool_name>",
  "arguments": {{
    "<argument-name>": "<value>"
  }}
}}
```

OR when task is complete , provide final answer:

```Result
<your final natural language answer summarizing all results> 
```
"""




# SYSTEM_PROMPT = f"""
# You are an AI agent specializing in Tool calls.  
# Your job is to analyze user queries and use the Available tools when needed.

# ### Reasoning Loop
# Follow this sequence:

# 1. Thought:Explain your reasoning and explicitly choose which tool is needed next.
#    - If all required data is already collected → skip Action and proceed immediately to Result block.  
#    - Only describe reasoning here, do NOT call any tool.  

# 2. Action (optional): Take an Action only if you do not yet have the data you need.  
#    - Output a Action block with a SINGLE tool call.  
#    - Use only the tools listed in TOOLS.  
#    - Wrap the JSON_BLOB in triple backticks.  

# 3. **Observation:**  
#    After each Action, you will receive the **exact tool output** (called the Observation).  
#    In your next Thought:
#    - Use the Observation to decide the next step.  
#    - If the Observation clearly shows that the **task goal is achieved** (contains terms such as “completed”, “done”, “successful”, “ready”, or “opened and running”),  
#      → **immediately output a single Result block and stop.**  
#    - If more steps are needed, continue with another Thought (and optionally one more Action).  
#    - Never repeat the same Action for the same input.  

# Repeat Thought → optional Action → Observation → Thought ... until all required information is collected.  
# Once all reasoning is complete → skip Action entirely → output Result immediately.  

# ---

# ### CRITICAL RULES
# - If an Observation shows completion, you must stop and output Result immediately.
# - Never use tools for reasoning, comparison, or summarization — do these in Thought/Result.  
# - Do NOT call the same tool twice for the same input; reuse Observations instead.  
# - If tool output is empty, malformed, or unusable, do not retry. Move to final Result with what you have.  
# - The final result must be wrapped exactly in a ```Result``` block. No extra text.  

# ---

# ### AVAILABLE TOOLS
# {tool_map}

# ---

# ### OUTPUT FORMAT (Strict):  

# ```Thought
# <your reasoning in natural language>
# ```

# ```Action
# {{
#   "name": "<tool_name>",
#   "arguments": {{
#     "<argument-name>": "<value>"
#   }}
# }}
# ```

# OR when task is complete , provide final answer:

# ```Result
# <your final natural language answer summarizing all results> 
# ```
# """


# --- Test ---
def test():
    freq_path = "/Users/ganeshnikhil/Memory-Twin/data/tools_policy/tool_freq.json"

    agent = RobustAgent(
        llm_model_name="gemma3:4b",
        reason_model_name="qwen3:4b",
        embd_model_name="nomic-embed-text",
        tools=tools,
        tool_schema=tool_map,
        sys_prompt=SYSTEM_PROMPT,
        freq_path=freq_path
    )

    question = (
        "Check the earthquake probability in Tokyo, "
        "the flood alert in Mumbai, "
        "and then tell me which city faces the higher immediate disaster risk."
    )

    print(f"\n=== TESTING ===\n{question}\n")
    result = agent.run(question)

    print("\n=== FINAL RESULT ===")
    print(result)


if __name__ == "__main__":
    test()


# # --- Test ---
# def test():
#     freq_path = "/Users/ganeshnikhil/Memory-Twin/data/tools_policy/tool_freq.json"
#     agent = RobustAgent("gemma3:4b","qwen3:4b","nomic-embed-text", tools, tool_map, SYSTEM_PROMPT , freq_path)
#     question = "Check the earthquake probability in Tokyo, the flood alert in Mumbai, and then tell me which city faces the higher immediate disaster risk."
#     print(f"\n=== TESTING: {question} ===")
#     result = agent.run(question)
#     print(f"\n[RESULT] {result}")

# if __name__ == "__main__":
#     test()
