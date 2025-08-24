# Universal Data Analysis Chatbot

A powerful AI-powered chatbot that can analyze **any dataset** using Google's Gemini LLM. The chatbot automatically detects column types, understands your data structure, and generates insightful visualizations and analysis through natural language queries.

## 🚀 Features

- **Universal Data Support**: Works with any CSV or Excel dataset - no predefined schema required
- **Intelligent Column Detection**: AI-powered analysis to understand your data structure automatically
- **Natural Language Processing**: Ask questions about your data in plain English
- **Web Interface**: Modern, responsive web UI for easy interaction
- **REST API**: Full API endpoints for integration with other applications
- **Multiple Chart Types**: Generates appropriate visualizations based on your data
- **Smart Analysis**: Context-aware insights and recommendations
- **File Upload**: Drag-and-drop interface for dataset uploads

## 🎯 Supported Data Types

The chatbot can analyze any type of structured data:

- **Business Data**: Sales, revenue, customer metrics, operational data
- **Manufacturing Data**: Production metrics, quality data, efficiency measures
- **Financial Data**: Trading data, expenses, budgets, financial metrics
- **Scientific Data**: Experimental results, measurements, observations
- **Web Analytics**: Traffic data, user metrics, conversion rates
- **Survey Data**: Responses, ratings, demographic information
- **Time Series Data**: Any data with temporal components
- **And much more!**

## 🛠️ Installation & Setup

### Quick Start (5 minutes)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   ```bash
   python config.py
   ```
   Or manually edit `.env`:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Start the Application**
   ```bash
   python start_server.py
   ```

4. **Open Web Interface**
   - Automatically opens at http://localhost:8080
   - API available at http://localhost:8000

## 🌐 Web Interface

### Upload Your Data
- Drag and drop CSV or Excel files
- Automatic column type detection
- Instant data summary and metadata

### Ask Questions
- Natural language queries
- Real-time AI analysis
- Interactive charts and insights

### Example Questions for Any Dataset:
- "Show me the trend over time"
- "What are the top 10 values by category?"
- "Compare different groups in the data"
- "Find correlations between variables"
- "Summarize the key metrics"
- "Show distribution of values"
- "Identify outliers or anomalies"

## � API Endpoints

### Core Endpoints

- `POST /upload` - Upload dataset file
- `POST /query` - Submit analysis query  
- `GET /summary/{session_id}` - Get data summary
- `GET /sessions` - List active sessions
- `GET /chart/{session_id}/{filename}` - Download generated charts

### Example API Usage

```python
import requests

# Upload dataset
files = {'file': open('your_data.csv', 'rb')}
response = requests.post('http://localhost:8000/upload', files=files)
session_data = response.json()
session_id = session_data['session_id']

# Query the data
query_data = {
    'session_id': session_id,
    'query': 'Show me the trend over time'
}
response = requests.post('http://localhost:8000/query', json=query_data)
results = response.json()

print(results['response'])  # AI-generated insights
# Download chart if available
if results['chart_url']:
    chart_response = requests.get(f"http://localhost:8000{results['chart_url']}")
    with open('chart.png', 'wb') as f:
        f.write(chart_response.content)
```

## 🧠 How It Works

### 1. Intelligent Column Detection
The system uses AI to analyze your dataset and automatically identify:
- Date/time columns
- Numeric measures (quantities, amounts, counts)
- Quality measures (defects, errors, issues)  
- Efficiency measures (rates, percentages, performance)
- Categorical data (groups, classifications)
- Identifier columns (IDs, names, codes)

### 2. Context-Aware Analysis
Based on your data structure, the AI:
- Suggests appropriate analysis methods
- Recommends suitable chart types
- Provides domain-specific insights
- Identifies meaningful patterns and trends

### 3. Dynamic Visualization
Charts are automatically generated based on:
- Data types and relationships
- Query context and intent
- Statistical significance
- Visual best practices
# Manuverse_Demo
