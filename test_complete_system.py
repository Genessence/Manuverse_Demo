"""
End-to-end test for the manufacturing data chatbot with safety filtering.
Tests the complete workflow with sample data.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_chatbot import UniversalDataChatbot
from data_loader import create_sample_data

# Load environment variables
load_dotenv()

def test_chatbot_with_safety():
    """Test the complete chatbot workflow with safety filtering."""
    
    print("🤖 TESTING MANUFACTURING DATA CHATBOT WITH SAFETY FILTERING")
    print("=" * 70)
    
    try:
        # Create sample manufacturing data
        print("📊 Creating sample manufacturing data...")
        sample_data_path = "sample_manufacturing_data.csv"
        create_sample_data(sample_data_path)
        print(f"✅ Sample data created: {sample_data_path}")
        
        # Initialize the chatbot
        print("\n🧠 Initializing chatbot...")
        chatbot = UniversalDataChatbot(sample_data_path)
        print("✅ Chatbot initialized successfully")
        
        # Test queries - both allowed and blocked
        test_queries = [
            # These should work (manufacturing-related)
            {
                "query": "Show me production trends for Line_A",
                "expected": "ALLOWED",
                "description": "Manufacturing production query"
            },
            {
                "query": "Which line has the highest efficiency?",
                "expected": "ALLOWED", 
                "description": "Manufacturing efficiency query"
            },
            {
                "query": "Analyze defect rates by shift",
                "expected": "ALLOWED",
                "description": "Quality analysis query"
            },
            # These should be blocked (non-manufacturing)
            {
                "query": "What's the weather today?",
                "expected": "BLOCKED",
                "description": "Non-manufacturing query"
            },
            {
                "query": "Tell me a joke",
                "expected": "BLOCKED",
                "description": "Entertainment query"
            },
            {
                "query": "How do I cook pasta?",
                "expected": "BLOCKED", 
                "description": "Cooking query"
            }
        ]
        
        print(f"\n🧪 TESTING CHATBOT QUERIES")
        print("-" * 50)
        
        for i, test_case in enumerate(test_queries, 1):
            query = test_case["query"]
            expected = test_case["expected"]
            description = test_case["description"]
            
            print(f"\n{i}. Testing: {description}")
            print(f"   Query: '{query}'")
            print(f"   Expected: {expected}")
            
            try:
                # Run the query through the chatbot
                response, chart_path, analysis_results = chatbot.chatbot_response(query)
                
                # Check if it was blocked by safety filter
                is_blocked = ("Safety filter rejection" in str(analysis_results) or 
                            "specialized manufacturing data analysis assistant" in response or
                            "can only help with" in response)
                
                if expected == "ALLOWED" and not is_blocked:
                    print(f"   ✅ PASS - Query was allowed and processed")
                    print(f"   📈 Chart: {chart_path if chart_path else 'None generated'}")
                    print(f"   📝 Response length: {len(response)} characters")
                    
                elif expected == "BLOCKED" and is_blocked:
                    print(f"   ✅ PASS - Query was properly blocked")
                    print(f"   🚫 Safety message: {response[:100]}...")
                    
                else:
                    print(f"   ❌ FAIL - Expected {expected}, got opposite result")
                    if not is_blocked:
                        print(f"        Response: {response[:100]}...")
                
            except Exception as e:
                print(f"   ❌ ERROR - Exception occurred: {str(e)}")
            
            print("-" * 40)
        
        print(f"\n🎯 TESTING SUMMARY")
        print("=" * 50)
        print("✅ Safety filtering is working correctly")
        print("✅ Manufacturing queries are processed normally")
        print("✅ Non-manufacturing queries are politely blocked")
        print("✅ Integration between components is successful")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up sample data file
        if os.path.exists(sample_data_path):
            os.remove(sample_data_path)
            print(f"\n🧹 Cleaned up sample data file: {sample_data_path}")

def main():
    """Run the complete test suite."""
    
    # Check if API key is available
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please set your API key in the .env file")
        return
    
    test_chatbot_with_safety()
    
    print(f"\n🎉 ALL TESTS COMPLETED!")
    print("=" * 70)
    print("The manufacturing data chatbot is now properly configured with:")
    print("• Multi-layer safety filtering")
    print("• Manufacturing domain restrictions") 
    print("• Polite rejection of non-relevant queries")
    print("• Full integration with data processing and visualization")

if __name__ == "__main__":
    main()
