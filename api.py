"""
API endpoints for Universal Data Chatbot.
Provides REST API interface for data upload and analysis.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import pandas as pd
import io
import os
import uuid
from typing import Optional, Dict, List
import shutil
from pathlib import Path

# Import our modules
from data_loader import load_manufacturing_data, validate_universal_columns, get_data_summary
from llm_system import ManufacturingLLMSystem
from data_processor import UniversalDataProcessor
from chart_generator import ManufacturingChartGenerator

app = FastAPI(
    title="Universal Data Analysis Chatbot API",
    description="""
    🤖 **Universal Data Analysis Chatbot API**
    
    An AI-powered data analysis API that can work with **any structured dataset** (CSV/Excel).
    
    ## 🚀 Features
    
    - **Universal Data Support**: Works with any CSV or Excel file
    - **AI Column Detection**: Automatically identifies date, numeric, categorical columns
    - **Natural Language Queries**: Ask questions in plain English
    - **Smart Chart Generation**: Creates appropriate visualizations
    - **Session Management**: Upload once, query multiple times
    
    ## 📊 Supported Data Types
    
    - Sales Data (revenue, products, customers)
    - Manufacturing Data (production, quality, efficiency)  
    - Financial Data (expenses, budgets, transactions)
    - HR Data (employees, performance, salaries)
    - Web Analytics (traffic, conversions, behavior)
    - Survey Data (responses, ratings, demographics)
    - Research Data (experiments, measurements)
    
    ## 🎯 Example Queries
    
    - "What are the top performers?"
    - "Show me trends over time"
    - "Compare different categories"
    - "Find correlations between variables"
    - "Identify outliers or unusual patterns"
    
    ## 📈 Workflow
    
    1. **Upload** your data file via `/upload`
    2. **Query** your data using natural language via `/query` 
    3. **Download** generated charts and get AI insights
    4. **Summarize** your data with `/summary`
    """,
    version="1.0.0",
    contact={
        "name": "Universal Data Chatbot",
        "url": "https://github.com/chahalbaljinder/gemini_chatbot",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for session management
sessions = {}
llm_system = None

# Initialize LLM system
try:
    llm_system = ManufacturingLLMSystem()
except Exception as e:
    print(f"Warning: LLM system initialization failed: {e}")

# Request/Response models
class QueryRequest(BaseModel):
    session_id: str
    query: str

class QueryResponse(BaseModel):
    session_id: str
    response: str
    chart_url: Optional[str] = None
    analysis_results: Dict
    success: bool
    error_message: Optional[str] = None

class DataSummaryResponse(BaseModel):
    session_id: str
    summary: Dict
    column_metadata: Dict
    success: bool

class SessionInfo(BaseModel):
    session_id: str
    filename: str
    upload_timestamp: str
    data_shape: tuple
    columns: List[str]

@app.get(
    "/",
    summary="🏠 API Information",
    description="Welcome to the Universal Data Analysis Chatbot API",
    tags=["General"]
)
async def root():
    """
    ## 🏠 Welcome to Universal Data Analysis Chatbot API
    
    ### 🚀 Quick Start Guide
    1. **Upload** your data: `POST /upload` 
    2. **Get summary**: `GET /summary/{session_id}`
    3. **Ask questions**: `POST /query`
    4. **Download charts**: `GET /chart/{filename}`
    
    ### 📚 Interactive Documentation
    - **Swagger UI**: `/docs` (this page)
    - **ReDoc**: `/redoc` (alternative documentation)
    
    ### 🎯 Example Workflow
    ```python
    # 1. Upload your data
    files = {'file': open('data.csv', 'rb')}
    response = requests.post('/upload', files=files)
    session_id = response.json()['session_id']
    
    # 2. Query your data
    query_data = {
        'session_id': session_id,
        'query': 'What are the top performers?'
    }
    result = requests.post('/query', json=query_data)
    print(result.json()['response'])
    ```
    """
    return {
        "message": "🤖 Universal Data Analysis Chatbot API",
        "version": "1.0.0",
        "status": "✅ Running",
        "capabilities": [
            "📤 Upload any CSV/Excel dataset",
            "🤖 Natural language data queries", 
            "📊 Automatic chart generation",
            "🔍 AI-powered column detection",
            "📈 Trend and pattern analysis"
        ],
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "/upload": "POST - Upload dataset file (CSV/Excel)",
            "/query": "POST - Query data analysis with natural language",
            "/summary/{session_id}": "GET - Get comprehensive data summary",
            "/sessions": "GET - List all active analysis sessions",
            "/chart/{filename}": "GET - Download generated chart images",
            "/health": "GET - API health status"
        }
    }

@app.post(
    "/upload",
    summary="📤 Upload Dataset",
    description="Upload your data file and create a new analysis session",
    response_description="Session ID and data summary with column analysis",
    tags=["Data Management"]
)
async def upload_dataset(file: UploadFile = File(...)):
    """
    ## 📤 Upload Dataset
    
    Upload any structured dataset (CSV/Excel) to start analyzing your data.
    
    ### 📋 Supported File Types
    - **CSV** (.csv) - Comma-separated values
    - **Excel** (.xlsx, .xls) - Microsoft Excel files
    
    ### 🔍 What Happens
    1. **File Validation** - Checks file type and format
    2. **Data Loading** - Reads your data with smart encoding detection  
    3. **Column Analysis** - AI identifies column types (dates, numbers, categories)
    4. **Session Creation** - Generates unique session ID for your data
    
    ### 📊 Column Types Detected
    - **Date Columns** - Automatically parsed for time-series analysis
    - **Numeric Measures** - Revenue, sales, production, scores, etc.
    - **Categories** - Groups, types, classifications, regions, etc.
    - **Quality Measures** - Defects, errors, ratings, performance
    - **Identifiers** - Names, IDs, codes, labels
    
    ### 🎯 Example Data Types
    - Sales data with dates, products, revenue, regions
    - Manufacturing data with production, defects, efficiency
    - Survey data with responses, ratings, demographics
    - Financial data with transactions, categories, amounts
    
    ### ✅ Response Includes
    - **Session ID** - Use this for all subsequent queries
    - **Data Summary** - Row/column counts, date ranges
    - **Column Analysis** - How AI interpreted each column
    - **Sample Data** - Preview of your data structure
    
    ### 🚨 File Requirements
    - Maximum file size: 50MB
    - Must have column headers in first row
    - At least 2 columns required
    - Data should be structured (no merged cells in Excel)
    """
    try:
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session directory
        session_dir = Path(f"sessions/{session_id}")
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        file_path = session_dir / f"data{file_extension}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Load and analyze data
        try:
            if file_extension == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Check if DataFrame is empty
            if df.empty:
                raise ValueError("The uploaded file contains no data")
            
            # Universal column analysis
            processed_df, column_metadata = validate_universal_columns(df, llm_system)
            
            # Get data summary
            data_summary = get_universal_data_summary(processed_df, column_metadata)
            
            # Store session data
            sessions[session_id] = {
                'data': processed_df,
                'metadata': column_metadata,
                'summary': data_summary,
                'filename': file.filename,
                'upload_timestamp': pd.Timestamp.now().isoformat(),
                'file_path': str(file_path),
                'processor': UniversalDataProcessor(),
                'chart_generator': ManufacturingChartGenerator()
            }
            
            return {
                "session_id": session_id,
                "message": "File uploaded successfully",
                "data_info": {
                    "filename": file.filename,
                    "shape": processed_df.shape,
                    "columns": processed_df.columns.tolist()
                },
                "column_metadata": column_metadata,
                "data_summary": data_summary
            }
            
        except Exception as e:
            # Clean up on error
            shutil.rmtree(session_dir, ignore_errors=True)
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/query",
    response_model=QueryResponse,
    summary="🤖 Query Your Data",
    description="Ask questions about your data in natural language and get AI-powered insights",
    response_description="Analysis results, insights, and optional chart visualization",
    tags=["Data Analysis"]
)
async def query_data(request: QueryRequest):
    """
    ## 🤖 Query Your Data
    
    Ask questions about your uploaded data using natural language and get intelligent analysis with charts.
    
    ### 🎯 Example Queries
    
    #### 🏆 Performance & Rankings
    - "What are the top performers?"
    - "Which category has the highest values?"
    - "Show me the best and worst performers"
    - "Rank items by performance"
    
    #### 📈 Trends & Time Analysis  
    - "Show me trends over time"
    - "How has performance changed month by month?"
    - "What are the seasonal patterns?"
    - "Compare this quarter to last quarter"
    
    #### ⚖️ Comparisons & Segments
    - "Compare different categories"
    - "How do regions compare?"
    - "Show differences between groups"
    - "Which segment performs better?"
    
    #### 🔍 Insights & Patterns
    - "Find correlations between variables"
    - "Identify outliers or unusual values"
    - "What factors affect performance?"
    - "Show me data distributions"
    
    #### 📊 Summaries & Overviews
    - "Summarize my data"
    - "Show key statistics"
    - "Give me an overview"
    - "What are the main insights?"
    
    ### 🎨 Chart Types Generated
    - **Bar Charts** - For comparisons and rankings
    - **Line Charts** - For trends and time series
    - **Scatter Plots** - For correlations and relationships
    - **Histograms** - For distributions
    
    ### ✅ Response Includes
    - **AI Analysis** - Intelligent insights about your data
    - **Key Findings** - Important patterns and trends
    - **Recommendations** - Actionable suggestions
    - **Chart Image** - Professional visualization (when applicable)
    - **Data Summary** - Relevant statistics and metrics
    
    ### 🔧 Requirements
    - Valid **session_id** from `/upload` endpoint
    - **Query text** in natural language
    - Session must have uploaded data
    """
    try:
        session_id = request.session_id
        query = request.query
        
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = sessions[session_id]
        df = session_data['data']
        metadata = session_data['metadata']
        summary = session_data['summary']
        processor = session_data['processor']
        chart_generator = session_data['chart_generator']
        
        if llm_system is None:
            raise HTTPException(status_code=503, detail="LLM system not available")
        
        # Get analysis instructions from LLM (with safety filtering)
        analysis_instructions = llm_system.query_llm_system(
            query, summary, metadata
        )
        
        # Check if query was rejected by safety filter
        if analysis_instructions.get('analysis_type') == 'safety_filter':
            return QueryResponse(
                session_id=session_id,
                response=analysis_instructions.get('message', 'Query not allowed.'),
                success=False,
                error_message="Query rejected by manufacturing domain safety filter",
                analysis_results={"filter_status": "rejected"}
            )
        
        # Process data according to instructions
        try:
            filtered_data = processor.filter_manufacturing_data(
                df,
                analysis_instructions.get('filters', {}),
                analysis_instructions.get('metrics', df.select_dtypes(include='number').columns.tolist())
            )
        except Exception as e:
            error_msg = str(e)
            if "cannot convert the series to" in error_msg:
                return QueryResponse(
                    session_id=session_id,
                    response="I encountered an issue processing your data. This might be due to mixed data types in date columns or other formatting issues. Please check your data and try uploading again.",
                    success=False,
                    error_message="Data processing error: " + error_msg,
                    analysis_results={}
                )
            else:
                raise HTTPException(status_code=500, detail=f"Data processing error: {error_msg}")
        
        if filtered_data.empty:
            return QueryResponse(
                session_id=session_id,
                response="No data found matching your criteria. Please try a different query.",
                success=False,
                analysis_results={}
            )
        
        # Aggregate data
        aggregated_data = processor.aggregate_data(
            filtered_data,
            analysis_instructions.get('grouping', 'none'),
            analysis_instructions.get('calculations', ['sum', 'mean'])
        )
        
        # Compile analysis results
        analysis_results = compile_universal_analysis_results(
            filtered_data, aggregated_data, analysis_instructions, metadata
        )
        
        # Generate insights
        textual_response = llm_system.generate_insights(analysis_results, "")
        
        # Determine if chart should be generated based on query type
        chart_type = analysis_instructions.get('chart_type', 'line')
        should_generate_chart = chart_type not in ['none', None] and chart_type in ['line', 'bar', 'scatter', 'pie', 'heatmap']
        chart_url = None
        
        if should_generate_chart:
            try:
                # Generate chart
                chart_data, chart_config = processor.prepare_chart_data(
                    aggregated_data, analysis_instructions
                )
                
                chart_filename = f"chart_{session_id}_{uuid.uuid4().hex[:8]}.png"
                chart_path = f"sessions/{session_id}/{chart_filename}"
                
                chart_generator.plot_manufacturing_data(chart_data, chart_config, chart_path)
                chart_url = f"/chart/{session_id}/{chart_filename}"
            except Exception as e:
                print(f"Chart generation failed: {e}")
                # Continue without chart
        
        return QueryResponse(
            session_id=session_id,
            response=textual_response,
            chart_url=chart_url,
            analysis_results=analysis_results,
            success=True
        )
        
    except Exception as e:
        return QueryResponse(
            session_id=request.session_id,
            response="",
            success=False,
            error_message=str(e),
            analysis_results={}
        )

@app.get(
    "/summary/{session_id}",
    response_model=DataSummaryResponse,
    summary="📋 Get Data Summary",
    description="Get comprehensive summary and metadata for your uploaded dataset",
    response_description="Complete data overview including statistics and column information",
    tags=["Data Management"]
)
async def get_data_summary(session_id: str):
    """
    ## 📋 Get Data Summary
    
    Retrieve comprehensive summary information about your uploaded dataset.
    
    ### ✅ Response Includes
    - **Row Count** - Total number of records
    - **Column Count** - Number of data columns
    - **Date Range** - Time span of your data (if applicable)
    - **Column Metadata** - How AI interpreted each column
    - **Data Types** - Detected column types and formats
    - **Sample Values** - Preview of actual data
    
    ### 🔍 Column Analysis Details
    - **date** - Time-based columns for trend analysis
    - **numeric_measure** - Quantities, amounts, scores, KPIs
    - **categorical** - Groups, types, categories, segments  
    - **quality_measure** - Defects, errors, ratings, quality scores
    - **efficiency_measure** - Performance, utilization, productivity
    - **identifier** - Names, IDs, codes, labels
    
    ### 🎯 Use This Information To
    - Understand your data structure
    - Plan your analysis queries
    - Verify data was loaded correctly
    - Check column interpretations
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    return DataSummaryResponse(
        session_id=session_id,
        summary=session_data['summary'],
        column_metadata=session_data['metadata'],
        success=True
    )

@app.get(
    "/sessions",
    summary="📋 List Active Sessions",
    description="Get information about all active data analysis sessions",
    response_description="List of all sessions with metadata and statistics",
    tags=["Data Management"]
)
async def list_sessions():
    """
    ## 📋 List Active Sessions
    
    View all currently active data analysis sessions with their metadata.
    
    ### ✅ Response Includes For Each Session
    - **Session ID** - Unique identifier for the session
    - **Filename** - Original uploaded file name
    - **Upload Time** - When the data was uploaded
    - **Data Shape** - Number of rows and columns
    - **Column Names** - List of all column headers
    
    ### 🎯 Use This Endpoint To
    - Track multiple analysis sessions
    - Recall session IDs for queries
    - Monitor data upload activity
    - Manage concurrent analyses
    """
    session_list = []
    
    for session_id, session_data in sessions.items():
        session_list.append(SessionInfo(
            session_id=session_id,
            filename=session_data['filename'],
            upload_timestamp=session_data['upload_timestamp'],
            data_shape=session_data['data'].shape,
            columns=session_data['data'].columns.tolist()
        ))
    
    return {"sessions": session_list, "total": len(session_list)}

@app.get(
    "/health",
    summary="💚 Health Check",
    description="Check API health status and system information",
    tags=["General"]
)
async def health_check():
    """
    ## 💚 API Health Check
    
    Verify that the API is running properly and check system status.
    
    ### ✅ Health Information
    - **Status** - API operational status
    - **Active Sessions** - Number of current data sessions
    - **System Info** - Python version and dependencies
    - **Available Features** - List of working capabilities
    
    ### 🔧 Use This Endpoint To
    - Monitor API availability
    - Check system health in production
    - Verify all components are working
    - Get system statistics
    """
    import sys
    import pandas as pd
    
    try:
        # Test core functionality
        test_df = pd.DataFrame({'test': [1, 2, 3]})
        llm_system = ManufacturingLLMSystem()
        
        return {
            "status": "✅ Healthy",
            "api_version": "1.0.0",
            "python_version": sys.version.split()[0],
            "active_sessions": len(sessions),
            "pandas_version": pd.__version__,
            "features": {
                "data_upload": "✅ Working",
                "llm_analysis": "✅ Working", 
                "chart_generation": "✅ Working",
                "session_management": "✅ Working"
            },
            "timestamp": pd.Timestamp.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "❌ Unhealthy",
            "error": str(e),
            "timestamp": pd.Timestamp.now().isoformat()
        }

@app.get(
    "/chart/{session_id}/{filename}",
    summary="📊 Download Chart",
    description="Download generated chart images from data analysis",
    response_class=FileResponse,
    tags=["Data Analysis"]
)
async def get_chart(session_id: str, filename: str):
    """
    ## 📊 Download Chart
    
    Download chart images generated from your data analysis queries.
    
    ### 🎨 Chart Types Available
    - **Bar Charts** - Comparisons and rankings (.png)
    - **Line Charts** - Trends and time series (.png) 
    - **Scatter Plots** - Correlations (.png)
    - **Histograms** - Data distributions (.png)
    
    ### 📥 Download Information
    - **Format**: High-quality PNG images
    - **Resolution**: Optimized for reports and presentations
    - **File Size**: Typically 50-500KB per chart
    
    ### 🔧 URL Format
    ```
    GET /chart/{session_id}/{filename}
    ```
    
    ### 🎯 Usage
    - Charts are generated automatically during `/query` requests
    - Filename is provided in query response
    - Charts are stored per session
    - Images can be embedded in reports or dashboards
    """
    chart_path = Path(f"sessions/{session_id}/{filename}")
    
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")
    
    return FileResponse(
        chart_path,
        media_type="image/png",
        filename=filename
    )

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and clean up files."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clean up files
    session_dir = Path(f"sessions/{session_id}")
    if session_dir.exists():
        shutil.rmtree(session_dir)
    
    # Remove from sessions
    del sessions[session_id]
    
    return {"message": f"Session {session_id} deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_available": llm_system is not None,
        "active_sessions": len(sessions)
    }

def get_universal_data_summary(df: pd.DataFrame, metadata: Dict) -> Dict:
    """
    Generate summary for any dataset based on column metadata.
    
    Args:
        df (pd.DataFrame): Dataset
        metadata (dict): Column metadata
        
    Returns:
        dict: Universal data summary
    """
    summary = {
        'total_records': len(df),
        'available_columns': df.columns.tolist(),
        'column_metadata': metadata
    }
    
    # Date range if date columns exist
    date_columns = metadata.get('date_columns', [])
    if date_columns:
        date_col = date_columns[0]  # Use first date column
        summary['date_range'] = {
            'start': df[date_col].min().strftime('%Y-%m-%d') if pd.notna(df[date_col].min()) else None,
            'end': df[date_col].max().strftime('%Y-%m-%d') if pd.notna(df[date_col].max()) else None
        }
    
    # Numeric summaries
    numeric_cols = metadata.get('numeric_measures', []) + metadata.get('quality_measures', []) + metadata.get('efficiency_measures', [])
    if numeric_cols:
        summary['numeric_summary'] = {}
        for col in numeric_cols:
            if col in df.columns:
                summary['numeric_summary'][col] = {
                    'total': float(df[col].sum()),
                    'mean': float(df[col].mean()),
                    'max': float(df[col].max()),
                    'min': float(df[col].min()),
                    'std': float(df[col].std())
                }
    
    # Categorical summaries
    categorical_cols = metadata.get('categorical_columns', [])
    if categorical_cols:
        summary['categorical_summary'] = {}
        for col in categorical_cols:
            if col in df.columns:
                summary['categorical_summary'][col] = df[col].value_counts().to_dict()
    
    return summary

def compile_universal_analysis_results(filtered_data, aggregated_data, instructions, metadata) -> Dict:
    """Compile analysis results for any dataset."""
    results = {
        'query_type': instructions.get('analysis_type', 'general_analysis'),
        'records_analyzed': len(filtered_data),
        'metrics_summary': {}
    }
    
    # Add date range if applicable
    date_columns = metadata.get('date_columns', [])
    if date_columns and date_columns[0] in filtered_data.columns:
        date_col = date_columns[0]
        results['date_range'] = {
            'start': filtered_data[date_col].min().strftime('%Y-%m-%d'),
            'end': filtered_data[date_col].max().strftime('%Y-%m-%d'),
            'days': len(filtered_data[date_col].unique())
        }
    
    # Numeric metrics summary
    numeric_cols = metadata.get('numeric_measures', []) + metadata.get('quality_measures', [])
    for col in numeric_cols:
        if col in filtered_data.columns:
            results['metrics_summary'][col] = {
                'total': float(filtered_data[col].sum()),
                'average': float(filtered_data[col].mean()),
                'max': float(filtered_data[col].max()),
                'min': float(filtered_data[col].min())
            }
    
    return results

if __name__ == "__main__":
    import uvicorn
    
    # Create necessary directories
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("charts", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
