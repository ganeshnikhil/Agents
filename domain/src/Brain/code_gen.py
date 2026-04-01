
import logging
import os
import pandas as pd
import re
from langchain_ollama import ChatOllama
from ..FUNCTION.Tools.get_env import EnvManager
from ..FUNCTION.Tools.code_exec import CodeExecutor
from google import genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)


class CodeRefactorAssistant:
    def __init__(self):
        self.genai_key = EnvManager.load_variable("genai_key")
        self.local_model = EnvManager.load_variable("Text_to_info_model")
        self.execute_code_with_dependencies = CodeExecutor()
    def provide_file_details(self, path: str) -> str:
        logger.info(f"Providing details for file: {path}")
        try:
            df = pd.read_csv(path)
            details = [
                f"File Path: {path}",
                f"File Size: {df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB",
                f"Shape (rows, columns): {df.shape}",
                f"Column Names: {df.columns.tolist()}",
                f"Data Types:\n{df.dtypes.to_string()}",
                f"First 5 rows:\n{df.head().to_string(index=False)}",
                f"Missing values:\n{df.isnull().sum().to_string()}",
                f"Summary statistics:\n{df.describe(include='all').to_string()}",
                f"Unique values per column:\n{df.nunique().to_string()}",
                f"Sample value types per column:\n{df.iloc[0].to_dict()}"
            ]
            return "\n\n".join(details)
        except FileNotFoundError:
            logger.error(f"File not found at path: {path}")
            return ""
        except Exception as e:
            logger.error(f"Error while processing file {path}: {e}", exc_info=True)
            return ""

    def extract_python_code(self, text):
        pattern = r"```python\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        logger.info("No Python code found in the text.")
        return ""

    def generate_refactor_prompt(self, code: str, error: str, file_description: str):
        return f"""
        You are an expert Python code refactor assistant. The user has provided code that generated an error during execution.

        File Description:
        {file_description}

        Code:
        {code}

        Error:
        {error}

        Instructions:
        - Analyze and refactor to resolve the issue.
        - Use pandas, numpy, matplotlib correctly.
        - Handle file-related errors.
        - Refactor to be functional and error-free."""

    def gem_refactor_code(self, code: str, file_path: str, max_attempts=3):
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Gemini refactor attempt {attempt}/{max_attempts}")

            if not code:
                return {"error": "No code provided for execution."}

            exec_info = self.execute_code_with_dependencies.execute_code(code)
            if not exec_info.get("error"):
                logger.info("Code executed successfully.")
                return exec_info  # ✅ Successful execution

            # Prepare for next attempt: describe file and generate a new prompt
            file_desc = self.provide_file_details(file_path)
            prompt = self.generate_refactor_prompt(code, exec_info["error"], file_desc)

            try:
                client = genai.Client(api_key=self.genai_key)
                response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)

                if hasattr(response, "text"):
                    code = self.extract_python_code(response.text)
                else:
                    logger.warning("Gemini response has no 'text' attribute.")
                    return {"error": "Gemini response format unexpected."}
            except Exception as e:
                logger.error("Gemini API failed", exc_info=True)
                return {"error": str(e)}

        return {"error": f"Max attempts reached. Last error: {exec_info['error']}"}

    def gem_text_to_code(self, user_prompt: str, file_path: str):
        logger.info("Generating code from Gemini")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found!")

        file_desc = self.provide_file_details(file_path)
        prompt = f"""
            You are a Python data analysis assistant. The user has provided a CSV file at path: '{file_path}'.

            Use pandas, numpy, matplotlib.
            File Description:
            {file_desc}

            User Query:
            {user_prompt}"""
        try:
            client = genai.Client(api_key=self.genai_key)
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            code = self.extract_python_code(response.text)
            return self.gem_refactor_code(code, file_path)
        except Exception as e:
            logger.error("Gemini API failed", exc_info=True)
            return {"error": str(e)}

    def local_refactor_code(self, code: str, file_path: str, max_attempts=10):
        if not code:
            return {"error": "No code provided for refactoring."}

        last_error = "Unknown error"

        for attempt in range(1, max_attempts + 1):
            logger.info(f"Local refactor attempt {attempt}/{max_attempts}")

            exec_info = self.execute_code_with_dependencies.execute_code(code)
            if not exec_info.get("error"):
                logger.info("Code executed successfully.")
                return exec_info  # ✅ Success

            last_error = exec_info["error"]

            # Describe file and generate prompt
            file_desc = self.provide_file_details(file_path)
            prompt = self.generate_refactor_prompt(code, last_error, file_desc)

            try:
                llm = ChatOllama(model=self.local_model, temperature=0.3)
                messages = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Here is the code to refactor:\n{code}"}
                ]
                response = llm.invoke(messages)
                code = self.extract_python_code(response)
            except Exception as e:
                logger.error("Local LLM failed", exc_info=True)
                return {"error": str(e)}

        return {"error": f"Max attempts reached. Last error: {last_error}"}

    def local_text_to_code(self, user_prompt: str, file_path: str):
        logger.info("Generating code from local LLM")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found!")

        file_desc = self.provide_file_details(file_path)
        prompt = f"""
            You are a Python data analysis assistant. The user has provided a CSV file at path: '{file_path}'.

            Use pandas, numpy, matplotlib.
            File Description:
            {file_desc}

            User Query:
            {user_prompt}"""
        try:
            llm = ChatOllama(model=self.local_model, temperature=0.3)
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_prompt}
            ]
            response = llm.invoke(messages)
            code = self.extract_python_code(response)
            return self.local_refactor_code(code, file_path)
        except Exception as e:
            logger.error("Local LLM failed", exc_info=True)
            return {"error": str(e)}


def data_analysis(user_prompt: str , file_path:str):
    codeassistant = CodeRefactorAssistant()
    try:
        # Try to generate code via API
        response = codeassistant.gem_text_to_code(user_prompt , file_path)
        
    except Exception as e:
        # If API fails, log the error and fall back to local code generation
        logger.error(f"ERROR: {e} - Falling back to local processing.")
        response = codeassistant.local_text_to_code(user_prompt , file_path)

    return response

