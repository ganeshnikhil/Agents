
# Memory format:
# {
#     "timestamp_id": "20250814_142530_123",
#     "agent": "jarvis",
#     "user": "What's the weather in Paris?",
#     "assistant": "It's currently 22°C and sunny in Paris.",
# }
# """



from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from qdrant_client.models import VectorParams, Distance
import ollama
from datetime import datetime
from typing import Dict, List, Optional
import uuid 
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
Memory format:
{
    "timestamp_id": "20250814_142530_123456",
    "agent": "jarvis",
    "user": "What's the weather in Paris?",
    "assistant": "It's currently 22°C and sunny in Paris.",
}
"""

class LongTermMemory:
    def __init__(self, collection_name="memories", embed_dim=768, host="localhost", port=6335, model="nomic-embed-text", similarity_threshold=0.85):
        self.collection_name = collection_name
        self.embed_dim = embed_dim
        self.model = model
        self.similarity_threshold = similarity_threshold  # Threshold for duplicate detection
        
        try:
            self.client = QdrantClient(host=host, port=port)
            self._initialize_collection()
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise
        
    def _initialize_collection(self):
        """Initialize the collection if it doesn't exist."""
        try:
            if not self.client.collection_exists(self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.embed_dim, distance=Distance.COSINE)
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise

    def _get_embedding(self, text: str) -> List[float]:
        """Generate an embedding using Ollama."""
        try:
            response = ollama.embeddings(model=self.model, prompt=text)
            return response["embedding"]
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def check_similarity_threshold(self, query_text: str, threshold: float = None) -> tuple[bool, dict]:
        """
        Check if incoming memory is too similar to existing memories.
        
        Returns:
            tuple: (is_duplicate, similar_memory_info)
            - is_duplicate: True if similar memory exists above threshold
            - similar_memory_info: Details of the most similar existing memory
        """
        if threshold is None:
            threshold = self.similarity_threshold
            
        try:
            # Search for similar memories (limit to 1 for efficiency)
            embedding = self._get_embedding(query_text)
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                limit=1,  # Only need the most similar
                with_payload=True,
                score_threshold=threshold  # Only return if above threshold
            ).points
            
            if results:
                most_similar = results[0]
                similar_memory_info = {
                    "timestamp_id": most_similar.payload.get("timestamp_id", "unknown"),
                    "score": float(most_similar.score),
                    "user": most_similar.payload.get("user", ""),
                    "assistant": most_similar.payload.get("assistant", ""),
                    "agent": most_similar.payload.get("agent", ""),
                }
                
                logger.info(f"🔍 Similar memory found with score {most_similar.score:.4f} (threshold: {threshold})")
                return True, similar_memory_info
            else:
                logger.info(f"✅ No similar memories found above threshold {threshold}")
                return False, {}
            
        except Exception as e:
            logger.info(f"Error: {e}")
            return False, {}
            
        def find_similar_memories(self, query_text: str, threshold: float = 0.8, limit: int = 5) -> List[Dict]:
            """Find all memories above similarity threshold."""
            try:
                embedding = self._get_embedding(query_text)
                results = self.client.query_points(
                    collection_name=self.collection_name,
                    query=embedding,
                    limit=limit,
                    with_payload=True,
                    score_threshold=threshold
                ).points
                
                return [
                    {
                        "timestamp_id": r.payload.get("timestamp_id", "unknown"),
                        "score": float(r.score),
                        "user": r.payload.get("user", ""),
                        "assistant": r.payload.get("assistant", ""),
                        "agent": r.payload.get("agent", ""),
                    }
                    for r in results
                ]
                
            except Exception as e:
                logger.error(f"Failed to find similar memories: {e}")
                return []

    def set_similarity_threshold(self, new_threshold: float) -> bool:
        """Update the similarity threshold for duplicate detection."""
        if 0.0 <= new_threshold <= 1.0:
            old_threshold = self.similarity_threshold
            self.similarity_threshold = new_threshold
            logger.info(f"📊 Similarity threshold updated: {old_threshold:.2f} → {new_threshold:.2f}")
            return True
        else:
            logger.error("❌ Threshold must be between 0.0 and 1.0")
            return False, {}
                
        # except Exception as e:
        #     logger.error(f"Failed to check similarity: {e}")
        #     return False, {}

    # def add_memory_with_similarity_check(self, data: Dict[str, str], 
    #                                    similarity_threshold: float = None,
    #                                    force_add: bool = False) -> tuple[bool, str, dict]:
    #     """
    #     Add memory with similarity checking to prevent duplicates.
        
    #     Args:
    #         data: Memory data to store
    #         similarity_threshold: Custom threshold (uses default if None)
    #         force_add: If True, add even if similar memory exists
            
    #     Returns:
    #         tuple: (success, message, similar_memory_info)
    #     """
    #     try:
    #         # Check for similarity first
    #         if not force_add:
    #             is_duplicate, similar_memory = self.check_similarity_threshold(
    #                 data["user"], similarity_threshold
    #             )
                
    #             if is_duplicate:
    #                 message = f"⚠️ Similar memory exists (score: {similar_memory['score']:.4f})"
    #                 logger.warning(f"{message}: '{similar_memory['user'][:50]}...'")
    #                 return False, message, similar_memory
            
    #         # If no similarity or forced, add the memory
    #         print(data)
    #         success = self.add_memory(data)
    #         if success:
    #             return True, "✅ Memory added successfully", {}
    #         else:
    #             return False, "❌ Failed to add memory", {}
                
    #     except Exception as e:
    #         logger.error(f"Failed to add memory with similarity check: {e}")
    #         return False, f"❌ Error: {str(e)}", {}
    
    
    
    def add_memory_with_similarity_check(self, data: Dict[str, str], 
                                similarity_threshold: float = None,
                                force_add: bool = False) -> tuple[bool, str, dict]:
        """
        Add memory with similarity checking.
        If a similar memory exists, update it instead of skipping.
        """
        try:
            # Check for similarity first
            is_duplicate, similar_memory = self.check_similarity_threshold(
                data["user"], similarity_threshold
            )

            if is_duplicate and not force_add:
                # Update the existing memory (by timestamp_id)
                updated = self.update_memory_by_id(similar_memory["timestamp_id"], data)
                if updated:
                    message = f"♻️ Updated similar memory (score: {similar_memory['score']:.4f})"
                    logger.info(message)
                    return True, message, similar_memory
                else:
                    message = f"❌ Failed to update similar memory"
                    logger.error(message)
                    return False, message, similar_memory

            # If no similarity or forced, add new memory
            success = self.add_memory(data)
            if success:
                return True, "✅ Memory added successfully", {}
            else:
                return False, "❌ Failed to add memory", {}

        except Exception as e:
            logger.error(f"Failed to add/update memory with similarity check: {e}")
            return False, f"❌ Error: {str(e)}", {}

    def add_memory(self, data: Dict[str, str]) -> bool:
        """Store a memory in Qdrant. Returns True if successful."""
        try:
            if self.memory_exists(data["user"], data.get("agent", "")):
                logger.warning(f"Memory already exists for user '{data['user']}' and agent '{data.get('agent', '')}'")
                return False

            embedding = self._get_embedding(data["user"])
            point_id = str(uuid.uuid4())
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": point_id,
                    "vector": embedding,
                    "payload": data
                }]
            )
            logger.info(f"✅ Memory saved: {data['user'][:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return False
        
    def memory_exists(self, user_text: str, agent_name: str = "") -> bool:
        """Check if a memory with the same user text and agent already exists."""
        try:
            filter_conditions = [FieldCondition(key="user", match=MatchValue(value=user_text))]
            
            if agent_name:
                filter_conditions.append(FieldCondition(key="agent", match=MatchValue(value=agent_name)))
            
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=filter_conditions),
                limit=1,
                with_payload=True
            )
            
            return len(result[0]) > 0
            
        except Exception as e:
            logger.error(f"Failed to check memory existence: {e}")
            return False

    def delete_memory_by_id(self, timestamp_id: str) -> bool:
        """Delete memory by timestamp-based ID."""
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=[FieldCondition(key="timestamp_id", match=MatchValue(value=timestamp_id))]),
                with_payload=True
            )
            
            points_to_delete = []
            for point in result[0]:
                points_to_delete.append(point.id)
            
            if points_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=points_to_delete
                )
                logger.info(f"🗑️ Deleted {len(points_to_delete)} memory(ies) with timestamp_id: {timestamp_id}")
                return True
            else:
                logger.warning(f"❌ No memory found with timestamp_id: {timestamp_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False
    
    def delete_memory_by_query(self, user_query: str) -> bool:
        """Delete memory by user query text."""
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=[FieldCondition(key="user", match=MatchValue(value=user_query))]),
                with_payload=True
            )
            
            points_to_delete = []
            for point in result[0]:
                points_to_delete.append(point.id)
            
            if points_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=points_to_delete
                )
                logger.info(f"🗑️ Deleted {len(points_to_delete)} memory(ies) matching query: {user_query}")
                return True
            else:
                logger.warning(f"❌ No memory found matching query: {user_query}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete memory by query: {e}")
            return False
    
    def update_memory_by_id(self, timestamp_id: str, new_data: Dict[str, str]) -> bool:
        """Update memory payload by timestamp-based ID."""
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=[FieldCondition(key="timestamp_id", match=MatchValue(value=timestamp_id))]),
                with_payload=True
            )
            
            if not result[0]:
                logger.warning(f"❌ No memory found with timestamp_id: {timestamp_id}")
                return False
            
            print(result)
            point = result[0][0]  # Get first match
            updated_payload = {**point.payload, **new_data}
            
            print(point.payload.get("user", "").strip())
            print(new_data["user"].strip())
            # Update embedding only if user query changed
            vector = None
            if point.payload.get("user", "").strip() != new_data["user"].strip():
                vector = self._get_embedding(new_data["user"])
                
            else:
                print(f'Value is already persent .. {point.payload.get("user", "")} -> {new_data.get("user")}')
                return False
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": point.id,  # Keep same Qdrant UUID
                    "vector": vector,  # New embedding or None to keep existing
                    "payload": updated_payload
                }]
            )
            logger.info(f"✅ Updated memory with timestamp_id: {timestamp_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory: {e}")
            return False

    def update_memory_by_query(self, prev_user_query: str, new_data: Dict[str, str]) -> bool:
        """Update memory payload by user query."""
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=[FieldCondition(key="user", match=MatchValue(value=prev_user_query))]),
                with_payload=True
            )

            if not result[0]:
                logger.warning(f"❌ No memory found with query: '{prev_user_query}'")
                return False

            point = result[0][0]  # Update only the first match
            updated_payload = {**point.payload, **new_data}

            # Update embedding only if user query changed
            vector = None
            if "user" in new_data and point.payload.get("user", "").strip() != new_data["user"].strip():
                vector = self._get_embedding(new_data["user"])

            self.client.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": point.id,  # Keep same Qdrant UUID
                    "vector": vector,
                    "payload": updated_payload
                }]
            )

            logger.info(f"✅ Updated memory for query: '{prev_user_query}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory by query: {e}")
            return False

    def search_memory(self, query: str, limit: int = 3, min_score: float = 0.0) -> List[Dict]:
        """Search for similar memories with optional minimum score threshold."""
        try:
            embedding = self._get_embedding(query)
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                limit=limit,
                with_payload=True,
                score_threshold=min_score
            ).points
            
            memories = []
            for r in results:
                try:
                    memory = {
                        "timestamp_id": r.payload.get("timestamp_id", "unknown"),
                        "score": float(r.score),
                        "user": r.payload.get("user", ""),
                        "assistant": r.payload.get("assistant", ""),
                        "agent": r.payload.get("agent", ""),
                    }
                    memories.append(memory)
                except Exception as point_error:
                    logger.warning(f"Skipping malformed search result: {point_error}")
                    continue
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []

    def get_all_memories(self, limit: int = 100) -> List[Dict]:
        """Retrieve all memories (up to limit)."""
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True
            )
            
            memories = []
            points = result[0] if result else []
            
            for point in points:
                try:
                    memory = {
                        "timestamp_id": point.payload.get("timestamp_id", "unknown"),
                        "user": point.payload.get("user", ""),
                        "assistant": point.payload.get("assistant", ""),
                        "agent": point.payload.get("agent", ""),
                    }
                    memories.append(memory)
                except Exception as point_error:
                    logger.warning(f"Skipping malformed point: {point_error}")
                    continue
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []

    def get_memory_count(self) -> int:
        """Get total number of memories stored."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except Exception as e:
            logger.error(f"Failed to get memory count: {e}")
            return 0

    def delete_all_memories(self) -> bool:
        """Delete all memories from the collection."""
        try:
            # Get current count for logging
            initial_count = self.get_memory_count()
            
            # Delete the entire collection and recreate it
            self.client.delete_collection(self.collection_name)
            self._initialize_collection()
            
            logger.info(f"🗑️ Deleted all {initial_count} memories from collection '{self.collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete all memories: {e}")
            return False

    def clear_memories_by_agent(self, agent_name: str) -> bool:
        """Delete all memories from a specific agent."""
        try:
            result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=[FieldCondition(key="agent", match=MatchValue(value=agent_name))]),
                with_payload=True
            )
            
            points_to_delete = []
            for point in result[0]:
                points_to_delete.append(point.id)
            
            if points_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=points_to_delete
                )
                logger.info(f"🗑️ Deleted {len(points_to_delete)} memories from agent '{agent_name}'")
                return True
            else:
                logger.warning(f"❌ No memories found for agent '{agent_name}'")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete memories by agent: {e}")
            return False

def main():
    """Interactive CLI for testing the memory system."""
    memory = LongTermMemory()
    
    print("🧠 Long-Term Memory System")
    print(f"📊 Current memories: {memory.get_memory_count()}")

    while True:
        print("\n" + "="*50)
        print("1. Add memory (with similarity check)")
        print("2. Add memory (force, skip similarity check)")
        print("3. Search memory") 
        print("4. Update memory by ID")
        print("5. Update memory by query")
        print("6. Delete memory by ID")
        print("7. Delete memory by query")
        print("8. Delete ALL memories (⚠️ DESTRUCTIVE)")
        print("9. Delete memories by agent")
        print("10. List all memories")
        print("11. Find similar memories")
        print("12. Set similarity threshold")
        print("13. Memory statistics")
        print("14. Exit")
        
        choice = input("\nChoose (1-14): ").strip()
        
        if choice == "1":
            time_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Remove last 3 microsecond digits
            agent = input("Agent name: ").strip() or "unknown"
            user_text = input("User: ").strip()
            assistant_text = input("Assistant: ").strip()
            
            # Optional custom threshold
            custom_threshold = input(f"Custom similarity threshold (default {memory.similarity_threshold}): ").strip()
            threshold = float(custom_threshold) if custom_threshold and custom_threshold.replace('.', '').isdigit() else None
            
            if user_text and assistant_text:
                success, message, similar_memory = memory.add_memory_with_similarity_check({
                    "timestamp_id": time_id,
                    "agent": agent,
                    "user": user_text,
                    "assistant": assistant_text
                }, similarity_threshold=threshold)
                
                print(message)
                
                if not success and similar_memory:
                    print(f"\n🔍 Found similar memory:")
                    print(f"   Score: {similar_memory['score']:.4f}")
                    print(f"   Agent: {similar_memory['agent']}")
                    print(f"   User: {similar_memory['user']}")
                    print(f"   Assistant: {similar_memory['assistant']}")
                    
                    force = input("\nForce add anyway? (y/N): ").strip().lower()
                    if force == 'y':
                        success = memory.add_memory({
                            "timestamp_id": time_id,
                            "agent": agent,
                            "user": user_text,
                            "assistant": assistant_text
                        })
                        if success:
                            print("✅ Memory force-added successfully")
                        else:
                            print("❌ Failed to force-add memory")
            else:
                print("❌ Both user and assistant text are required")
                
        elif choice == "2":
            time_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            agent = input("Agent name: ").strip() or "unknown"
            user_text = input("User: ").strip()
            assistant_text = input("Assistant: ").strip()
            
            if user_text and assistant_text:
                success = memory.add_memory({
                    "timestamp_id": time_id,
                    "agent": agent,
                    "user": user_text,
                    "assistant": assistant_text
                })
                if success:
                    print("✅ Memory added (similarity check skipped)")
                else:
                    print("❌ Failed to add memory")
            else:
                print("❌ Both user and assistant text are required")
                
        elif choice == "3":
            query = input("Search for: ").strip()
            if query:
                results = memory.search_memory(query, limit=5)
                print(f"\n🔍 Found {len(results)} results:")
                for i, r in enumerate(results, 1):
                    print(f"\n{i}. [{r['timestamp_id']}] Score: {r['score']:.4f}")
                    print(f"   Agent: {r['agent']}")
                    print(f"   User: {r['user']}")
                    print(f"   Assistant: {r['assistant']}")
                    
        elif choice == "4":
            ts_id = input("Enter timestamp ID to update: ").strip()
            if ts_id:
                print("Enter new values (leave empty to keep current):")
                user_text = input("New user text: ").strip()
                assistant_text = input("New assistant text: ").strip()
                agent_name = input("New agent name: ").strip()
                
                new_data = {}
                if user_text: new_data["user"] = user_text
                if assistant_text: new_data["assistant"] = assistant_text
                if agent_name: new_data["agent"] = agent_name
                
                if new_data:
                    success = memory.update_memory_by_id(ts_id, new_data)
                    if not success:
                        print("❌ Failed to update memory")
                else:
                    print("❌ No updates provided")
                    
        elif choice == "6":
            prev_query = input("Enter current user query to find: ").strip()
            if prev_query:
                print("Enter new values (leave empty to keep current):")
                user_text = input("New user text: ").strip()
                assistant_text = input("New assistant text: ").strip()
                agent_name = input("New agent name: ").strip()
                
                new_data = {}
                if user_text: new_data["user"] = user_text
                if assistant_text: new_data["assistant"] = assistant_text
                if agent_name: new_data["agent"] = agent_name
                
                if new_data:
                    success = memory.update_memory_by_query(prev_query, new_data)
                    if not success:
                        print("❌ Failed to update memory")
                else:
                    print("❌ No updates provided")
                    
        elif choice == "5":
            ts_id = input("Enter timestamp ID to delete: ").strip()
            if ts_id:
                success = memory.delete_memory_by_id(ts_id)
                if not success:
                    print("❌ Failed to delete memory")
                    
        elif choice == "7":
            query = input("Enter user query to delete: ").strip()
            if query:
                confirm = input(f"Are you sure you want to delete memories matching '{query}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    success = memory.delete_memory_by_query(query)
                    if not success:
                        print("❌ Failed to delete memory")
                else:
                    print("❌ Deletion cancelled")
                    
        elif choice == "8":
            print("⚠️  WARNING: This will DELETE ALL MEMORIES permanently!")
            confirm1 = input("Type 'DELETE ALL' to confirm: ").strip()
            if confirm1 == "DELETE ALL":
                confirm2 = input("Are you absolutely sure? (yes/no): ").strip().lower()
                if confirm2 == "yes":
                    success = memory.delete_all_memories()
                    if success:
                        print("✅ All memories have been deleted")
                    else:
                        print("❌ Failed to delete all memories")
                else:
                    print("❌ Deletion cancelled")
            else:
                print("❌ Deletion cancelled - incorrect confirmation")
                
        elif choice == "9":
            agent_name = input("Enter agent name to delete all memories from: ").strip()
            if agent_name:
                confirm = input(f"Delete ALL memories from agent '{agent_name}'? (y/N): ").strip().lower()
                if confirm == 'y':
                    success = memory.clear_memories_by_agent(agent_name)
                    if not success:
                        print("❌ Failed to delete memories")
                else:
                    print("❌ Deletion cancelled")
                    
        elif choice == "10":
            limit = input("Number of memories to show (default 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            
            memories = memory.get_all_memories(limit=limit)
            print(f"\n📋 Showing {len(memories)} memories:")
            
            for i, m in enumerate(memories, 1):
                print(f"\n{i}. [{m['timestamp_id']}] Agent: {m['agent']}")
                print(f"   User: {m['user']}")
                print(f"   Assistant: {m['assistant']}")
                
        elif choice == "11":
            query = input("Find memories similar to: ").strip()
            threshold = input("Similarity threshold (default 0.8): ").strip()
            threshold = float(threshold) if threshold and threshold.replace('.', '').isdigit() else 0.8
            
            if query:
                results = memory.find_similar_memories(query, threshold=threshold)
                print(f"\n🔍 Found {len(results)} similar memories (threshold: {threshold}):")
                
                for i, r in enumerate(results, 1):
                    print(f"\n{i}. [{r['timestamp_id']}] Score: {r['score']:.4f}")
                    print(f"   Agent: {r['agent']}")
                    print(f"   User: {r['user']}")
                    print(f"   Assistant: {r['assistant']}")
                    
        elif choice == "12":
            current = memory.similarity_threshold
            print(f"Current similarity threshold: {current}")
            new_threshold = input("Enter new threshold (0.0-1.0): ").strip()
            
            if new_threshold and new_threshold.replace('.', '').isdigit():
                success = memory.set_similarity_threshold(float(new_threshold))
                if not success:
                    print("❌ Invalid threshold value")
            else:
                print("❌ Please enter a valid number between 0.0 and 1.0")
                
        elif choice == "13":
            count = memory.get_memory_count()
            print(f"\n📊 Memory Statistics:")
            print(f"   Total memories: {count}")
            print(f"   Collection: {memory.collection_name}")
            print(f"   Embedding model: {memory.model}")
            print(f"   Vector dimension: {memory.embed_dim}")
            print(f"   Similarity threshold: {memory.similarity_threshold}")
            
        elif choice == "14":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please select 1-14.")

if __name__ == "__main__":
    main()
    
    
    
