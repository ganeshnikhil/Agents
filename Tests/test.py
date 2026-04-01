"""
Architecture Testing Script for CognitiveDigitalTwin
Model-agnostic evaluation focusing on:
1. Routing correctness
2. Memory retention (STM/WM/LTM)
3. Context consistency
4. Latency
"""

import time
from Tests.main import CognitiveDigitalTwin

# -----------------------------
# Instantiate the Cognitive Twin
# -----------------------------
twin = CognitiveDigitalTwin(model="gemma3:4b", temperature=0)

# -----------------------------
# Test Queries
# -----------------------------
test_queries = [
    {"query": "Remember my appointment at 3 PM", "expected_memory": "STM"},
    {"query": "Add my friends Alice and Bob", "expected_memory": "LTM"},
    {"query": "What did I ask last?", "expected_memory": "WM"},
]

# -----------------------------
# 1. Routing Correctness Test
# -----------------------------
def test_routing_correctness(queries):
    correct = 0
    for q in queries:
        decision = twin.mem_in_out.gateway_router(q["query"])
        mem_type = None
        if decision.get("operation") == "memory_in":
            mem_type = twin.hippocampus_in.gateway_router(q["query"]).get("memory_type")
        elif decision.get("operation") == "memory_out":
            mem_type = twin.hippocampus_out.gateway_router(q["query"]).get("memory_type")
        elif decision.get("operation") == "cur":
            mem_type = "CUR"

        print(f"Query: {q['query']}, Routed to: {mem_type}")
        if mem_type == q["expected_memory"]:
            correct += 1

    accuracy = correct / len(queries)
    print(f"Routing correctness: {accuracy:.2f}")
    return accuracy

# -----------------------------
# 2. Memory Retention Test
# -----------------------------
def test_memory_retention():
    # STM test
    stm_id = "STM_test_001"
    twin.stm.add({"timestamp_id": stm_id, "user": "test_user", "assistant": "STM data"})
    retrieved_stm = twin.stm.search("test_user")
    print(f"STM retrieval: {retrieved_stm}")

    # WM test
    twin.working_memory.add({"timestamp_id": "WM_test_001", "user": "test_user", "assistant": "WM data"})
    retrieved_wm = twin.working_memory.retrieve_last()
    print(f"WM retrieval: {retrieved_wm}")

    # LTM test
    ltm_id = "LTM_test_001"
    twin.ltm.add_memory_with_similarity_check({"timestamp_id": ltm_id, "user": "test_user", "assistant": "LTM data"})
    retrieved_ltm = twin.ltm.search_memory("test_user")
    print(f"LTM retrieval: {retrieved_ltm}")

# -----------------------------
# 3. Context Consistency Test
# -----------------------------
def test_context_consistency():
    # Simulate multi-step query
    twin.stm.add({"timestamp_id": "STM_multi", "user": "user", "assistant": "recent info"})
    twin.ltm.add_memory_with_similarity_check({"timestamp_id": "LTM_multi", "user": "user", "assistant": "persistent info"})
    twin.working_memory.add({"timestamp_id": "WM_multi", "user": "user", "assistant": "last query"})

    # Process a query that should combine context
    result = twin.process_query("Summarize all my recent info", "TEST_TS_001", "AssistantBot")
    print(f"Combined context response: {result}")

# -----------------------------
# 4. Latency Test
# -----------------------------
def test_latency(num_queries=10):
    start = time.time()
    for i in range(num_queries):
        twin.process_query(f"Dummy query {i}", f"TS_{i}", "AssistantBot")
    end = time.time()
    avg_latency = (end - start) / num_queries
    print(f"Average latency per query: {avg_latency:.3f} sec")

# -----------------------------
# Run Tests
# -----------------------------
print("=== Twin-Memory Architecture Tests ===")
print("\n1. Routing Correctness Test")
test_routing_correctness(test_queries)

print("\n2. Memory Retention Test")
test_memory_retention()

print("\n3. Context Consistency Test")
test_context_consistency()

print("\n4. Latency Test")
test_latency()
