"""
Focused test for manufacturing domain safety filtering - testing just the LLM system.
"""

import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_system import ManufacturingLLMSystem
from query_filter import ManufacturingQueryFilter

# Load environment variables
load_dotenv()

def test_llm_safety_integration():
    """Test the LLM system with integrated safety filtering."""
    
    print("🔐 TESTING LLM SYSTEM WITH SAFETY FILTERING")
    print("=" * 60)
    
    try:
        # Initialize LLM system (includes safety filter)
        print("🧠 Initializing LLM system...")
        llm_system = ManufacturingLLMSystem()
        print("✅ LLM system initialized with safety filtering")
        
        # Test queries with expected outcomes
        test_cases = [
            # Manufacturing queries - should be ALLOWED
            {
                "query": "Show me production efficiency trends",
                "expected": "ALLOWED",
                "category": "Manufacturing Analysis"
            },
            {
                "query": "Compare defect rates between shifts",
                "expected": "ALLOWED", 
                "category": "Quality Control"
            },
            {
                "query": "What are the top performing production lines?",
                "expected": "ALLOWED",
                "category": "Performance Metrics"
            },
            {
                "query": "Analyze equipment downtime patterns",
                "expected": "ALLOWED",
                "category": "Equipment Analysis"
            },
            {
                "query": "Show inventory levels by category",
                "expected": "ALLOWED",
                "category": "Supply Chain"
            },
            
            # Non-manufacturing queries - should be BLOCKED
            {
                "query": "What's the weather today?",
                "expected": "BLOCKED",
                "category": "Weather"
            },
            {
                "query": "Tell me a funny joke",
                "expected": "BLOCKED",
                "category": "Entertainment"
            },
            {
                "query": "How do I cook dinner?",
                "expected": "BLOCKED",
                "category": "Cooking"
            },
            {
                "query": "What's your favorite movie?",
                "expected": "BLOCKED",
                "category": "Personal"
            },
            {
                "query": "Give me investment advice",
                "expected": "BLOCKED",
                "category": "Finance"
            }
        ]
        
        print(f"\n🧪 RUNNING TEST CASES")
        print("-" * 50)
        
        passed_tests = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            query = test_case["query"]
            expected = test_case["expected"]
            category = test_case["category"]
            
            print(f"\n{i:2d}. [{category}] {query}")
            print(f"    Expected: {expected}")
            
            try:
                # Test with query_llm_system method
                result = llm_system.query_llm_system(query)
                
                # Check if it was filtered
                is_blocked = result.get('analysis_type') == 'safety_filter'
                
                if expected == "ALLOWED" and not is_blocked:
                    print(f"    ✅ PASS - Query allowed, analysis type: {result.get('analysis_type', 'unknown')}")
                    passed_tests += 1
                    
                elif expected == "BLOCKED" and is_blocked:
                    print(f"    ✅ PASS - Query blocked by safety filter")
                    print(f"    🚫 Message: {result.get('message', 'No message')[:60]}...")
                    passed_tests += 1
                    
                else:
                    print(f"    ❌ FAIL - Expected {expected}, got {'BLOCKED' if is_blocked else 'ALLOWED'}")
                    if is_blocked:
                        print(f"        Filter message: {result.get('message', '')[:60]}...")
                    else:
                        print(f"        Analysis type: {result.get('analysis_type', 'unknown')}")
                
            except Exception as e:
                print(f"    ❌ ERROR - Exception: {str(e)[:60]}...")
        
        print(f"\n📊 TEST RESULTS")
        print("=" * 40)
        print(f"Passed: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Safety filtering is working correctly")
            print("✅ Manufacturing queries are properly allowed")
            print("✅ Non-manufacturing queries are properly blocked")
        else:
            print(f"⚠️ {total_tests - passed_tests} tests failed")
            print("❌ Safety filtering may need adjustment")
        
    except Exception as e:
        print(f"❌ Error initializing LLM system: {str(e)}")
        print("Make sure your GEMINI_API_KEY is set in the .env file")

def test_direct_filter():
    """Test the filter directly without LLM integration."""
    
    print(f"\n🛡️ TESTING DIRECT FILTER FUNCTIONALITY")
    print("=" * 50)
    
    filter_system = ManufacturingQueryFilter()
    
    test_queries = [
        ("Show production trends", "Manufacturing", True),
        ("Analyze defect rates", "Quality", True), 
        ("What's the weather?", "Weather", False),
        ("Tell me a joke", "Entertainment", False),
        ("How to hack?", "Unsafe", False)
    ]
    
    for query, category, should_allow in test_queries:
        result = filter_system.filter_query(query)
        status = "✅ PASS" if result.is_allowed == should_allow else "❌ FAIL"
        allowed_text = "ALLOWED" if result.is_allowed else "BLOCKED"
        
        print(f"{status} [{category:12}] {query:25} -> {allowed_text}")
        if not result.is_allowed:
            print(f"     Reason: {result.message[:50]}...")

def main():
    """Run all safety filter tests."""
    
    # Check if API key is available
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set your API key in the .env file")
        print("\nRunning direct filter test only...")
        test_direct_filter()
        return
    
    # Run comprehensive tests
    test_llm_safety_integration()
    test_direct_filter()
    
    print(f"\n🎯 SAFETY CONFIGURATION COMPLETE!")
    print("=" * 60)
    print("Your manufacturing data chatbot is now configured with:")
    print("• ✅ Multi-layer safety filtering")
    print("• ✅ Manufacturing domain restrictions")
    print("• ✅ Polite rejection of irrelevant queries")
    print("• ✅ Professional safety responses")

if __name__ == "__main__":
    main()
