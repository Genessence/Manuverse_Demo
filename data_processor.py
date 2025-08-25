"""
Query parsing and data filtering module for manufacturing data chatbot.
Interprets LLM instructions and filters DataFrame accordingly.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import re


class UniversalDataProcessor:
    """
    Universal data processor that works with any dataset structure.
    Interprets LLM instructions and filters/analyzes DataFrame accordingly.
    """
    
    def __init__(self):
        self.df = None
        self.column_metadata = {}
    
    def process_query(self, df: pd.DataFrame, instructions: Dict, column_metadata: Dict = None) -> Dict:
        """
        Process user query based on LLM instructions and return analysis results.
        
        Args:
            df (pd.DataFrame): Original data
            instructions (dict): Analysis instructions from LLM
            column_metadata (dict): Column semantic information
            
        Returns:
            dict: Analysis results with processed data and insights
        """
        self.df = df.copy()
        self.column_metadata = column_metadata or {}
        
        analysis_type = instructions.get('analysis_type', 'summary')
        
        if analysis_type == 'ranking':
            return self._process_ranking_query(instructions)
        elif analysis_type == 'trend_analysis':
            return self._process_trend_query(instructions)
        elif analysis_type == 'comparison':
            return self._process_comparison_query(instructions)
        elif analysis_type == 'summary':
            return self._process_summary_query(instructions)
        else:
            return self._process_generic_query(instructions)
    
    def _process_ranking_query(self, instructions: Dict) -> Dict:
        """
        Process ranking queries like "What are the top performers?"
        
        Args:
            instructions (dict): Analysis instructions
            
        Returns:
            dict: Ranking analysis results
        """
        primary_metric = instructions.get('primary_metric', self._guess_primary_metric())
        grouping_column = instructions.get('grouping_column', self._guess_grouping_column())
        sort_order = instructions.get('sort_order', 'desc')
        top_n = instructions.get('top_n', 10)
        
        if not primary_metric or not grouping_column:
            return {'error': 'Could not identify metrics for ranking analysis'}
        
        # Group and aggregate data
        if grouping_column in self.df.columns and primary_metric in self.df.columns:
            grouped = self.df.groupby(grouping_column).agg({
                primary_metric: ['sum', 'mean', 'count'],
                **{col: 'mean' for col in self.df.select_dtypes(include=[np.number]).columns 
                   if col != primary_metric}
            }).reset_index()
            
            # Flatten column names
            new_columns = [grouping_column]
            for col in grouped.columns[1:]:
                if isinstance(col, tuple):
                    new_columns.append(f"{col[0]}_{col[1]}")
                else:
                    new_columns.append(col)
            grouped.columns = new_columns
            
            # Sort by primary metric
            sort_column = f"{primary_metric}_sum" if f"{primary_metric}_sum" in grouped.columns else f"{primary_metric}_mean"
            if sort_column in grouped.columns:
                grouped = grouped.sort_values(sort_column, ascending=(sort_order == 'asc'))
                top_results = grouped.head(top_n)
                
                return {
                    'analysis_type': 'ranking',
                    'data': top_results,
                    'primary_metric': primary_metric,
                    'grouping_column': grouping_column,
                    'insights': self._generate_ranking_insights(top_results, primary_metric, grouping_column, sort_column),
                    'chart_data': top_results,
                    'x_column': grouping_column,
                    'y_column': sort_column
                }
        
        return {'error': 'Could not perform ranking analysis with available data'}
    
    def _generate_ranking_insights(self, results: pd.DataFrame, metric: str, grouping: str, sort_col: str) -> str:
        """
        Generate specific insights for ranking results.
        """
        if results.empty:
            return "No data available for analysis."
        
        top_performer = results.iloc[0]
        top_value = top_performer[sort_col]
        
        if len(results) > 1:
            second_value = results.iloc[1][sort_col]
            difference = top_value - second_value
            pct_diff = (difference / second_value) * 100 if second_value != 0 else 0
            
            insights = f"""
**Top Performers Analysis:**

🏆 **#1 Top Performer:** {top_performer[grouping]} with {top_value:.2f} {metric}
📊 **Performance Gap:** {difference:.2f} ({pct_diff:.1f}% higher than #2)

**Top {min(len(results), 5)} Rankings:**
"""
            for i, row in results.head(5).iterrows():
                rank = i + 1
                value = row[sort_col]
                name = row[grouping]
                insights += f"{rank}. {name}: {value:.2f}\n"
                
            return insights
        else:
            return f"Top performer: {top_performer[grouping]} with {top_value:.2f} {metric}"
    
    def _guess_primary_metric(self) -> str:
        """
        Guess the primary performance metric from available columns.
        """
        # Performance-related column names (ordered by priority)
        performance_keywords = [
            'production', 'sales', 'revenue', 'profit', 'efficiency', 
            'performance', 'score', 'rating', 'volume', 'amount', 'total'
        ]
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for keyword in performance_keywords:
            for col in numeric_cols:
                if keyword in col.lower():
                    return col
        
        # If no keyword match, return first numeric column
        return numeric_cols[0] if len(numeric_cols) > 0 else None
    
    def _guess_grouping_column(self) -> str:
        """
        Guess the grouping column for ranking (entities to compare).
        """
        # Entity-related column names
        entity_keywords = [
            'operator', 'employee', 'worker', 'line', 'machine', 'product', 
            'category', 'type', 'name', 'id', 'department', 'team', 'shift'
        ]
        
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        for keyword in entity_keywords:
            for col in categorical_cols:
                if keyword in col.lower():
                    return col
        
    def _process_trend_query(self, instructions: Dict) -> Dict:
        """Process trend analysis queries."""
        # Implementation for trend queries
        return {'analysis_type': 'trend_analysis', 'data': self.df}
    
    def _process_comparison_query(self, instructions: Dict) -> Dict:
        """Process comparison queries."""
        # Implementation for comparison queries  
        return {'analysis_type': 'comparison', 'data': self.df}
    
    def _process_summary_query(self, instructions: Dict) -> Dict:
        """Process summary queries."""
        # Implementation for summary queries
        return {'analysis_type': 'summary', 'data': self.df}
    
    def _process_generic_query(self, instructions: Dict) -> Dict:
        """Process generic queries."""
        # Implementation for generic queries
        return {'analysis_type': 'generic', 'data': self.df}
    
    def filter_manufacturing_data(self, df: pd.DataFrame, 
                                filters: Dict, 
                                metrics: List[str]) -> pd.DataFrame:
        """
        Filter dataframe based on filters and selected metrics.
        
        Args:
            df (pd.DataFrame): Original data
            filters (dict): Filtering criteria from LLM
            metrics (list): List of metrics to include
            
        Returns:
            pd.DataFrame: Filtered and processed data
        """
        filtered_df = df.copy()
        
        # Apply date range filter if date columns exist
        if 'date_range' in filters and filters['date_range'] and isinstance(filters['date_range'], dict):
            filtered_df = self._apply_date_filter(filtered_df, filters['date_range'])
        
        # Apply categorical filters dynamically based on available columns
        categorical_filters = ['shifts', 'lines', 'operators', 'categories', 'groups']
        for filter_key in categorical_filters:
            if filter_key in filters:
                filter_values = filters[filter_key]
                # Check if filter_values is not empty and is a list
                if filter_values and isinstance(filter_values, list) and len(filter_values) > 0:
                    # Try to find matching column (singular form)
                    column_name = filter_key.rstrip('s')  # Remove 's' to get singular form
                    if column_name in filtered_df.columns:
                        # Use .isin() method properly to avoid Series ambiguity
                        mask = filtered_df[column_name].isin(filter_values)
                        filtered_df = filtered_df[mask]
        
        # Calculate derived metrics if applicable
        filtered_df = self._calculate_derived_metrics(filtered_df)
        
        # Select only requested metrics (plus essential columns)
        essential_cols = []
        
        # Add date columns if they exist
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        essential_cols.extend(date_cols)
        
        # Add categorical columns that might be needed for grouping
        categorical_cols = [col for col in df.columns if df[col].dtype == 'object' and col not in essential_cols]
        essential_cols.extend(categorical_cols[:3])  # Limit to first 3 categorical columns
        
        available_metrics = [m for m in metrics if m in filtered_df.columns]
        
        selected_columns = essential_cols + available_metrics
        selected_columns = [col for col in selected_columns if col in filtered_df.columns]
        
        # Ensure we have at least some columns
        if not selected_columns and len(filtered_df.columns) > 0:
            selected_columns = filtered_df.columns.tolist()
        
        return filtered_df[selected_columns]
    
    def _apply_date_filter(self, df: pd.DataFrame, date_range: Dict) -> pd.DataFrame:
        """
        Apply date range filtering to the DataFrame.
        
        Args:
            df (pd.DataFrame): Input data
            date_range (dict): Date range with 'start' and 'end' keys
            
        Returns:
            pd.DataFrame: Date-filtered data
        """
        if not date_range:
            return df
        
        # Find date column
        date_column = None
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                date_column = col
                break
        
        if not date_column:
            # No date column found, return original data
            return df
        
        start_date = date_range.get('start')
        end_date = date_range.get('end')
        
        # Handle relative date expressions
        if start_date:
            start_date = self._parse_date_expression(start_date, df, date_column)
        if end_date:
            end_date = self._parse_date_expression(end_date, df, date_column)
        
        # Apply filters using proper boolean masks to avoid Series ambiguity
        if start_date:
            # Ensure the date column is datetime type before comparison
            if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            mask = df[date_column] >= start_date
            df = df[mask]
        if end_date:
            # Ensure the date column is datetime type before comparison
            if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            mask = df[date_column] <= end_date
            df = df[mask]
        
        return df
    
    def _parse_date_expression(self, date_expr: str, df: pd.DataFrame, date_column: str = 'date') -> Optional[pd.Timestamp]:
        """
        Parse date expressions including relative dates like 'last week', 'last 7 days'.
        
        Args:
            date_expr (str): Date expression
            df (pd.DataFrame): Data for context
            date_column (str): Name of the date column
            
        Returns:
            pd.Timestamp: Parsed date
        """
        if not date_expr:
            return None
        
        # If it's already a valid date format
        try:
            return pd.to_datetime(date_expr)
        except:
            pass
        
        # Handle relative expressions
        try:
            if not df.empty and date_column in df.columns:
                # Ensure the column is datetime type
                if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
                    # Try to convert to datetime
                    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
                
                # Get max date, handling any remaining NaT values
                max_date = df[date_column].max()
                if pd.isna(max_date):
                    today = pd.Timestamp.now()
                else:
                    today = max_date
            else:
                today = pd.Timestamp.now()
        except Exception as e:
            print(f"Warning: Could not get max date from {date_column}: {e}")
            today = pd.Timestamp.now()
        
        if 'last week' in date_expr.lower():
            return today - timedelta(days=7)
        elif 'last month' in date_expr.lower():
            return today - timedelta(days=30)
        elif 'last' in date_expr.lower() and 'days' in date_expr.lower():
            # Extract number of days
            match = re.search(r'(\d+)\s*days?', date_expr.lower())
            if match:
                days = int(match.group(1))
                return today - timedelta(days=days)
        elif 'yesterday' in date_expr.lower():
            return today - timedelta(days=1)
        elif 'today' in date_expr.lower():
            return today
        
        return None
    
    def _calculate_derived_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived metrics based on available columns.
        
        Args:
            df (pd.DataFrame): Input data
            
        Returns:
            pd.DataFrame: Data with calculated metrics
        """
        df = df.copy()
        
        # Get numeric columns for calculations
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Calculate derived metrics only if the required columns exist
        if 'defects' in df.columns and 'production' in df.columns:
            df['defect_rate'] = (df['defects'] / df['production'] * 100).fillna(0)
            df['quality_score'] = 100 - df['defect_rate']
        
        if 'production' in df.columns:
            df['total_production'] = df['production']
            # Calculate production per hour (assuming 8-hour shifts)
            df['production_per_hour'] = df['production'] / 8
        
        if 'efficiency' in df.columns:
            df['avg_efficiency'] = df['efficiency']
        
        # Add generic derived metrics for any numeric columns
        for col in numeric_cols:
            if col not in ['defect_rate', 'quality_score', 'total_production', 'production_per_hour', 'avg_efficiency']:
                try:
                    # Ensure the column is numeric and handle mixed types
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    total = numeric_series.sum()
                    if total > 0 and not pd.isna(total):
                        df[f'{col}_percentage'] = (numeric_series / total * 100).fillna(0)
                except Exception as e:
                    print(f"Warning: Could not calculate percentage for {col}: {e}")
                    continue
        
        return df
    
    def aggregate_data(self, df: pd.DataFrame, 
                      grouping: str, 
                      calculations: List[str]) -> pd.DataFrame:
        """
        Aggregate data based on grouping criteria and calculations.
        
        Args:
            df (pd.DataFrame): Filtered data
            grouping (str): Grouping method (daily, weekly, shift, etc.)
            calculations (list): List of aggregation functions
            
        Returns:
            pd.DataFrame: Aggregated data
        """
        if df.empty:
            return df
        
        # Define grouping columns
        group_cols = self._get_grouping_columns(grouping, df)
        
        if not group_cols:
            return df
        
        # Define aggregation functions
        agg_funcs = self._get_aggregation_functions(calculations, df)
        
        try:
            # Group and aggregate
            grouped_df = df.groupby(group_cols).agg(agg_funcs).reset_index()
            
            # Flatten column names if multi-level
            if isinstance(grouped_df.columns, pd.MultiIndex):
                grouped_df.columns = ['_'.join(col).strip('_') for col in grouped_df.columns]
            
            return grouped_df
            
        except Exception as e:
            print(f"Aggregation error: {e}")
            return df
    
    def _get_grouping_columns(self, grouping: str, df: pd.DataFrame) -> List[str]:
        """
        Get appropriate columns for grouping based on grouping type.
        
        Args:
            grouping (str): Grouping method
            df (pd.DataFrame): Input data
            
        Returns:
            list: List of columns to group by
        """
        available_cols = df.columns.tolist()
        
        # Find date column dynamically
        date_col = None
        for col in available_cols:
            if 'date' in col.lower() or 'time' in col.lower():
                date_col = col
                break
        
        if grouping == 'daily':
            return [date_col] if date_col else []
        elif grouping == 'weekly':
            # Add week column
            if date_col:
                df['week'] = df[date_col].dt.isocalendar().week
                return ['week']
        elif grouping == 'monthly':
            # Add month column
            if date_col:
                df['month'] = df[date_col].dt.to_period('M')
                return ['month']
        elif grouping == 'shift':
            # Look for shift-related columns
            shift_cols = [col for col in available_cols if 'shift' in col.lower()]
            return shift_cols[:1] if shift_cols else []
        elif grouping == 'line':
            # Look for line-related columns
            line_cols = [col for col in available_cols if 'line' in col.lower()]
            return line_cols[:1] if line_cols else []
        elif grouping == 'operator':
            # Look for operator-related columns
            operator_cols = [col for col in available_cols if 'operator' in col.lower() or 'worker' in col.lower()]
            return operator_cols[:1] if operator_cols else []
        
        return []
    
    def _get_aggregation_functions(self, calculations: List[str], df: pd.DataFrame) -> Dict:
        """
        Get aggregation functions based on calculation requirements.
        
        Args:
            calculations (list): List of calculation types
            df (pd.DataFrame): Input data
            
        Returns:
            dict: Aggregation functions mapping
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        agg_dict = {}
        
        for col in numeric_cols:
            col_funcs = []
            
            if 'sum' in calculations:
                col_funcs.append('sum')
            if 'mean' in calculations or 'average' in calculations:
                col_funcs.append('mean')
            if 'max' in calculations:
                col_funcs.append('max')
            if 'min' in calculations:
                col_funcs.append('min')
            if 'count' in calculations:
                col_funcs.append('count')
            
            # Default to sum for production-type metrics, mean for rates/percentages
            if not col_funcs:
                if col in ['production', 'defects', 'downtime']:
                    col_funcs = ['sum']
                elif col in ['efficiency', 'defect_rate', 'quality_score']:
                    col_funcs = ['mean']
                else:
                    col_funcs = ['sum']
            
            agg_dict[col] = col_funcs[0] if len(col_funcs) == 1 else col_funcs
        
        return agg_dict
    
    def prepare_chart_data(self, df: pd.DataFrame, 
                          analysis_instructions: Dict) -> Tuple[pd.DataFrame, Dict]:
        """
        Prepare data specifically for chart generation based on analysis instructions.
        
        Args:
            df (pd.DataFrame): Processed data
            analysis_instructions (dict): LLM analysis instructions
            
        Returns:
            tuple: (chart_data, chart_config)
        """
        chart_type = analysis_instructions.get('chart_type', 'line')
        grouping = analysis_instructions.get('grouping', 'daily')
        metrics = analysis_instructions.get('metrics', ['production'])
        
        # Aggregate data for charting
        chart_data = self.aggregate_data(df, grouping, ['sum', 'mean'])
        
        # Prepare chart configuration
        chart_config = {
            'title': analysis_instructions.get('title', 'Manufacturing Analysis'),
            'x_axis': self._get_x_axis_column(grouping, chart_data),
            'y_axis': metrics,
            'chart_type': chart_type,
            'grouping': grouping
        }
        
        return chart_data, chart_config
    
    def _get_x_axis_column(self, grouping: str, df: pd.DataFrame) -> str:
        """
        Get the appropriate X-axis column based on grouping.
        
        Args:
            grouping (str): Grouping method
            df (pd.DataFrame): Chart data
            
        Returns:
            str: Column name for X-axis
        """
        if grouping == 'daily' and 'date' in df.columns:
            return 'date'
        elif grouping == 'weekly' and 'week' in df.columns:
            return 'week'
        elif grouping == 'monthly' and 'month' in df.columns:
            return 'month'
        elif grouping == 'shift' and 'shift' in df.columns:
            return 'shift'
        elif grouping == 'line' and 'line' in df.columns:
            return 'line'
        elif grouping == 'operator' and 'operator' in df.columns:
            return 'operator'
        
        # Default to first non-numeric column
        for col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                return col
        
        return df.columns[0] if len(df.columns) > 0 else 'index'


if __name__ == "__main__":
    # Test the data processor with sample data
    try:
        from data_loader import load_manufacturing_data, create_sample_data
        
        # Create and load sample data
        sample_file = create_sample_data()
        df = load_manufacturing_data(sample_file)
        
        # Initialize processor
        processor = UniversalDataProcessor()
        
        # Test ranking query
        test_instructions = {
            'analysis_type': 'ranking',
            'primary_metric': 'production',
            'grouping_column': 'operator',
            'sort_order': 'desc',
            'top_n': 5
        }
        
        result = processor.process_query(df, test_instructions)
        
        print(f"Analysis type: {result.get('analysis_type')}")
        print(f"Top performers:")
        if 'data' in result:
            print(result['data'].head())
        if 'insights' in result:
            print(result['insights'])
        
    except Exception as e:
        print(f"Error testing data processor: {e}")
