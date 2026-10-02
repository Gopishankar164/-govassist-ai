import sys
from tests.test_rag import test_rag_pipeline_search, test_rag_pipeline_grounded_context
from tests.test_agents import test_profile_extraction_agent, test_query_rewriter_agent, test_eligibility_agent, test_langgraph_engine_execution
from tests.test_database import test_database_insert_and_find, test_database_schemes_collection
from tests.test_api import test_health_endpoint, test_schemes_list_endpoint, test_agent_chat_endpoint

def main():
    print("==========================================")
    print(" RUNNING AUTOMATED SUITE (UNIT + INTEGRATION)")
    print("==========================================")

    tests = [
        ("test_rag_pipeline_search", test_rag_pipeline_search),
        ("test_rag_pipeline_grounded_context", test_rag_pipeline_grounded_context),
        ("test_profile_extraction_agent", test_profile_extraction_agent),
        ("test_query_rewriter_agent", test_query_rewriter_agent),
        ("test_eligibility_agent", test_eligibility_agent),
        ("test_langgraph_engine_execution", test_langgraph_engine_execution),
        ("test_database_insert_and_find", test_database_insert_and_find),
        ("test_database_schemes_collection", test_database_schemes_collection),
        ("test_health_endpoint", test_health_endpoint),
        ("test_schemes_list_endpoint", test_schemes_list_endpoint),
        ("test_agent_chat_endpoint", test_agent_chat_endpoint)
    ]

    passed = 0
    failed = 0

    for name, fn in tests:
        try:
            fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed += 1

    print("==========================================")
    print(f" RESULT: {passed} PASSED, {failed} FAILED")
    print("==========================================")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
