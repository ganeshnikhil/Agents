"""
store() → Save new information (text, structured data, embeddings, etc.).
retrieve() → Get relevant information based on a query or context.
update() → Modify an existing memory entry.
delete() → Remove an entry by ID or content.
[
{
    "timestamp_id": "20250814_142530_123",  
    "agent" : jarvis
    "user": "What's the weather in Paris?",
    "assistant": "It's currently 22°C and sunny in Paris.",
}
]
"""
# import json 

# class ShortTermMemory:
#     def __init__(self):
#         self.enteries = []
#         self.acess = reteriver()
        
#     def load_data(self):
#         with open(self.path , 'r') as memory:
#             self.enteries = json.load(memory)
    
#     def write_data(self):
#         # Write back to file
#         with open(self.path, "w") as f:
#             json.dump(self.enteries, f, indent=2)

#     def store(self, data:dict[str , str , str]):
#         self.enteries.append(data)
    
#     def reterive(self , target , int k = 5):
#         return self.retervier(target , self.enteries)
        
    
#     def delete(self , entry_id):
#         self.entries = [e for e in self.entries if e.get("id") != entry_id]
    
    
#     def update(self, data:dict[str , str , str , str] ):
#         """Update a stored memory entry."""
#         for e in self.entries:
#             if e.get("id") == data.get("id"):
#                 e["id"] = data.get("id")
#                 e["name"] = data.get("name")
#                 e["user"] = data.get("user")
#                 e["assitant"] = data.get("assistant")

# import json
# import os
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional, Any
# import logging
# from dataclasses import dataclass, asdict
# import uuid
# import numpy as np
# import ollama
# from sklearn.metrics.pairwise import cosine_similarity

# # Memory format
# """{
#     "timestamp_id": "20250814_142530_123",  
#     "agent" : jarvis
#     "user": "What's the weather in Paris?",
#     "assistant": "It's currently 22°C and sunny in Paris.",
# }"""
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# @dataclass
# class MemoryEntry:
#     """Structure for memory entries with type hints and validation."""
#     timestamp_id: str
#     agent: str
#     user: str
#     assistant: str
#     timestamp: str
    
#     def __post_init__(self):
#         if self.tags is None:
#             self.tags = []

# class EmbeddingRetriever:
#     """Embedding-based retriever using Ollama's nomic-embed-text model."""
    
#     def __init__(self, model_name: str = "nomic-embed-text"):
#         """
#         Initialize the embedding retriever with Ollama.
        
#         Args:
#             model_name: Name of the embedding model (nomic-embed-text)
#             host: Ollama host URL
#         """
#         self.model_name = model_name
#         self._test_connection()
#         logger.info(f"✅ Initialized Ollama embedding retriever with model: {model_name}")
    
#     def _test_connection(self):
#         """Test connection to Ollama server and model availability."""
#         try:
#             # Test connection by listing models
#             models = ollama.list()
#             model_names = [model['name'] for model in models['models']]
            
#             if not any(self.model_name in name for name in model_names):
#                 logger.warning(f"⚠️ Model '{self.model_name}' not found in Ollama.")
#                 logger.warning(f"Available models: {model_names}")
#                 logger.warning(f"Please run: ollama pull {self.model_name}")
                
#                 # Try to pull the model automatically
#                 try:
#                     logger.info(f"🔄 Attempting to pull {self.model_name}...")
#                     self.client.pull(self.model_name)
#                     logger.info(f"✅ Successfully pulled {self.model_name}")
#                 except Exception as pull_error:
#                     logger.error(f"❌ Failed to pull model: {pull_error}")
#                     raise
#             else:
#                 logger.info(f"✅ Model {self.model_name} is available")
                
#         except Exception as e:
#             logger.error(f"❌ Failed to connect to Ollama: {e}")
#             raise ConnectionError(f"Cannot connect to Ollama: {e}")
    
#     def _create_searchable_text(self, entry: Dict) -> str:
#         """Create a searchable text from memory entry."""
#         return entry.get("user","")
#         # parts = [
#         #     entry.get("user", ""),
#         #     entry.get("assistant", ""),
#         #     entry.get("agent", ""),
#         #     " ".join(entry.get("tags", []))
#         # ]
#         # return " ".join(filter(None, parts))
    
#     def _get_embeddings(self, texts: List[str]) -> np.ndarray:
#         """Generate embeddings using Ollama client."""
#         try:
#             embeddings = []
            
#             for text in texts:
#                 if not text.strip():  # Skip empty texts
#                     continue
                
#                 response = ollama.embeddings(
#                     model=self.model_name, 
#                     prompt=text)
                
#                 if 'embedding' in response:
#                     embeddings.append(response['embedding'])
#                 else:
#                     logger.error(f"❌ No embedding returned for text: {text[:50]}...")
#                     return np.array([])
            
#             if not embeddings:
#                 logger.error("❌ No embeddings generated")
#                 return np.array([])
            
#             return np.array(embeddings)
            
#         except Exception as e:
#             logger.error(f"❌ Failed to get embeddings from Ollama: {e}")
#             return np.array([])
    
#     def __call__(self, target: str, entries: List[Dict], k: int = 5) -> List[Dict]:
#         """
#         Embedding-based retrieval for short-term memory.
        
#         Args:
#             target: Search query
#             entries: List of memory entries
#             k: Number of results to return
            
#         Returns:
#             List of most relevant memory entries
#         """
#         if not target or not entries:
#             return []
        
#         try:
#             # Create searchable texts from entries
#             entry_texts = [self._create_searchable_text(entry) for entry in entries]
            
#             # Generate embeddings for query and entries
#             query_embedding = self._get_embeddings([target])
#             entry_embeddings = self._get_embeddings(entry_texts)
            
#             if query_embedding.size == 0 or entry_embeddings.size == 0:
#                 logger.warning("Failed to generate embeddings, falling back to keyword search")
#                 return self._fallback_search(target, entries, k)
            
#             # Calculate cosine similarities
#             similarities = cosine_similarity(query_embedding, entry_embeddings)[0]
            
#             # Get top k most similar entries
#             top_indices = np.argsort(similarities)[::-1][:k]
            
#             # Filter out entries with very low similarity (threshold: 0.1)
#             filtered_results = []
#             for idx in top_indices:
#                 if similarities[idx] > 0.1:  # Similarity threshold
#                     entry_copy = entries[idx].copy()
#                     entry_copy['similarity_score'] = float(similarities[idx])
#                     filtered_results.append(entry_copy)
            
#             logger.info(f"🔍 Retrieved {len(filtered_results)} memories using embeddings")
#             return filtered_results
            
#         except Exception as e:
#             logger.error(f"❌ Embedding retrieval failed: {e}, falling back to keyword search")
#             return self._fallback_search(target, entries, k)
    
#     def _fallback_search(self, target: str, entries: List[Dict], k: int) -> List[Dict]:
#         """Fallback keyword-based search when embeddings fail."""
#         target_lower = target.lower()
#         scored_entries = []
        
#         for entry in entries:
#             score = 0
#             # Check user query
#             if target_lower in entry.get("user", "").lower():
#                 score += 3
#             # Check assistant response  
#             if target_lower in entry.get("assistant", "").lower():
#                 score += 2
#             # Check agent name
#             if target_lower in entry.get("agent", "").lower():
#                 score += 1
#             # Check tags
#             for tag in entry.get("tags", []):
#                 if target_lower in tag.lower():
#                     score += 2
                    
#             if score > 0:
#                 scored_entries.append((score, entry))
        
#         # Sort by score and return top k
#         scored_entries.sort(key=lambda x: x[0], reverse=True)
#         return [entry for score, entry in scored_entries[:k]]

# class ShortTermMemory:
#     """
#     Short-term memory system for temporary storage and quick retrieval.
#     Designed for session-based memory that expires or gets moved to long-term storage.
#     Uses Ollama embeddings for semantic search.
#     """
    
#     def __init__(self, filepath: str = "short_term_memory.json", 
#                 max_entries: int = 100,
#                 auto_save: bool = True,
#                 session_timeout_hours: int = 24,
#                 embedding_model: str = "nomic-embed-text",):
#         self.path = filepath
#         self.max_entries = max_entries
#         self.auto_save = auto_save
#         self.session_timeout_hours = session_timeout_hours
#         self.entries: List[Dict] = []
        
#         # Initialize embedding retriever
#         try:
#             self.retriever = EmbeddingRetriever(
#                 model_name=embedding_model
#             )
#         except Exception as e:
#             logger.warning(f"⚠️ Failed to initialize embedding retriever: {e}")
#             logger.warning("Falling back to keyword-based search")
#             self.retriever = None
        
#         # Load existing data if file exists
#         self.load_data()
        
#         # Clean expired entries
#         self._cleanup_expired_entries()
        
#     def _is_duplicate(self, user_query: str, assistant_response: str) -> bool:
#         """
#         Checks if a memory with the same user query and assistant response already exists.
        
#         Args:
#             user_query: The user's input.
#             assistant_response: The assistant's response.
        
#         Returns:
#             True if a duplicate is found, False otherwise.
#         """
#         for entry in self.entries:
#             if entry.get("user") == user_query or entry.get("assistant") == assistant_response:
#                 return True
#         return False
        
#     def add(self,data:dict[str , str]):
#         """
#         Adds a new memory entry.
        
#         Args:
#             user_query: The user's input.
#             assistant_response: The agent's response.
#             agent: The name of the agent.
#             tags: Optional list of tags.
#             priority: An integer indicating the priority of the memory.
#         """
#         # Check for duplicates before adding
#         if self._is_duplicate(user_query, assistant_response):
#             logger.info("ℹ️ Duplicate memory detected. Skipping addition.")
#             return

#         # Remove oldest entry if max capacity is reached
#         if len(self.entries) >= self.max_entries:
#             self.entries.pop(0)
#             logger.info("🗑️ Max entries reached, removing oldest memory.")
            
#         new_entry = MemoryEntry(
#             timestamp_id=data.get("timestamp_id")
#             agent=data.get("agent"),
#             user=data.get("user"),
#             assistant=data.get("assistant"),
#         )
#         self.entries.append(asdict(new_entry))
        
#         if self.auto_save:
#             self.save_data()
            
#         logger.info(f"➕ Added new memory from agent '{data.get("agent")}'.")

#     def search(self, user_query: str, k: int = 5) -> List[Dict]:
#         """
#         Searches for relevant memories based on the user's query.
#         Prioritizes semantic search with embeddings, falls back to keyword search.
        
#         Args:
#             user_query: The query to search for.
#             k: The number of top results to return.
            
#         Returns:
#             A list of the k most relevant memory entries, sorted by relevance.
#         """
#         if not user_query:
#             return []
            
#         # Use embedding retriever if available
#         if self.retriever:
#             return self.retriever(target=user_query, entries=self.entries, k=k)
#         else:
#             logger.info("🔍 No embedding retriever available, using keyword search.")
#             return self._fallback_search(target=user_query, k=k)
            
#     def _fallback_search(self, target: str, k: int) -> List[Dict]:
#         """Performs a simple keyword-based search across all entry fields."""
#         target_lower = target.lower()
#         scored_entries = []
        
#         for entry in self.entries:
#             score = 0
#             if target_lower in entry.get("user", "").lower():
#                 score += 3
#             if target_lower in entry.get("assistant", "").lower():
#                 score += 2
#             if target_lower in entry.get("agent", "").lower():
#                 score += 1
#             for tag in entry.get("tags", []):
#                 if target_lower in tag.lower():
#                     score += 2
                    
#             if score > 0:
#                 scored_entries.append((score, entry))
                
#         scored_entries.sort(key=lambda x: x[0], reverse=True)
#         return [entry for score, entry in scored_entries[:k]]
        
#     def load_data(self):
#         """Loads memory entries from a JSON file."""
#         if os.path.exists(self.path):
#             try:
#                 with open(self.path, 'r', encoding='utf-8') as f:
#                     data = json.load(f)
#                     self.entries = [MemoryEntry(**entry).asdict() for entry in data]
#                 logger.info(f"💾 Loaded {len(self.entries)} memories from {self.path}")
#             except (IOError, json.JSONDecodeError) as e:
#                 logger.error(f"❌ Failed to load data from {self.path}: {e}")
#                 self.entries = []

#     def save_data(self):
#         """Saves all memory entries to a JSON file."""
#         try:
#             with open(self.path, 'w', encoding='utf-8') as f:
#                 json.dump(self.entries, f, indent=2)
#             logger.info(f"✅ Saved {len(self.entries)} memories to {self.path}")
#         except IOError as e:
#             logger.error(f"❌ Failed to save data to {self.path}: {e}")
    
#     def clear(self):
#         """Clears all memory entries."""
#         self.entries = []
#         if os.path.exists(self.path):
#             os.remove(self.path)
#         logger.info("🔥 All short-term memories cleared.")
        
#     def _cleanup_expired_entries(self):
#         """Removes entries older than the session timeout."""
#         if not self.entries:
#             return
            
#         timeout_delta = timedelta(hours=self.session_timeout_hours)
#         now = datetime.now()
        
#         active_entries = []
#         for entry in self.entries:
#             try:
#                 entry_time = datetime.fromisoformat(entry['timestamp'])
#                 if now - entry_time < timeout_delta:
#                     active_entries.append(entry)
#             except (ValueError, KeyError) as e:
#                 logger.warning(f"⚠️ Invalid timestamp format in entry: {entry.get('timestamp')}. Removing entry.")
                
#         if len(active_entries) < len(self.entries):
#             removed_count = len(self.entries) - len(active_entries)
#             self.entries = active_entries
#             logger.info(f"🗑️ Cleaned up {removed_count} expired memory entries.")
#             if self.auto_save:
#                 self.save_data()
                
                




import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
import numpy as np
import ollama
from sklearn.metrics.pairwise import cosine_similarity

# Memory format
"""{
    "timestamp_id": "20250814_142530_123",  
    "agent": "jarvis",
    "user": "What's the weather in Paris?",
    "assistant": "It's currently 22°C and sunny in Paris."
}"""

# Configure logging
logging.basicConfig(level=logging.INFO, force=True)
#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Structure for memory entries with type hints and validation."""
    timestamp_id: str
    agent: str
    user: str
    assistant: str

class EmbeddingRetriever:
    """Embedding-based retriever using Ollama's nomic-embed-text model."""
    
    def __init__(self, model_name: str="nomic-embed-text:latest"):
        """
        Initialize the embedding retriever with Ollama.
        
        Args:
            model_name: Name of the embedding model (nomic-embed-text)
        """
        self.model_name = model_name
        try:
            self._test_connection()
            logger.info(f"✅ Initialized Ollama embedding retriever with model: {model_name}")
        except Exception as e:
            logger.warning(f"⚠️ Embedding retriever initialization failed: {e}")
            raise
    
    def _test_connection(self):
        """Test connection to Ollama server and model availability."""
        try:
            # Test connection by listing models
            models = ollama.list()
            model_names = [model['model'] for model in models['models']]
            
            if not any(self.model_name in name for name in model_names):
                logger.warning(f"⚠️ Model '{self.model_name}' not found in Ollama.")
                logger.warning(f"Available models: {model_names}")
                logger.warning(f"Please run: ollama pull {self.model_name}")
                
                # Try to pull the model automatically
                try:
                    logger.info(f"🔄 Attempting to pull {self.model_name}...")
                    ollama.pull(self.model_name)
                    logger.info(f"✅ Successfully pulled {self.model_name}")
                except Exception as pull_error:
                    logger.error(f"❌ Failed to pull model: {pull_error}")
                    raise
            else:
                logger.info(f"✅ Model {self.model_name} is available")
                
        except Exception as e:
            logger.error(f"❌ Failed to connect to Ollama: {e}")
            raise ConnectionError(f"Cannot connect to Ollama: {e}")
    
    def _create_searchable_text(self, entry: Dict, use_combined: bool) -> str:
        if use_combined:
            parts = [entry.get("user", ""), entry.get("assistant", "")]
            return " ".join(filter(None, parts))
        else:
            return entry.get("assistant", "")

    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Ollama client."""
        try:
            embeddings = []
            
            for text in texts:
                if not text.strip():  # Skip empty texts
                    continue
                
                response = ollama.embeddings(
                    model=self.model_name, 
                    prompt=text)
                
                if 'embedding' in response:
                    embeddings.append(response['embedding'])
                else:
                    logger.error(f"❌ No embedding returned for text: {text[:50]}...")
                    return np.array([])
            
            if not embeddings:
                logger.error("❌ No embeddings generated")
                return np.array([])
            
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"❌ Failed to get embeddings from Ollama: {e}")
            return np.array([])
    
    @staticmethod
    def calculate_decay(similarity_score: float, timestamp_id: str, decay_hours: int = 168) -> float:
        """
        Apply decay to similarity score based on age of memory.
        decay_hours: number of hours for full decay (default 1 week)
        """
        try:
            # Extract timestamp from timestamp_id: YYYYMMDD_HHMMSS_mmm
            # date_part = timestamp_id[:8]  # YYYYMMDD
            # time_part = timestamp_id[9:15]  # HHMMSS
            # created_at = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
            created_at = datetime.strptime(timestamp_id, "%Y%m%d_%H%M%S_%f")
            age_hours = (datetime.now() - created_at).total_seconds() / 3600
            decay_factor = np.exp(-np.log(2) * age_hours / decay_hours)

            #decay_factor = np.exp(-age_hours / decay_hours)
            return similarity_score * decay_factor
        except Exception as e:
            logger.warning(f"⚠️ Failed to apply decay for {timestamp_id}: {e}")
            return similarity_score 
        
    def __call__(self, target: str, entries: List[Dict], threshold: float = 0.60 , k: int = 5) -> List[Dict]:
        """
        Embedding-based retrieval for short-term memory.
        
        Args:
            target: Search query
            entries: List of memory entries
            k: Number of results to return
            
        Returns:
            List of most relevant memory entries
        """
        if not target or not entries:
            return []
        
        try:
            use_combined_search = len(target.strip()) >= 50
            # Create searchable texts from entries
            entry_texts = [self._create_searchable_text(entry , use_combined_search) for entry in entries]
            # Generate embeddings for query and entries
            query_embedding = self._get_embeddings([target])
            entry_embeddings = self._get_embeddings(entry_texts)
            if query_embedding.size == 0 or entry_embeddings.size == 0:
                logger.warning("Failed to generate embeddings, falling back to keyword search")
                return self._fallback_search(target, entries, k)
            
            # Calculate cosine similarities
            query_embedding = np.array(query_embedding).reshape(1, -1)
            entry_embeddings = np.array(entry_embeddings)
            
            similarities = cosine_similarity(query_embedding, entry_embeddings)[0]
            
            # Apply decay based on timestamp_id
            if len(similarities) > 1:
                for i, entry in enumerate(entries):
                    timestamp_id = entry.get('timestamp_id', '')
                    similarities[i] = self.calculate_decay(similarities[i], timestamp_id)
                
            
            # Get top k most similar entries
            top_indices = np.argsort(similarities)[::-1][:k]
            # Filter out entries with very low similarity (threshold: 0.1)
            filtered_results = []
            for idx in top_indices:
                if similarities[idx] > threshold:  # Similarity threshold
                    entry_copy = entries[idx].copy()
                    entry_copy['similarity_score'] = float(similarities[idx])
                    filtered_results.append(entry_copy)
            
            logger.info(f"🔍 Retrieved {len(filtered_results)} memories using embeddings")
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ Embedding retrieval failed: {e}, falling back to keyword search")
            return self._fallback_search(target, entries, k)
    
    def _fallback_search(self, target: str, entries: List[Dict], k: int) -> List[Dict]:
        """Fallback keyword-based search when embeddings fail."""
        target_lower = target.lower()
        scored_entries = []
        
        for entry in entries:
            score = 0
            # Check user query
            if target_lower in entry.get("user", "").lower():
                score += 3
            # Check assistant response  
            if target_lower in entry.get("assistant", "").lower():
                score += 2
            # Check agent name
            if target_lower in entry.get("agent", "").lower():
                score += 1
                    
            if score > 0:
                scored_entries.append((score, entry))
        
        # Sort by score and return top k
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [entry for score, entry in scored_entries[:k]]

class ShortTermMemory:
    """
    Short-term memory system for temporary storage and quick retrieval.
    Designed for session-based memory that expires or gets moved to long-term storage.
    Uses Ollama embeddings for semantic search.
    """
    
    def __init__(self, filepath: str = "short_term_memory.json", 
                max_entries: int = 100,
                auto_save: bool = True,
                session_timeout_hours: int = 24,
                embedding_model: str = "nomic-embed-text"):
        self.path = filepath
        self.max_entries = max_entries
        self.auto_save = auto_save
        self.session_timeout_hours = session_timeout_hours
        self.entries: List[Dict] = []
        
        # Initialize embedding retriever
        try:
            self.retriever = EmbeddingRetriever(
                model_name=embedding_model
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize embedding retriever: {e}")
            logger.warning("Falling back to keyword-based search")
            self.retriever = None
        
        # Load existing data if file exists
        self.load_data()
        
        # Clean expired entries
        self._cleanup_expired_entries()
        
    def _generate_timestamp_id(self) -> str:
        """Generate timestamp ID in the specified format."""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        
    def _is_duplicate(self, user_query: str, assistant_response: str) -> bool:
        """
        Checks if a memory with the same user query and assistant response already exists.
        
        Args:
            user_query: The user's input.
            assistant_response: The assistant's response.
        
        Returns:
            True if a duplicate is found, False otherwise.
        """
        for entry in self.entries:
            if (entry.get("user") == user_query and 
                entry.get("assistant") == assistant_response):
                return True
        return False
    
    
    def _find_duplicate_index(self, user_query: str, assistant_response: str) -> Optional[int]:
        """
        Returns the index of a duplicate memory if found, else None.
        """
        for i, entry in enumerate(self.entries):
            if (entry.get("user") == user_query and 
                entry.get("assistant") == assistant_response):
                return i
        return None
    
    
    def add(self, data: Dict[str, Any]):
        """
        Adds a new memory entry. If a duplicate exists, replaces it.
        """
        user_query = data.get("user", "")
        assistant_response = data.get("assistant", "")
        
        # Check if duplicate exists
        duplicate_index = self._find_duplicate_index(user_query, assistant_response)
        
        # Generate timestamp_id (new one)
        timestamp_id = data.get("timestamp_id") or self._generate_timestamp_id()
        
        new_entry = MemoryEntry(
            timestamp_id=timestamp_id,
            agent=data.get("agent", "unknown"),
            user=user_query,
            assistant=assistant_response
        )
        
        if duplicate_index is not None:
            # Replace the old memory
            self.entries[duplicate_index] = asdict(new_entry)
            logger.info(f"♻️ Duplicate found. Replaced memory at index {duplicate_index}.")
        else:
            # Remove oldest entry if max capacity is reached
            if len(self.entries) >= self.max_entries:
                self.entries.pop(0)
                logger.info("🗑️ Max entries reached, removing oldest memory.")
            self.entries.append(asdict(new_entry))
            logger.info(f"➕ Added new memory from agent '{data.get('agent', 'unknown')}'.")
        
        if self.auto_save:
            self.save_data()


    # def add(self, data: Dict[str, Any]):
    #     """
    #     Adds a new memory entry.
        
    #     Args:
    #         data: Dictionary containing memory data with keys: agent, user, assistant, tags (optional)
    #     """
    #     user_query = data.get("user", "")
    #     assistant_response = data.get("assistant", "")
        
    #     # Check for duplicates before adding
    #     if self._is_duplicate(user_query, assistant_response):
    #         logger.info("ℹ️ Duplicate memory detected. Skipping addition.")
    #         return

    #     # Remove oldest entry if max capacity is reached
    #     if len(self.entries) >= self.max_entries:
    #         self.entries.pop(0)
    #         logger.info("🗑️ Max entries reached, removing oldest memory.")
            
    #     # Generate timestamp and timestamp_id
    #     timestamp_id = data.get("timestamp_id") or self._generate_timestamp_id()
        
    #     new_entry = MemoryEntry(
    #         timestamp_id=timestamp_id,
    #         agent=data.get("agent", "unknown"),
    #         user=user_query,
    #         assistant=assistant_response
    #     )
    #     self.entries.append(asdict(new_entry))
        
    #     if self.auto_save:
    #         self.save_data()
            
    #     logger.info(f"➕ Added new memory from agent '{data.get('agent', 'unknown')}'.")

    def search(self, user_query: str, k: int = 5) -> List[Dict]:
        """
        Searches for relevant memories based on the user's query.
        Prioritizes semantic search with embeddings, falls back to keyword search.
        
        Args:
            user_query: The query to search for.
            k: The number of top results to return.
            
        Returns:
            A list of the k most relevant memory entries, sorted by relevance.
        """
        if not user_query:
            return []
            
        # Use embedding retriever if available
        if self.retriever:
            return self.retriever(target=user_query, entries=self.entries, k=k)
        else:
            logger.info("🔍 No embedding retriever available, using keyword search.")
            return self._fallback_search(target=user_query, k=k)
            
    def _fallback_search(self, target: str, k: int) -> List[Dict]:
        """Performs a simple keyword-based search across all entry fields."""
        target_lower = target.lower()
        scored_entries = []
        
        for entry in self.entries:
            score = 0
            if target_lower in entry.get("user", "").lower():
                score += 3
            if target_lower in entry.get("assistant", "").lower():
                score += 2
            if target_lower in entry.get("agent", "").lower():
                score += 1
                    
            if score > 0:
                scored_entries.append((score, entry))
                
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        return [entry for score, entry in scored_entries[:k]]
        
    def load_data(self):
        """Loads memory entries from a JSON file."""
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Data is already in dict format, no need to convert
                    self.entries = data if isinstance(data, list) else []
                logger.info(f"💾 Loaded {len(self.entries)} memories from {self.path}")
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"❌ Failed to load data from {self.path}: {e}")
                self.entries = []

    def save_data(self):
        """Saves all memory entries to a JSON file."""
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {len(self.entries)} memories to {self.path}")
        except IOError as e:
            logger.error(f"❌ Failed to save data to {self.path}: {e}")
    
    def clear(self):
        """Clears all memory entries."""
        self.entries = []
        if os.path.exists(self.path):
            os.remove(self.path)
        logger.info("🔥 All short-term memories cleared.")
        
    def get_all_entries(self) -> List[Dict]:
        """Returns all memory entries."""
        return self.entries.copy()
        
    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the memory system."""
        if not self.entries:
            return {"total_entries": 0, "agents": []}
            
        agents = list(set(entry.get("agent", "unknown") for entry in self.entries))
        
        return {
            "total_entries": len(self.entries),
            "agents": agents,
            "max_capacity": self.max_entries
        }
        
    def _cleanup_expired_entries(self):
        """Removes entries older than the session timeout."""
        if not self.entries:
            return
            
        timeout_delta = timedelta(hours=self.session_timeout_hours)
        now = datetime.now()
        
        active_entries = []
        for entry in self.entries:
            try:
                # Extract timestamp from timestamp_id format: YYYYMMDD_HHMMSS_mmm
                timestamp_str = entry.get('timestamp_id', '')
                if len(timestamp_str) >= 15:  # YYYYMMDD_HHMMSS format minimum
                    entry_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S_%f")
                    # Parse the timestamp
                    if now - entry_time < timeout_delta:
                        active_entries.append(entry)
                else:
                    # If timestamp format is invalid, keep the entry
                    active_entries.append(entry)
            except (ValueError, KeyError) as e:
                logger.warning(f"⚠️ Invalid timestamp_id format: {entry.get('timestamp_id')}. Keeping entry.")
                active_entries.append(entry)
                
        if len(active_entries) < len(self.entries):
            removed_count = len(self.entries) - len(active_entries)
            self.entries = active_entries
            logger.info(f"🗑️ Cleaned up {removed_count} expired memory entries.")
            if self.auto_save:
                self.save_data()


def print_memory_entry(entry: Dict, index: int = None):
    """Pretty print a memory entry."""
    prefix = f"[{index + 1}] " if index is not None else ""
    print(f"\n{prefix}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📅 ID: {entry.get('timestamp_id', 'N/A')}")
    print(f"🤖 Agent: {entry.get('agent', 'N/A')}")
    print(f"👤 User: {entry.get('user', 'N/A')}")
    print(f"💬 Assistant: {entry.get('assistant', 'N/A')}")
    if 'similarity_score' in entry:
        print(f"📊 Similarity: {entry['similarity_score']:.3f}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def main_menu():
    """Main menu-driven interface for testing the memory system."""
    print("\n🧠 Short-Term Memory System Test Interface")
    print("=" * 50)
    # /Users/ganeshnikhil/Memory-Twin/data/memory_store/shorterm
    # Initialize memory system
    try:
        memory = ShortTermMemory(
            filepath="../../data/memory_store/shorterm/short_term.json",
            max_entries=50,
            auto_save=True,
            session_timeout_hours=24
        )
        print("✅ Memory system initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize memory system: {e}")
        print("🔄 Continuing with keyword-only search...")
        memory = ShortTermMemory(
            filepath="test_memory.json",
            max_entries=50,
            auto_save=True,
            session_timeout_hours=24,
            embedding_model="none"  # This will cause embedding init to fail gracefully
        )
    
    while True:
        print("\n📋 MAIN MENU")
        print("-" * 20)
        print("1. ➕ Add Memory Entry")
        print("2. 🔍 Search Memories") 
        print("3. 📂 View All Memories")
        print("4. 📊 Show Statistics")
        print("5. 🗑️  Clear All Memories")
        print("6. 💾 Save Memories")
        print("7. 📥 Load Memories") 
        print("8. ❌ Exit")
        
        choice = input("\n🔢 Enter your choice (1-8): ").strip()
        
        try:
            if choice == '1':
                add_memory_interactive(memory)
            elif choice == '2':
                search_memories_interactive(memory)
            elif choice == '3':
                view_all_memories(memory)
            elif choice == '4':
                show_statistics(memory)
            elif choice == '5':
                clear_memories_interactive(memory)
            elif choice == '6':
                memory.save_data()
                print("✅ Memories saved successfully!")
            elif choice == '7':
                memory.load_data()
                print("✅ Memories loaded successfully!")
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def add_memory_interactive(memory: ShortTermMemory):
    """Interactive function to add a memory entry."""
    print("\n➕ ADD NEW MEMORY")
    print("-" * 20)
    
    agent = input("🤖 Agent name (default: 'jarvis'): ").strip() or "jarvis"
    user_input = input("👤 User input: ").strip()
    assistant_response = input("💬 Assistant response: ").strip()
    
    if not user_input or not assistant_response:
        print("❌ User input and assistant response are required!")
        return
    
    data = {
        "agent": agent,
        "user": user_input,
        "assistant": assistant_response
    }
    
    memory.add(data)
    print("✅ Memory added successfully!")


def search_memories_interactive(memory: ShortTermMemory):
    """Interactive function to search memories."""
    print("\n🔍 SEARCH MEMORIES")
    print("-" * 20)
    
    query = input("🔎 Enter search query: ").strip()
    if not query:
        print("❌ Search query cannot be empty!")
        return
        
    try:
        k = int(input("📊 Number of results (default: 5): ").strip() or "5")
    except ValueError:
        k = 5
        
    results = memory.search(query, k=k)
    
    if not results:
        print("❌ No matching memories found!")
        return
        
    print(f"\n✅ Found {len(results)} matching memories:")
    for i, entry in enumerate(results):
        print_memory_entry(entry, i)


def view_all_memories(memory: ShortTermMemory):
    """View all stored memories."""
    print("\n📂 ALL STORED MEMORIES")
    print("-" * 25)
    
    entries = memory.get_all_entries()
    
    if not entries:
        print("📭 No memories stored yet!")
        return
        
    print(f"📊 Total memories: {len(entries)}")
    
    for i, entry in enumerate(entries):
        print_memory_entry(entry, i)


def show_statistics(memory: ShortTermMemory):
    """Show memory system statistics."""
    print("\n📊 MEMORY STATISTICS")
    print("-" * 20)
    
    stats = memory.get_stats()
    
    print(f"📈 Total Entries: {stats['total_entries']}")
    print(f"🎯 Max Capacity: {stats['max_capacity']}")
    print(f"🤖 Agents: {', '.join(stats['agents']) if stats['agents'] else 'None'}")
    
    if stats['total_entries'] > 0:
        usage_percent = (stats['total_entries'] / stats['max_capacity']) * 100
        print(f"💾 Memory Usage: {usage_percent:.1f}%")


def clear_memories_interactive(memory: ShortTermMemory):
    """Interactive function to clear all memories."""
    print("\n🗑️ CLEAR ALL MEMORIES")
    print("-" * 22)
    
    confirm = input("⚠️  Are you sure you want to clear ALL memories? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        memory.clear()
        print("✅ All memories cleared successfully!")
    else:
        print("❌ Operation cancelled.")


if __name__ == "__main__":
    # Add some sample data for testing
    
    memory = ShortTermMemory(
            filepath="/Users/ganeshnikhil/Memory-Twin/data/memory_store/shorterm/short_term.json",
            max_entries=50,
            auto_save=True,
            session_timeout_hours=24
        )
    
    ans = memory.search("is there any metting today at 4pm",k=3)
    print(ans)
    # def add_sample_data(memory: ShortTermMemory):
    #     """Add sample data for testing."""
    #     sample_data = [
    #         {
    #             "agent": "jarvis",
    #             "user": "What's the weather in Paris?",
    #             "assistant": "It's currently 22°C and sunny in Paris with light winds."
    #         },
    #         {
    #             "agent": "jarvis", 
    #             "user": "Tell me about machine learning",
    #             "assistant": "Machine learning is a subset of AI that enables computers to learn from data."
    #         },
    #         {
    #             "agent": "assistant",
    #             "user": "How do I cook pasta?",
    #             "assistant": "Boil water, add salt, cook pasta for 8-12 minutes until al dente."
    #         }
    #     ]
        
    #     print("🔄 Adding sample data...")
    #     for data in sample_data:
    #         memory.add(data)
    #     print("✅ Sample data added!")
    
    # # Ask if user wants sample data
    # add_samples = input("🎯 Add sample data for testing? (y/n): ").strip().lower()
    
    # if add_samples in ['y', 'yes']:
    #     temp_memory = ShortTermMemory(filepath="test_memory.json")
    #     add_sample_data(temp_memory)
    
    # # Start main menu
    # main_menu()