"""
Main chatbot module for universal data analysis.
Integrates data processing, LLM interaction, and graph plotting for any dataset.
"""

import os
import sys
import pandas as pd
from typing import Tuple, Dict, Optional
import traceback

# Import our custom modules
from data_loader import load_manufacturing_data, validate_universal_columns, get_data_summary, create_sample_data
from llm_system import ManufacturingLLMSystem
from data_processor import UniversalDataProcessor
from chart_generator import ManufacturingChartGenerator


class UniversalDataChatbot:
    """
    Universal chatbot class integrating data processing, LLM interaction, and graph plotting
    for any type of dataset.
    """
    
    def __init__(self, data_file: str, api_key: Optional[str] = None):
        """
        Initialize the universal data chatbot.
        
        Args:
            data_file (str): Path to data file
            api_key (str, optional): Gemini API key
        """
        self.data_file = data_file
        self.data = None
        self.data_summary = None
        self.column_metadata = None
        
        # Initialize components
        try:
            self.llm_system = ManufacturingLLMSystem(api_key)
            self.data_processor = UniversalDataProcessor()
            self.chart_generator = ManufacturingChartGenerator()
            
            # Load and validate data
            self._load_data()
            
            print("Universal Data Chatbot initialized successfully!")
            print(f"Data loaded: {self.data.shape[0]} records with {self.data.shape[1]} columns")
            if self.data_summary.get('date_range'):
                print(f"Date range: {self.data_summary['date_range']['start']} to {self.data_summary['date_range']['end']}")
            
        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            raise
    
    def _load_data(self):
        """Load and prepare data with universal column analysis."""
        try:
            # Load raw data
            if self.data_file.endswith('.csv'):
                import pandas as pd
                raw_data = pd.read_csv(self.data_file)
            elif self.data_file.endswith(('.xlsx', '.xls')):
                import pandas as pd
                raw_data = pd.read_excel(self.data_file)
            else:
                raise ValueError("Unsupported file format")
            
            # Universal column validation and analysis
            self.data, self.column_metadata = validate_universal_columns(raw_data, self.llm_system)
            self.data_summary = self.get_universal_data_summary()
            
            print(f"Loaded {len(self.data)} records")
            print(f"Column analysis: {self.column_metadata['column_mapping']}")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def get_universal_data_summary(self) -> Dict:
        """Generate universal data summary based on column metadata."""
        summary = {
            'total_records': len(self.data),
            'available_columns': self.data.columns.tolist(),
            'column_metadata': self.column_metadata
        }
        
        # Date range if date columns exist
        date_columns = self.column_metadata.get('date_columns', [])
        if date_columns:
            date_col = date_columns[0]  # Use first date column
            summary['date_range'] = {
                'start': self.data[date_col].min().strftime('%Y-%m-%d') if pd.notna(self.data[date_col].min()) else None,
                'end': self.data[date_col].max().strftime('%Y-%m-%d') if pd.notna(self.data[date_col].max()) else None
            }
        
        # Numeric summaries
        numeric_cols = (self.column_metadata.get('numeric_measures', []) + 
                       self.column_metadata.get('quality_measures', []) + 
                       self.column_metadata.get('efficiency_measures', []))
        
        if numeric_cols:
            summary['numeric_summary'] = {}
            for col in numeric_cols:
                if col in self.data.columns:
                    summary['numeric_summary'][col] = {
                        'total': float(self.data[col].sum()),
                        'mean': float(self.data[col].mean()),
                        'max': float(self.data[col].max()),
                        'min': float(self.data[col].min()),
                        'std': float(self.data[col].std())
                    }
        
        # Categorical summaries
        categorical_cols = self.column_metadata.get('categorical_columns', [])
        if categorical_cols:
            summary['categorical_summary'] = {}
            for col in categorical_cols[:3]:  # Limit to first 3 categorical columns
                if col in self.data.columns:
                    value_counts = self.data[col].value_counts().head(5)  # Top 5 values
                    summary['categorical_summary'][col] = value_counts.to_dict()
        
        return summary
    
    def _get_default_metrics(self) -> list:
        """Get default metrics based on column analysis."""
        metrics = []
        
        # Add numeric measures
        metrics.extend(self.column_metadata.get('numeric_measures', []))
        metrics.extend(self.column_metadata.get('quality_measures', []))
        metrics.extend(self.column_metadata.get('efficiency_measures', []))
        
        # If no specific metrics found, use all numeric columns
        if not metrics:
            metrics = self.data.select_dtypes(include=['number']).columns.tolist()
        
        return metrics[:5]  # Limit to first 5 metrics
    
    def chatbot_response(self, user_query: str) -> Tuple[str, str, Dict]:
        """
        Main chatbot function integrating data processing, LLM interaction, and graph plotting.
        
        Args:
            user_query (str): User's question about manufacturing data
            
        Returns:
            tuple: (textual_response, chart_path, analysis_results)
        """
        try:
            print(f"\nProcessing query: {user_query}")
            
            # Step 1: Get analysis instructions from LLM (with safety filtering)
            print("1. Analyzing query with LLM...")
            analysis_instructions = self.llm_system.query_llm_system(
                user_query, self.data_summary, self.column_metadata
            )
            
            # Check if query was rejected by safety filter
            if analysis_instructions.get('analysis_type') == 'safety_filter':
                safety_message = analysis_instructions.get('message', 'Query not allowed.')
                print(f"   Query rejected by safety filter: {safety_message}")
                return safety_message, "", {"error": "Safety filter rejection"}
            
            print(f"   Analysis type: {analysis_instructions.get('analysis_type', 'unknown')}")
            print(f"   Chart type: {analysis_instructions.get('chart_type', 'unknown')}")
            
            # Step 2: Process data using new universal system
            print("2. Processing data with new universal system...")
            analysis_results = self.data_processor.process_query(
                self.data, 
                analysis_instructions, 
                self.column_metadata
            )
            
            if 'error' in analysis_results:
                return f"Analysis error: {analysis_results['error']}", "", {}
            
            if 'data' in analysis_results and not analysis_results['data'].empty:
                print(f"   Processed {len(analysis_results['data'])} records")
            else:
                print("   No specific data processing - using overview")
            
            # Step 3: Generate chart using processed data
            print("3. Generating chart...")
            if 'chart_data' in analysis_results:
                chart_data = analysis_results['chart_data']
                chart_config = {
                    'title': analysis_instructions.get('title', 'Data Analysis'),
                    'x_axis': analysis_results.get('x_column', chart_data.columns[0]),
                    'y_axis': [analysis_results.get('y_column', chart_data.columns[1])],
                    'chart_type': analysis_instructions.get('chart_type', 'bar')
                }
                
                chart_path = self.chart_generator.plot_manufacturing_data(
                    chart_data, chart_config
                )
            else:
                # Fallback to basic chart generation
                chart_data, chart_config = self.data_processor.prepare_chart_data(
                    self.data, analysis_instructions
                )
                chart_path = self.chart_generator.plot_manufacturing_data(
                    chart_data, chart_config
                )
            
            print(f"   Chart saved: {chart_path}")
            
            # Step 4: Generate textual response
            print("4. Generating insights...")
            if 'insights' in analysis_results:
                textual_response = analysis_results['insights']
            else:
                # Generate textual insights using LLM
                textual_response = self.llm_system.generate_insights(
                    analysis_results, chart_path
                )
            
            print("5. Analysis complete!")
            
            return textual_response, chart_path, analysis_results
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            return error_msg, "", {}
    
    def _compile_analysis_results(self, filtered_data, aggregated_data, instructions) -> Dict:
        """
        Compile analysis results for insight generation.
        
        Args:
            filtered_data: Original filtered data
            aggregated_data: Aggregated data for charts
            instructions: LLM analysis instructions
            
        Returns:
            dict: Compiled analysis results
        """
        metrics = instructions.get('metrics', ['production'])
        
        results = {
            'query_type': instructions.get('analysis_type', 'trend_analysis'),
            'date_range': {
                'start': filtered_data['date'].min().strftime('%Y-%m-%d') if 'date' in filtered_data.columns else 'N/A',
                'end': filtered_data['date'].max().strftime('%Y-%m-%d') if 'date' in filtered_data.columns else 'N/A',
                'days': len(filtered_data['date'].unique()) if 'date' in filtered_data.columns else 0
            },
            'records_analyzed': len(filtered_data),
            'metrics_summary': {}
        }
        
        # Calculate summary statistics for each metric
        for metric in metrics:
            if metric in filtered_data.columns:
                results['metrics_summary'][metric] = {
                    'total': float(filtered_data[metric].sum()),
                    'average': float(filtered_data[metric].mean()),
                    'max': float(filtered_data[metric].max()),
                    'min': float(filtered_data[metric].min()),
                    'std': float(filtered_data[metric].std())
                }
        
        # Add specific manufacturing insights
        if 'production' in filtered_data.columns and 'defects' in filtered_data.columns:
            total_production = filtered_data['production'].sum()
            total_defects = filtered_data['defects'].sum()
            
            results['quality_metrics'] = {
                'total_production': int(total_production),
                'total_defects': int(total_defects),
                'overall_defect_rate': float(total_defects / total_production * 100) if total_production > 0 else 0,
                'best_day': {
                    'date': filtered_data.loc[filtered_data['production'].idxmax(), 'date'].strftime('%Y-%m-%d') if 'date' in filtered_data.columns else 'N/A',
                    'production': int(filtered_data['production'].max())
                } if not filtered_data.empty else {},
                'worst_day': {
                    'date': filtered_data.loc[filtered_data['production'].idxmin(), 'date'].strftime('%Y-%m-%d') if 'date' in filtered_data.columns else 'N/A',
                    'production': int(filtered_data['production'].min())
                } if not filtered_data.empty else {}
            }
        
        # Add grouping-specific insights
        grouping = instructions.get('grouping', 'daily')
        if grouping == 'shift' and 'shift' in filtered_data.columns:
            shift_performance = filtered_data.groupby('shift').agg({
                'production': 'sum',
                'defects': 'sum',
                'efficiency': 'mean'
            }).round(2)
            
            results['shift_performance'] = shift_performance.to_dict('index')
            
        elif grouping == 'line' and 'line' in filtered_data.columns:
            line_performance = filtered_data.groupby('line').agg({
                'production': 'sum',
                'defects': 'sum',
                'efficiency': 'mean'
            }).round(2)
            
            results['line_performance'] = line_performance.to_dict('index')
        
        return results
    
    def get_available_metrics(self) -> list:
        """Get list of available metrics in the data."""
        if self.data is not None:
            return self.data.columns.tolist()
        return []
    
    def get_data_overview(self) -> str:
        """Get a formatted overview of the data."""
        if not self.data_summary:
            return "No data loaded."
        
        overview = f"""
        Universal Data Overview:
        
        📊 Dataset Information:
        - Total Records: {self.data_summary['total_records']:,}
        - Available Columns: {', '.join(self.data_summary['available_columns'])}
        
        🔍 Column Analysis:
        """
        
        # Add date information
        if self.column_metadata.get('date_columns'):
            overview += f"        - Date Columns: {', '.join(self.column_metadata['date_columns'])}\n"
            if self.data_summary.get('date_range'):
                overview += f"        - Date Range: {self.data_summary['date_range']['start']} to {self.data_summary['date_range']['end']}\n"
        
        # Add numeric measures
        if self.column_metadata.get('numeric_measures'):
            overview += f"        - Numeric Measures: {', '.join(self.column_metadata['numeric_measures'])}\n"
        
        # Add categorical columns
        if self.column_metadata.get('categorical_columns'):
            overview += f"        - Categories: {', '.join(self.column_metadata['categorical_columns'])}\n"
        
        # Add quality measures if any
        if self.column_metadata.get('quality_measures'):
            overview += f"        - Quality Measures: {', '.join(self.column_metadata['quality_measures'])}\n"
        
        # Add efficiency measures if any
        if self.column_metadata.get('efficiency_measures'):
            overview += f"        - Efficiency Measures: {', '.join(self.column_metadata['efficiency_measures'])}\n"
        
        # Add numeric summaries
        if self.data_summary.get('numeric_summary'):
            overview += "\n        📈 Key Metrics:\n"
            for col, stats in list(self.data_summary['numeric_summary'].items())[:3]:  # Show first 3
                overview += f"        - {col}: Total={stats['total']:,.0f}, Avg={stats['mean']:.1f}\n"
        
        # Add categorical summaries
        if self.data_summary.get('categorical_summary'):
            overview += "\n        🏷️ Categories:\n"
            for col, values in list(self.data_summary['categorical_summary'].items())[:2]:  # Show first 2
                top_value = max(values.items(), key=lambda x: x[1])
                overview += f"        - {col}: Most common = '{top_value[0]}' ({top_value[1]} records)\n"
        
        return overview


def run_interactive_chatbot(data_file: str):
    """
    Run the chatbot in interactive mode.
    
    Args:
        data_file (str): Path to manufacturing data file
    """
    try:
        # Initialize chatbot
        chatbot = UniversalDataChatbot(data_file)
        
        print("\n" + "="*60)
        print("🤖 MANUFACTURING DATA CHATBOT")
        print("="*60)
        print("Ask questions about your manufacturing data!")
        print("Type 'help' for examples, 'overview' for data summary, or 'quit' to exit.")
        print("="*60)
        
        while True:
            user_input = input("\n📝 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Thank you for using Manufacturing Data Chatbot.")
                break
            
            elif user_input.lower() == 'help':
                print("""
                🔍 Example Questions:
                
                📈 Trend Analysis:
                - "Show me the production trend for the last week"
                - "How has efficiency changed over time?"
                - "What's the defect trend for Line_2?"
                
                📊 Comparisons:
                - "Compare defect rates between morning and evening shifts"
                - "Which production line has the highest efficiency?"
                - "Show operator performance comparison"
                
                🎯 Specific Analysis:
                - "What days had the highest downtime?"
                - "Show correlation between production and defects"
                - "Analyze quality metrics for August"
                
                📋 Summary Reports:
                - "Give me a summary of last month's performance"
                - "Show overall production statistics"
                - "What's the average efficiency by shift?"
                """)
            
            elif user_input.lower() == 'overview':
                print(chatbot.get_data_overview())
            
            elif user_input:
                print("\n🔄 Processing your query...")
                response, chart_path, results = chatbot.chatbot_response(user_input)
                
                print("\n" + "="*50)
                print("📊 ANALYSIS RESULTS")
                print("="*50)
                print(response)
                
                if chart_path and os.path.exists(chart_path):
                    print(f"\n📈 Chart generated: {chart_path}")
                
                print("="*50)
            
            else:
                print("Please enter a question or type 'help' for examples.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thank you for using Manufacturing Data Chatbot.")
    except Exception as e:
        print(f"Error running chatbot: {e}")
        print("Please make sure your GEMINI_API_KEY is set in the .env file.")


if __name__ == "__main__":
    # Check if data file is provided
    if len(sys.argv) > 1:
        data_file_path = sys.argv[1]
    else:
        # Create sample data if no file provided
        print("No data file provided. Creating sample data...")
        data_file_path = create_sample_data()
        print(f"Sample data created: {data_file_path}")
    
    # Run the interactive chatbot
    run_interactive_chatbot(data_file_path)
