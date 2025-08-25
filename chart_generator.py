"""
Graph generation module for manufacturing data chatbot.
Creates various types of charts using matplotlib and seaborn based on filtered data.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import os
from datetime import datetime


class ManufacturingChartGenerator:
    """
    Generates charts for manufacturing data analysis based on chart configuration.
    """
    
    def __init__(self, style: str = 'seaborn-v0_8', figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize the chart generator with styling preferences.
        
        Args:
            style (str): Matplotlib style
            figsize (tuple): Default figure size
        """
        plt.style.use(style)
        self.figsize = figsize
        self.colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#59CD90', '#845EC2']
        
        # Create output directory
        self.output_dir = "charts"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def plot_manufacturing_data(self, df: pd.DataFrame, chart_config: Dict, output_path: Optional[str] = None) -> str:
        """
        Plot data with dynamic chart type support and robust error handling.
        
        Args:
            df (pd.DataFrame): Processed data
            chart_config (dict): Chart configuration from LLM
            output_path (str, optional): Custom output path
            
        Returns:
            str: Path to the generated chart
        """
        chart_type = chart_config.get('chart_type', 'line')
        title = chart_config.get('title', 'Data Analysis')
        x_axis = chart_config.get('x_axis', df.columns[0] if not df.empty else 'index')
        y_axis = chart_config.get('y_axis', [df.select_dtypes(include='number').columns[0]] if not df.empty else [])

        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chart_{chart_type}_{timestamp}.png"
            output_path = os.path.join(self.output_dir, filename)

        # Handle empty DataFrame
        if df.empty:
            fig, ax = plt.subplots(figsize=self.figsize)
            ax.text(0.5, 0.5, 'No data available for visualization', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14, color='gray')
            ax.set_title(title, fontsize=16, fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            return output_path

        # Validate x_axis and y_axis
        if x_axis not in df.columns:
            x_axis = df.columns[0]
        y_axis = [col for col in y_axis if col in df.columns]
        if not y_axis:
            numeric_cols = df.select_dtypes(include='number').columns
            y_axis = [numeric_cols[0]] if len(numeric_cols) > 0 else [df.columns[0]]

        # Create chart based on type with error handling
        try:
            if chart_type == 'line':
                self._create_line_chart(df, x_axis, y_axis, title, output_path)
            elif chart_type == 'bar':
                self._create_bar_chart(df, x_axis, y_axis, title, output_path)
            elif chart_type == 'scatter':
                self._create_scatter_chart(df, x_axis, y_axis, title, output_path)
            elif chart_type == 'pie':
                self._create_pie_chart(df, x_axis, y_axis, title, output_path)
            elif chart_type == 'heatmap':
                self._create_heatmap(df, title, output_path)
            else:
                # Fallback to line chart for unknown types
                print(f"Warning: Unknown chart type '{chart_type}', falling back to line chart")
                self._create_line_chart(df, x_axis, y_axis, title, output_path)
        except Exception as e:
            print(f"Error creating {chart_type} chart: {e}")
            # Fallback to simple line chart
            try:
                self._create_line_chart(df, x_axis, y_axis[:1], title, output_path)
            except Exception as fallback_error:
                print(f"Fallback chart creation also failed: {fallback_error}")
                # Create error chart
                fig, ax = plt.subplots(figsize=self.figsize)
                ax.text(0.5, 0.5, f'Chart generation failed: {str(e)[:50]}...', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12, color='red')
                ax.set_title(title, fontsize=16, fontweight='bold')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()

        return output_path
    
    def _create_line_chart(self, df: pd.DataFrame, x_col: str, y_cols: List[str], 
                          title: str, output_path: str):
        """Create a line chart for trend analysis."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Handle date formatting if x-axis is date
        if 'date' in x_col.lower() and pd.api.types.is_datetime64_any_dtype(df[x_col]):
            df_sorted = df.sort_values(x_col)
            x_values = df_sorted[x_col]
        else:
            df_sorted = df
            x_values = df_sorted[x_col]
        
        # Plot multiple metrics
        for i, col in enumerate(y_cols):
            if col in df_sorted.columns:
                color = self.colors[i % len(self.colors)]
                ax.plot(x_values, df_sorted[col], marker='o', linewidth=2, 
                       label=col.replace('_', ' ').title(), color=color)
        
        # Formatting
        ax.set_xlabel(x_col.replace('_', ' ').title())
        ax.set_ylabel('Value')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format date axis if applicable
        if 'date' in x_col.lower() and pd.api.types.is_datetime64_any_dtype(df[x_col]):
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(df) // 10)))
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_bar_chart(self, df: pd.DataFrame, x_col: str, y_cols: List[str], 
                         title: str, output_path: str):
        """Create a bar chart for categorical comparisons."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Handle multiple metrics
        if len(y_cols) == 1:
            # Single metric bar chart
            col = y_cols[0]
            if col in df.columns:
                bars = ax.bar(df[x_col], df[col], color=self.colors[0], alpha=0.8)
                ax.set_ylabel(col.replace('_', ' ').title())
                
                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    if not pd.isna(height):
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{height:.1f}', ha='center', va='bottom')
        else:
            # Multiple metrics grouped bar chart
            x_pos = np.arange(len(df))
            width = 0.8 / len(y_cols)
            
            for i, col in enumerate(y_cols):
                if col in df.columns:
                    offset = (i - len(y_cols)/2) * width + width/2
                    ax.bar(x_pos + offset, df[col], width, 
                          label=col.replace('_', ' ').title(),
                          color=self.colors[i % len(self.colors)], alpha=0.8)
            
            ax.set_xticks(x_pos)
            ax.set_xticklabels(df[x_col])
            ax.legend()
            ax.set_ylabel('Value')
        
        ax.set_xlabel(x_col.replace('_', ' ').title())
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.xticks(rotation=45 if len(df) > 5 else 0)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_scatter_chart(self, df: pd.DataFrame, x_col: str, y_cols: List[str], 
                            title: str, output_path: str):
        """Create a scatter plot for correlation analysis."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if len(y_cols) >= 2:
            # Scatter plot between two metrics
            x_data = df[y_cols[0]] if y_cols[0] in df.columns else df[x_col]
            y_data = df[y_cols[1]] if y_cols[1] in df.columns else df[y_cols[0]]
            
            scatter = ax.scatter(x_data, y_data, alpha=0.6, s=60, color=self.colors[0])
            
            # Add trend line
            if len(x_data) > 1:
                z = np.polyfit(x_data.dropna(), y_data.dropna(), 1)
                p = np.poly1d(z)
                ax.plot(x_data, p(x_data), "r--", alpha=0.8, linewidth=2)
                
                # Calculate correlation
                correlation = x_data.corr(y_data)
                ax.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                       transform=ax.transAxes, fontsize=12, 
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            ax.set_xlabel(y_cols[0].replace('_', ' ').title())
            ax.set_ylabel(y_cols[1].replace('_', ' ').title())
        else:
            # Single metric scatter with index
            y_data = df[y_cols[0]] if y_cols[0] in df.columns else df[x_col]
            x_data = range(len(y_data))
            
            ax.scatter(x_data, y_data, alpha=0.6, s=60, color=self.colors[0])
            ax.set_xlabel('Index')
            ax.set_ylabel(y_cols[0].replace('_', ' ').title())
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_heatmap(self, df: pd.DataFrame, title: str, output_path: str):
        """Create a heatmap for correlation or pivot table analysis."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Select numeric columns for correlation
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Correlation heatmap
            corr_matrix = df[numeric_cols].corr()
            
            # Create heatmap
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": .8}, ax=ax)
            
            ax.set_title(f'{title} - Correlation Matrix', fontsize=16, fontweight='bold')
        else:
            # If not enough numeric columns, create a pivot table heatmap
            if 'shift' in df.columns and 'line' in df.columns and len(numeric_cols) > 0:
                pivot_data = df.pivot_table(
                    values=numeric_cols[0], 
                    index='shift', 
                    columns='line', 
                    aggfunc='mean'
                )
                
                sns.heatmap(pivot_data, annot=True, cmap='viridis', 
                           linewidths=0.5, cbar_kws={"shrink": .8}, ax=ax)
                
                ax.set_title(f'{title} - {numeric_cols[0].title()} by Shift and Line', 
                           fontsize=16, fontweight='bold')
            else:
                # Simple text message if no suitable data for heatmap
                ax.text(0.5, 0.5, 'Insufficient data for heatmap visualization', 
                       ha='center', va='center', transform=ax.transAxes, 
                       fontsize=14)
                ax.set_title(title, fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_pie_chart(self, df: pd.DataFrame, x_col: str, y_cols: List[str], 
                         title: str, output_path: str):
        """Create a pie chart for proportion analysis."""
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if len(y_cols) > 0 and y_cols[0] in df.columns:
            # Group by x_col and sum y_col
            if x_col in df.columns:
                pie_data = df.groupby(x_col)[y_cols[0]].sum()
            else:
                # Use direct values if no proper x_col
                pie_data = df[y_cols[0]]
                pie_data.index = range(len(pie_data))
            
            # Remove zero values
            pie_data = pie_data[pie_data > 0]
            
            if len(pie_data) > 0:
                # Create pie chart
                wedges, texts, autotexts = ax.pie(
                    pie_data.values, 
                    labels=pie_data.index, 
                    autopct='%1.1f%%',
                    startangle=90,
                    colors=self.colors[:len(pie_data)]
                )
                
                # Enhance text
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            else:
                ax.text(0.5, 0.5, 'No data available for pie chart', 
                       ha='center', va='center', transform=ax.transAxes)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_dual_axis_chart(self, df: pd.DataFrame, x_col: str, 
                             left_metrics: List[str], right_metrics: List[str],
                             title: str, output_path: Optional[str] = None) -> str:
        """
        Create a dual-axis chart for comparing metrics with different scales.
        
        Args:
            df (pd.DataFrame): Data to plot
            x_col (str): X-axis column
            left_metrics (list): Metrics for left Y-axis
            right_metrics (list): Metrics for right Y-axis
            title (str): Chart title
            output_path (str, optional): Output path
            
        Returns:
            str: Path to generated chart
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"manufacturing_dual_axis_{timestamp}.png"
            output_path = os.path.join(self.output_dir, filename)
        
        fig, ax1 = plt.subplots(figsize=self.figsize)
        
        # Left axis
        ax1.set_xlabel(x_col.replace('_', ' ').title())
        ax1.set_ylabel(' / '.join([m.replace('_', ' ').title() for m in left_metrics]), 
                      color='tab:blue')
        
        for i, metric in enumerate(left_metrics):
            if metric in df.columns:
                line1 = ax1.plot(df[x_col], df[metric], 
                                color=self.colors[i], marker='o', 
                                label=metric.replace('_', ' ').title())
        
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax1.grid(True, alpha=0.3)
        
        # Right axis
        ax2 = ax1.twinx()
        ax2.set_ylabel(' / '.join([m.replace('_', ' ').title() for m in right_metrics]), 
                      color='tab:red')
        
        for i, metric in enumerate(right_metrics):
            if metric in df.columns:
                line2 = ax2.plot(df[x_col], df[metric], 
                                color=self.colors[i + len(left_metrics)], 
                                marker='s', linestyle='--',
                                label=metric.replace('_', ' ').title())
        
        ax2.tick_params(axis='y', labelcolor='tab:red')
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xticks(rotation=45 if len(df) > 5 else 0)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_dashboard(self, df: pd.DataFrame, analysis_results: Dict, 
                        output_path: Optional[str] = None) -> str:
        """
        Create a comprehensive dashboard with multiple charts.
        
        Args:
            df (pd.DataFrame): Manufacturing data
            analysis_results (dict): Analysis results
            output_path (str, optional): Output path
            
        Returns:
            str: Path to generated dashboard
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"manufacturing_dashboard_{timestamp}.png"
            output_path = os.path.join(self.output_dir, filename)
        
        # Create subplot layout
        fig = plt.figure(figsize=(16, 12))
        
        # Chart 1: Production trend
        ax1 = plt.subplot(2, 2, 1)
        if 'date' in df.columns and 'production' in df.columns:
            daily_prod = df.groupby('date')['production'].sum()
            ax1.plot(daily_prod.index, daily_prod.values, marker='o', color=self.colors[0])
            ax1.set_title('Daily Production Trend')
            ax1.set_ylabel('Units Produced')
            ax1.grid(True, alpha=0.3)
        
        # Chart 2: Defect rate by shift
        ax2 = plt.subplot(2, 2, 2)
        if 'shift' in df.columns and 'defect_rate' in df.columns:
            shift_defects = df.groupby('shift')['defect_rate'].mean()
            bars = ax2.bar(shift_defects.index, shift_defects.values, color=self.colors[1])
            ax2.set_title('Average Defect Rate by Shift')
            ax2.set_ylabel('Defect Rate (%)')
            ax2.grid(True, alpha=0.3, axis='y')
        
        # Chart 3: Efficiency comparison
        ax3 = plt.subplot(2, 2, 3)
        if 'line' in df.columns and 'efficiency' in df.columns:
            line_eff = df.groupby('line')['efficiency'].mean()
            ax3.bar(line_eff.index, line_eff.values, color=self.colors[2])
            ax3.set_title('Average Efficiency by Production Line')
            ax3.set_ylabel('Efficiency (%)')
            ax3.grid(True, alpha=0.3, axis='y')
        
        # Chart 4: Correlation heatmap
        ax4 = plt.subplot(2, 2, 4)
        numeric_cols = ['production', 'defects', 'efficiency', 'downtime']
        available_cols = [col for col in numeric_cols if col in df.columns]
        
        if len(available_cols) >= 2:
            corr_matrix = df[available_cols].corr()
            im = ax4.imshow(corr_matrix, cmap='coolwarm', aspect='auto')
            ax4.set_xticks(range(len(available_cols)))
            ax4.set_yticks(range(len(available_cols)))
            ax4.set_xticklabels(available_cols, rotation=45)
            ax4.set_yticklabels(available_cols)
            ax4.set_title('Metrics Correlation')
            
            # Add correlation values
            for i in range(len(available_cols)):
                for j in range(len(available_cols)):
                    ax4.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                           ha='center', va='center')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path


if __name__ == "__main__":
    # Test the chart generator
    try:
        from data_loader import load_manufacturing_data, create_sample_data
        from data_processor import ManufacturingDataProcessor
        
        # Create sample data and load
        sample_file = create_sample_data()
        df = load_manufacturing_data(sample_file)
        
        # Initialize chart generator
        chart_gen = ManufacturingChartGenerator()
        
        # Test different chart types
        test_configs = [
            {
                'chart_type': 'line',
                'title': 'Production Trend Over Time',
                'x_axis': 'date',
                'y_axis': ['production']
            },
            {
                'chart_type': 'bar',
                'title': 'Efficiency by Production Line',
                'x_axis': 'line',
                'y_axis': ['efficiency']
            },
            {
                'chart_type': 'scatter',
                'title': 'Production vs Defects Correlation',
                'x_axis': 'production',
                'y_axis': ['production', 'defects']
            }
        ]
        
        for config in test_configs:
            # Prepare data
            processor = ManufacturingDataProcessor()
            if config['chart_type'] == 'bar':
                chart_data = processor.aggregate_data(df, 'line', ['mean'])
            else:
                chart_data = df.copy()
            
            # Generate chart
            chart_path = chart_gen.plot_manufacturing_data(chart_data, config)
            print(f"Created chart: {chart_path}")
        
        # Test dashboard
        dashboard_path = chart_gen.create_dashboard(df, {})
        print(f"Created dashboard: {dashboard_path}")
        
    except Exception as e:
        print(f"Error testing chart generator: {e}")
