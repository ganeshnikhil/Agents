import json
import logging
import os
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingMemory:
    """
    WorkingMemory stores only the latest memory chunk (1 at a time).
    Overwrites previous memory on each write.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def write(self, data: Dict) -> None:
        """
        Stores a single memory chunk (overwrites existing one).
        """
        try:
            with open(self.file_path, "w", encoding="utf-8") as memory:
                json.dump(data, memory, indent=2, ensure_ascii=False)
            logger.info(f"Working memory updated with timestamp: {data.get('timestamp_id')}")
        except Exception as e:
            logger.warning(f"Error writing to working memory file: {e}")
            raise

    def read(self) -> Optional[Dict]:
        """
        Reads the last memory chunk.
        Returns None if no memory file exists.
        """
        try:
            if not os.path.exists(self.file_path):
                logger.info("No working memory file found. Returning None.")
                return None

            with open(self.file_path, "r", encoding="utf-8") as memory:
                data = json.load(memory)
            logger.info(f"Working memory retrieved with timestamp: {data.get('timestamp_id')}")
            return data
        except Exception as e:
            logger.warning(f"Error reading working memory file: {e}")
            raise


if __name__ == "__main__":
    wm = WorkingMemory("working_memory.json")

    # Example memory chunk
    memory_chunk = {
        "timestamp_id": "20250814_142530_123456",
        "agent": "jarvis",
        "user": "What's the weather in Paris?",
        "assistant": "It's currently 22°C and sunny in Paris.",
    }

    # Write to working memory
    wm.write(memory_chunk)

    # Read back the last memory chunk
    last_memory = wm.read()
    print(last_memory)
