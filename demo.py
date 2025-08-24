"""
Demo script for Manufacturing Data Chatbot.
Shows examples of how to use the chatbot programmatically.
"""

import os
import sys
from datetime import datetime

def demo_chatbot():
    """Demonstrate the chatbot functionality."""
    
    print("🤖 Manufacturing Data Chatbot - Demo")
    print("=" * 60)
    
    try:
        # Import our chatbot modules
        from main_chatbot import ManufacturingDataChatbot
        from data_loader import create_sample_data
        
        # Create sample data
        print("1. Creating sample manufacturing data...")
        sample_file = create_sample_data("demo_data.csv")
        print(f"   ✅ Sample data created: {sample_file}")
        
        # Initialize chatbot
        print("\n2. Initializing chatbot...")
        chatbot = ManufacturingDataChatbot(sample_file)
        print("   ✅ Chatbot initialized successfully!")
        
        # Show data overview
        print("\n3. Data Overview:")
        print(chatbot.get_data_overview())
        
        # Demo queries
        demo_queries = [
            "Show me the production trend for the last week",
            "Compare defect rates between different shifts",
            "Which production line has the best efficiency?",
            "Show me the correlation between production and defects"
        ]
        
        print("\n4. Running Demo Queries:")
        print("=" * 40)
        
        for i, query in enumerate(demo_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("   Processing...")
            
            try:
                response, chart_path, results = chatbot.chatbot_response(query)
                
                print(f"   ✅ Analysis completed!")
                print(f"   📈 Chart: {os.path.basename(chart_path) if chart_path else 'None'}")
                print(f"   📊 Records analyzed: {results.get('records_analyzed', 'N/A')}")
                
                # Show brief insights
                if 'quality_metrics' in results:
                    defect_rate = results['quality_metrics'].get('overall_defect_rate', 0)
                    print(f"   🎯 Overall defect rate: {defect_rate:.2f}%")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Demo completed!")
        print(f"📁 Charts saved in: {os.path.abspath('charts')}")
        
        # List generated charts
        chart_dir = "charts"
        if os.path.exists(chart_dir):
            charts = [f for f in os.listdir(chart_dir) if f.endswith('.png')]
            if charts:
                print(f"📈 Generated {len(charts)} charts:")
                for chart in sorted(charts)[-3:]:  # Show last 3 charts
                    print(f"   - {chart}")
                if len(charts) > 3:
                    print(f"   ... and {len(charts) - 3} more")
        
        # Clean up
        if os.path.exists("demo_data.csv"):
            os.remove("demo_data.csv")
            print("🧹 Cleaned up demo data file")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Please check your Gemini API key configuration in the .env file")

def show_usage_examples():
    """Show usage examples."""
    print("\n📚 Usage Examples:")
    print("=" * 30)
    
    print("\n1. Command Line Usage:")
    print("   # With sample data")
    print("   python main_chatbot.py")
    print()
    print("   # With your own data")
    print("   python main_chatbot.py your_data.csv")
    
    print("\n2. Programmatic Usage:")
    print("""
    from main_chatbot import ManufacturingDataChatbot
    
    # Initialize chatbot
    chatbot = ManufacturingDataChatbot("your_data.csv")
    
    # Ask a question
    response, chart_path, results = chatbot.chatbot_response(
        "Show me production trends for last month"
    )
    
    print(response)  # Textual insights
    print(f"Chart saved: {chart_path}")  # Chart file path
    print(results)   # Detailed analysis results
    """)
    
    print("\n3. Example Questions:")
    examples = [
        "Production Analysis:",
        "- Show me daily production for August 2024",
        "- What's the average production per shift?",
        "- Which days had production above 1000 units?",
        "",
        "Quality Analysis:",
        "- Compare defect rates between morning and evening shifts",
        "- Show me the defect trend for the last two weeks",
        "- Which production line has the lowest defect rate?",
        "",
        "Efficiency Analysis:",
        "- Show efficiency trends over time",
        "- Compare efficiency between different operators",
        "- What's the correlation between efficiency and production?",
        "",
        "Operational Analysis:",
        "- Show me days with highest downtime",
        "- Compare performance across production lines",
        "- What's the overall equipment effectiveness?"
    ]
    
    for example in examples:
        if example.endswith(":"):
            print(f"\n{example}")
        else:
            print(f"   {example}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        show_usage_examples()
    else:
        demo_chatbot()
