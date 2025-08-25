"""
Data loading module for manufacturing data chatbot.
Handles loading CSV/Excel files and validates manufacturing data structure.
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Tuple, Dict
import os
from pathlib import Path
import json


def load_manufacturing_data(file_path: str) -> pd.DataFrame:
    """
    Load manufacturing data from CSV or Excel and validate columns like date, production, defects.
    
    Args:
        file_path (str): Path to the data file (CSV or Excel)
        
    Returns:
        pd.DataFrame: Validated manufacturing data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If required columns are missing
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    # Determine file type and load data
    file_extension = Path(file_path).suffix.lower()
    
    try:
        if file_extension == '.csv':
            df = pd.read_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
            
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")
    
    # Validate and analyze columns universally
    df, metadata = validate_universal_columns(df)
    
    # Convert date column to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
    # Remove rows with invalid dates
    df = df.dropna(subset=['date'])
    
    return df


def analyze_columns_with_llm(df: pd.DataFrame, llm_system=None) -> Dict[str, str]:
    """
    Use LLM to analyze and identify column types in any dataset.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        llm_system: LLM system for analysis
        
    Returns:
        dict: Mapping of column names to their identified types
    """
    if llm_system is None:
        # Fallback to rule-based detection if no LLM available
        return detect_columns_by_rules(df)
    
    try:
        # Prepare column information for LLM
        column_info = []
        for col in df.columns:
            sample_values = df[col].dropna().head(5).tolist()
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            
            column_info.append({
                'name': col,
                'data_type': dtype,
                'sample_values': sample_values,
                'null_count': null_count,
                'unique_values': df[col].nunique()
            })
        
        prompt = f"""
        Analyze the following dataset columns and identify their business meaning.
        Return a JSON mapping of column names to their semantic types.
        
        Available semantic types:
        - 'date': Date/time columns
        - 'numeric_measure': Quantities, amounts, counts (production, sales, revenue, etc.)
        - 'quality_measure': Quality metrics (defects, errors, failures, etc.)
        - 'efficiency_measure': Efficiency/performance metrics (percentages, rates, etc.)
        - 'categorical': Categories, groups, classifications
        - 'identifier': IDs, names, codes
        - 'time_measure': Time-based measures (duration, downtime, etc.)
        - 'other': Anything that doesn't fit above categories
        
        Column Information:
        {column_info}
        
        Respond with only a JSON object like:
        {{"column_name": "semantic_type", ...}}
        """
        
        response = llm_system.model.generate_content(prompt)
        
        # Parse JSON response
        import json
        json_start = response.text.find('{')
        json_end = response.text.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response.text[json_start:json_end]
            column_mapping = json.loads(json_str)
            return column_mapping
        else:
            return detect_columns_by_rules(df)
            
    except Exception as e:
        print(f"LLM column analysis failed: {e}")
        return detect_columns_by_rules(df)

def detect_columns_by_rules(df: pd.DataFrame) -> Dict[str, str]:
    """
    Rule-based column type detection as fallback.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        dict: Mapping of column names to their identified types
    """
    column_mapping = {}
    
    for col in df.columns:
        col_lower = col.lower()
        sample_values = df[col].dropna().head(10)
        
        # Date detection
        if any(keyword in col_lower for keyword in ['date', 'time', 'timestamp', 'day', 'month', 'year']):
            column_mapping[col] = 'date'
        # Try to parse as date
        elif df[col].dtype == 'object':
            try:
                pd.to_datetime(sample_values.iloc[0] if len(sample_values) > 0 else None)
                column_mapping[col] = 'date'
                continue
            except:
                pass
        
        if column_mapping.get(col):
            continue
            
        # Numeric measures - Universal detection
        if pd.api.types.is_numeric_dtype(df[col]):
            if any(keyword in col_lower for keyword in [
                'production', 'output', 'volume', 'quantity', 'count', 'amount', 
                'sales', 'revenue', 'units', 'total', 'sum', 'value', 'score',
                'measurement', 'result', 'data', 'number', 'level', 'concentration'
            ]):
                column_mapping[col] = 'numeric_measure'
            elif any(keyword in col_lower for keyword in [
                'defect', 'error', 'fault', 'failure', 'reject', 'waste', 'scrap',
                'negative', 'problem', 'issue'
            ]):
                column_mapping[col] = 'quality_measure'
            elif any(keyword in col_lower for keyword in [
                'efficiency', 'rate', 'percent', '%', 'ratio', 'performance',
                'percentage', 'proportion', 'share'
            ]):
                column_mapping[col] = 'efficiency_measure'
            elif any(keyword in col_lower for keyword in [
                'time', 'duration', 'downtime', 'uptime', 'minutes', 'hours',
                'period', 'interval', 'cycle'
            ]):
                column_mapping[col] = 'time_measure'
            else:
                column_mapping[col] = 'numeric_measure'
        
        # Categorical detection
        elif df[col].dtype == 'object' or df[col].dtype.name == 'category':
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.1 or df[col].nunique() < 20:  # Low cardinality
                column_mapping[col] = 'categorical'
            else:
                column_mapping[col] = 'identifier'
        
        # Default
        else:
            column_mapping[col] = 'other'
    
    return column_mapping

def validate_universal_columns(df: pd.DataFrame, llm_system=None) -> Tuple[pd.DataFrame, Dict]:
    """
    Universal column validation that works with any dataset.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        llm_system: Optional LLM system for intelligent analysis
        
    Returns:
        tuple: (processed_dataframe, column_metadata)
    """
    # Analyze columns
    column_mapping = analyze_columns_with_llm(df, llm_system)
    
    processed_df = df.copy()
    
    # Convert date columns
    date_columns = [col for col, type_ in column_mapping.items() if type_ == 'date']
    for date_col in date_columns:
        try:
            processed_df[date_col] = pd.to_datetime(processed_df[date_col], errors='coerce')
        except Exception as e:
            print(f"Warning: Could not convert {date_col} to datetime: {e}")
    
    # Clean up mixed data types in numeric columns
    numeric_columns = [col for col, type_ in column_mapping.items() if type_ in ['numeric_measure', 'quality_measure', 'efficiency_measure', 'time_measure']]
    for num_col in numeric_columns:
        try:
            # Convert to numeric, coercing errors to NaN
            processed_df[num_col] = pd.to_numeric(processed_df[num_col], errors='coerce')
            
            # Replace infinite values with NaN
            processed_df[num_col] = processed_df[num_col].replace([np.inf, -np.inf], np.nan)
            
        except Exception as e:
            print(f"Warning: Could not convert {num_col} to numeric: {e}")
    
    # Create metadata
    metadata = {
        'column_mapping': column_mapping,
        'date_columns': date_columns,
        'numeric_measures': [col for col, type_ in column_mapping.items() if type_ == 'numeric_measure'],
        'quality_measures': [col for col, type_ in column_mapping.items() if type_ == 'quality_measure'],
        'efficiency_measures': [col for col, type_ in column_mapping.items() if type_ == 'efficiency_measure'],
        'categorical_columns': [col for col, type_ in column_mapping.items() if type_ == 'categorical'],
        'time_measures': [col for col, type_ in column_mapping.items() if type_ == 'time_measure']
    }
    
    return processed_df, metadata


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Generate a summary of the manufacturing data for LLM context.
    
    Args:
        df (pd.DataFrame): Manufacturing data
        
    Returns:
        dict: Summary statistics and metadata
    """
    summary = {
        'total_records': len(df),
        'date_range': {
            'start': df['date'].min().strftime('%Y-%m-%d') if not df.empty else None,
            'end': df['date'].max().strftime('%Y-%m-%d') if not df.empty else None
        },
        'production_stats': {
            'total_production': df['production'].sum(),
            'avg_daily_production': df['production'].mean(),
            'max_production': df['production'].max(),
            'min_production': df['production'].min()
        },
        'quality_stats': {
            'total_defects': df['defects'].sum(),
            'avg_defect_rate': (df['defects'].sum() / df['production'].sum() * 100) if df['production'].sum() > 0 else 0,
            'max_defects': df['defects'].max(),
            'days_with_defects': len(df[df['defects'] > 0])
        },
        'available_columns': df.columns.tolist(),
        'shifts': df['shift'].unique().tolist() if 'shift' in df.columns else [],
        'production_lines': df['line'].unique().tolist() if 'line' in df.columns else []
    }
    
    return summary


def create_sample_data(output_path: str = "sample_manufacturing_data.csv") -> str:
    """
    Create sample manufacturing data for testing the chatbot.
    
    Args:
        output_path (str): Path where to save the sample data
        
    Returns:
        str: Path to the created sample file
    """
    # Generate sample data for the last 30 days
    dates = pd.date_range(start='2024-07-01', end='2024-08-21', freq='D')
    np.random.seed(42)  # For reproducible results
    
    sample_data = []
    for date in dates:
        # Simulate different shifts
        for shift in ['Morning', 'Evening', 'Night']:
            production = np.random.normal(1000, 150)  # Normal distribution around 1000 units
            production = max(0, int(production))  # Ensure non-negative
            
            # Defect rate varies by shift (night shift has slightly higher defect rate)
            base_defect_rate = 0.02 if shift != 'Night' else 0.035
            defects = np.random.poisson(production * base_defect_rate)
            
            efficiency = np.random.normal(92, 8)  # Efficiency around 92%
            efficiency = np.clip(efficiency, 70, 100)
            
            downtime = np.random.exponential(15)  # Exponential distribution for downtime
            downtime = min(downtime, 120)  # Cap at 2 hours
            
            sample_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'shift': shift,
                'line': f'Line_{np.random.choice([1, 2, 3])}',
                'production': production,
                'defects': defects,
                'efficiency': round(efficiency, 2),
                'downtime': round(downtime, 2),
                'operator': f'Operator_{np.random.choice(["A", "B", "C", "D"])}'
            })
    
    # Create DataFrame and save
    sample_df = pd.DataFrame(sample_data)
    full_path = os.path.join(os.getcwd(), output_path)
    sample_df.to_csv(full_path, index=False)
    
    print(f"Sample manufacturing data created: {full_path}")
    print(f"Data shape: {sample_df.shape}")
    print(f"Date range: {sample_df['date'].min()} to {sample_df['date'].max()}")
    
    return full_path


if __name__ == "__main__":
    # Create sample data for testing
    sample_file = create_sample_data()
    
    # Test loading the sample data
    try:
        df = load_manufacturing_data(sample_file)
        print("\nData loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Show summary
        summary = get_data_summary(df)
        print(f"\nData Summary:")
        print(f"Total Records: {summary['total_records']}")
        print(f"Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}")
        print(f"Total Production: {summary['production_stats']['total_production']:,}")
        print(f"Average Defect Rate: {summary['quality_stats']['avg_defect_rate']:.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")
