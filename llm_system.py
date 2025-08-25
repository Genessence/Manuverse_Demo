"""
LLM interaction module for manufacturing data chatbot.
Handles communication with Gemini LLM API for query processing and analysis instructions.
"""

import google.generativeai as genai
import json
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from query_filter import UniversalDataQueryFilter, FilterResponse

# Load environment variables
load_dotenv()


class ManufacturingLLMSystem:
    """
    Manufacturing-focused LLM system for processing user queries and generating
    data analysis instructions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM system with Gemini API and manufacturing-focused safety filters.
        
        Args:
            api_key (str, optional): Gemini API key. If None, loads from environment.
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize universal data query filter
        self.query_filter = UniversalDataQueryFilter()
        
        self.system_prompt = self._create_system_prompt()
    
    def generate_response(self, query: str, data_context: str = "", chart_info: str = "") -> str:
        """
        Generate response using Gemini with manufacturing domain safety filtering.
        
        Args:
            query (str): User's question or request
            data_context (str): Relevant data context and analysis
            chart_info (str): Information about any generated charts
            
        Returns:
            str: Generated response from the LLM or safety filter refusal message
        """
        # First, filter the query through manufacturing domain safety filter
        filter_result = self.query_filter.filter_query(query)
        
        if not filter_result.is_allowed:
            return filter_result.message
        
        try:
            # Construct the full prompt with context
            full_prompt = f"""
{self.system_prompt}

Data Context:
{data_context}

Chart Information:
{chart_info}

User Query: {query}

Please provide a comprehensive analysis and answer based on the manufacturing data provided.
"""
            
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your manufacturing-related query: {str(e)}"
    
    def _create_system_prompt(self) -> str:
        """
        Create the system prompt that guides Gemini to process manufacturing and industrial data queries only.
        
        Returns:
            str: System prompt for manufacturing-focused data analysis
        """
        return """
        You are a UNIVERSAL DATA ANALYSIS assistant. You can analyze ANY type of structured data:
        
        ✅ ALLOWED TOPICS:
        • ANY business data: Sales, marketing, finance, HR, operations
        • ANY scientific data: Research, experiments, measurements, surveys
        • ANY academic data: Studies, surveys, research findings
        • ANY operational data: Manufacturing, logistics, supply chain
        • ANY analytical data: Performance metrics, KPIs, benchmarks
        • ANY survey data: Customer feedback, employee surveys, market research
        • ANY time-series data: Trends, patterns, forecasting
        • ANY comparative data: Rankings, comparisons, segmentations
        
        🚫 STRICTLY PROHIBITED - ALWAYS REFUSE:
        • Personal questions, entertainment, or non-data topics
        • NSFW, harmful, illegal, or inappropriate content
        • Politics, religion, relationships, or personal advice
        • Medical advice, financial investment, or legal counsel
        • Weather, sports, cooking, travel, or general knowledge
        • Social media, gaming, movies, music, or celebrity topics
        
        📋 RESPONSE RULES:
        1. ONLY answer manufacturing and industrial data-related questions
                 2. If asked about anything outside data analysis domain, respond EXACTLY with:
            "I'm a universal data analysis assistant. I can help analyze any type of structured data including business metrics, scientific data, surveys, research findings, and more. Please ask a data-related question."
         3. For unsafe/inappropriate content, respond with:
            "I cannot assist with that type of content. Please ask questions about data analysis."
         4. Always focus on data analysis, visualization, and actionable insights for any dataset
         5. Provide specific, actionable analysis instructions in JSON format for valid queries
        
        When you receive manufacturing data context, use the actual column names in your response.
        
                 Provide a JSON response with this exact structure for VALID manufacturing queries:
         {
             "analysis_type": "ranking|trend_analysis|comparison|summary|correlation|distribution",
             "specific_query": "Restate what the user specifically wants to know",
             "filters": {
                 "date_range": {"start": null, "end": null},
                 "categories": {}
             },
             "primary_metric": "the main metric to analyze (use actual column name)",
             "grouping_column": "column to group by (use actual column name)", 
             "sort_by": "column to sort results by (use actual column name)",
             "sort_order": "desc|asc",
             "top_n": 10,
             "metrics": ["list of relevant columns to show"],
             "chart_type": "bar|line|scatter|pie|heatmap|none",
             "calculations": ["sum|mean|max|min|count"],
             "title": "Descriptive title for the specific analysis",
             "insights_focus": "What specific insights to highlight in results"
         }
         
         CHART DECISION RULES:
         - Use "none" for chart_type when user asks for summary, overview, or general information
         - Use "line" for trends over time
         - Use "bar" for comparisons and rankings
         - Use "scatter" for correlations
         - Use "pie" for proportions and distributions
         - Use "heatmap" for complex relationships
        
                 REMEMBER: You are a UNIVERSAL data analysis assistant. You can analyze ANY type of structured data. Focus on providing insights for whatever dataset is provided.
        """
    
    def query_llm_system(self, user_query: str, data_summary: Dict = None, column_metadata: Dict = None) -> Dict:
        """
        Send user query to Gemini LLM and receive structured instructions for analysis and charting.
        
        Args:
            user_query (str): User's question about the data
            data_summary (dict, optional): Summary of available data for context
            column_metadata (dict, optional): Column semantic information
            
        Returns:
            dict: Structured analysis instructions or safety filter response
        """
        # First, filter the query through manufacturing domain safety filter
        filter_result = self.query_filter.filter_query(user_query)
        
        if not filter_result.is_allowed:
            return {
                "analysis_type": "safety_filter",
                "error": "Query rejected by safety filter",
                "message": filter_result.message,
                "title": "Invalid Query"
            }
        
        # Enhance prompt with data context
        enhanced_prompt = self._enhance_prompt_with_context(user_query, data_summary, column_metadata)
        
        try:
            response = self.model.generate_content(enhanced_prompt)
            
            # Parse the response and extract JSON
            analysis_instructions = self._parse_llm_response(response.text)
            
            return analysis_instructions
            
        except Exception as e:
            print(f"Error querying LLM: {str(e)}")
            return self._create_fallback_response(user_query)
    
    def _enhance_prompt_with_context(self, user_query: str, data_summary: Dict = None, column_metadata: Dict = None) -> str:
        """
        Enhance the user query with data context and column information.
        
        Args:
            user_query (str): Original user query
            data_summary (dict, optional): Data summary for context
            column_metadata (dict, optional): Column semantic information
            
        Returns:
            str: Enhanced prompt with context
        """
        context_info = ""
        if data_summary:
            context_info = f"""
            
            Available data context:
            - Total records: {data_summary.get('total_records', 'Unknown')}
            - Available columns: {data_summary.get('available_columns', [])}
            """
            
            if data_summary.get('date_range'):
                context_info += f"""
            - Date range: {data_summary.get('date_range', {}).get('start', 'Unknown')} to {data_summary.get('date_range', {}).get('end', 'Unknown')}
                """
        
        column_info = ""
        if column_metadata:
            column_info = f"""
            
            Column semantic analysis:
            - Date columns: {column_metadata.get('date_columns', [])}
            - Numeric measures: {column_metadata.get('numeric_measures', [])}
            - Quality measures: {column_metadata.get('quality_measures', [])}
            - Efficiency measures: {column_metadata.get('efficiency_measures', [])}
            - Categorical columns: {column_metadata.get('categorical_columns', [])}
            - Time measures: {column_metadata.get('time_measures', [])}
            """
        

        
        enhanced_prompt = f"""
        {self.system_prompt}
        {context_info}
        {column_info}
        
        User Query: {user_query}
        
        Please analyze this query and provide structured JSON instructions for data filtering and visualization.
        Consider the semantic meaning of the columns when suggesting analysis approaches.
        """
        
        return enhanced_prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict:
        """
        Parse LLM response and extract JSON instructions.
        
        Args:
            response_text (str): Raw response from LLM
            
        Returns:
            dict: Parsed analysis instructions
        """
        try:
            # Try to find JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                # If no JSON found, create structured response from text
                return self._extract_instructions_from_text(response_text)
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return self._extract_instructions_from_text(response_text)
    
    def _extract_instructions_from_text(self, text: str) -> Dict:
        """
        Extract analysis instructions from plain text response.
        
        Args:
            text (str): Plain text response
            
        Returns:
            dict: Structured instructions
        """
        # Basic keyword-based extraction
        analysis_type = "trend_analysis"
        if any(word in text.lower() for word in ["compare", "comparison", "vs", "versus"]):
            analysis_type = "comparison"
        elif any(word in text.lower() for word in ["summary", "overview", "total"]):
            analysis_type = "summary"
        elif any(word in text.lower() for word in ["correlation", "relationship", "related"]):
            analysis_type = "correlation"
        
        chart_type = "line"
        if any(word in text.lower() for word in ["bar", "column"]):
            chart_type = "bar"
        elif any(word in text.lower() for word in ["scatter", "correlation"]):
            chart_type = "scatter"
        elif any(word in text.lower() for word in ["pie", "percentage", "proportion"]):
            chart_type = "pie"
        
        return {
            "analysis_type": analysis_type,
            "filters": {"date_range": {"start": None, "end": None}},
            "metrics": ["production", "defects"],
            "chart_type": chart_type,
            "grouping": "daily",
            "calculations": ["sum", "defect_rate"],
            "insights": "Analysis based on user query pattern matching",
            "title": "Manufacturing Data Analysis"
        }
    
    def _create_fallback_response(self, user_query: str) -> Dict:
        """
        Create a fallback response when LLM query fails.
        
        Args:
            user_query (str): Original user query
            
        Returns:
            dict: Basic analysis instructions
        """
        return {
            "analysis_type": "trend_analysis",
            "filters": {"date_range": {"start": None, "end": None}},
            "metrics": ["production", "defects", "efficiency"],
            "chart_type": "line",
            "grouping": "daily",
            "calculations": ["sum", "mean", "defect_rate"],
            "insights": f"Basic analysis for query: {user_query}",
            "title": "Manufacturing Performance Analysis"
        }
    
    def generate_insights(self, analysis_results: Dict, chart_path: str) -> str:
        """
        Generate textual insights based on analysis results.
        
        Args:
            analysis_results (dict): Results from data analysis
            chart_path (str): Path to generated chart
            
        Returns:
            str: Textual insights and recommendations
        """
        # Check if this is a column information query by looking at the data structure
        if 'column_metadata' in analysis_results or 'available_columns' in analysis_results:
            # Handle column information query specifically
            column_info = []
            
            # Get available columns
            available_columns = analysis_results.get('available_columns', [])
            if available_columns:
                column_info.append(f"📋 **All Columns ({len(available_columns)}):**")
                column_info.append(", ".join(available_columns))
                column_info.append("")
            
            # Get column metadata if available
            metadata = analysis_results.get('column_metadata', {})
            if metadata:
                column_info.append("🔍 **Column Analysis:**")
                for col_type, cols in metadata.items():
                    if cols and isinstance(cols, list):  # Only show non-empty column lists
                        column_info.append(f"• {col_type.replace('_', ' ').title()}: {', '.join(cols)}")
            
            if column_info:
                return "\n".join(column_info)
            else:
                return "Column information not available in the current analysis."
        
        # Convert DataFrames to readable format for the prompt
        def make_json_serializable(obj):
            """Recursively convert objects to JSON-serializable format"""
            if hasattr(obj, 'to_dict') and hasattr(obj, 'index'):  # DataFrame
                # Convert DataFrame to dict and process timestamps
                df_dict = obj.to_dict('records')
                return make_json_serializable(df_dict)
            elif isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            elif hasattr(obj, 'isoformat'):  # Timestamp/datetime objects
                return obj.isoformat()
            elif hasattr(obj, 'item'):  # numpy scalars
                return obj.item()
            elif isinstance(obj, (int, float, str, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        formatted_results = {}
        for key, value in analysis_results.items():
            try:
                if hasattr(value, 'to_dict') and hasattr(value, 'index'):  # It's a DataFrame
                    if len(value) > 0:
                        # Convert to a more readable format
                        if len(value) <= 20:  # Show all if small
                            formatted_results[key] = make_json_serializable(value)
                        else:  # Show top 10 if large
                            formatted_results[key] = make_json_serializable(value.head(10))
                            formatted_results[f"{key}_note"] = f"Showing top 10 of {len(value)} total records"
                    else:
                        formatted_results[key] = "No data available"
                else:
                    formatted_results[key] = make_json_serializable(value)
            except Exception as e:
                # If conversion fails, use string representation
                formatted_results[key] = f"Data: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}"

        insights_prompt = f"""
        You are a professional data analyst. Based on this data analysis, provide a clean, well-structured response:

        Data: {json.dumps(formatted_results, indent=2)}
        
        Format your response like this:
        
        📊 Summary
        [Brief overview of what the data shows]
        
        🔍 Key Insights
        • [First key finding]
        • [Second key finding]
        • [Third key finding]
        
        💡 What This Means
        [Business implications or recommendations]
        
        Keep it professional and clean. Use emojis sparingly and avoid markdown formatting. Don't mention technical details or file paths.
        """
        
        try:
            response = self.model.generate_content(insights_prompt)
            response_text = response.text
            
            # Clean up the response to remove any file paths or technical details
            if chart_path in response_text:
                response_text = response_text.replace(chart_path, "")
            
            # Remove any mentions of file paths or technical details
            response_text = response_text.replace("Chart saved at:", "")
            response_text = response_text.replace("Chart generated at:", "")
            
            # Clean up extra whitespace
            response_text = response_text.strip()
            
            return response_text
        except Exception as e:
            return f"Analysis completed successfully! Here's what I found in your data."


if __name__ == "__main__":
    # Test the LLM system
    try:
        llm_system = ManufacturingLLMSystem()
        
        # Test queries
        test_queries = [
            "Show me the production trend for the last week",
            "Compare defect rates between morning and evening shifts",
            "What's the efficiency of Line_2 compared to other lines?",
            "Show me days with highest downtime"
        ]
        
        for query in test_queries:
            print(f"\nQuery: {query}")
            result = llm_system.query_llm_system(query)
            print(f"Analysis Type: {result['analysis_type']}")
            print(f"Chart Type: {result['chart_type']}")
            print(f"Metrics: {result['metrics']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error testing LLM system: {e}")
        print("Make sure to set your GEMINI_API_KEY in the .env file")
