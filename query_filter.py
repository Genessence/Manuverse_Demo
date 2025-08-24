"""
Query filtering and safety module for Manufacturing Data Chatbot.
Implements multiple layers of protection to ensure only manufacturing-relevant queries are processed.
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum


class QueryFilterResult(Enum):
    """Enumeration for query filter results."""
    ALLOWED = "allowed"
    BLOCKED_IRRELEVANT = "blocked_irrelevant"
    BLOCKED_UNSAFE = "blocked_unsafe"
    BLOCKED_PERSONAL = "blocked_personal"


class FilterResponse:
    """
    Response object for query filtering results.
    """
    def __init__(self, status: QueryFilterResult, message: str = ""):
        self.status = status
        self.message = message
        self.is_allowed = status == QueryFilterResult.ALLOWED


class ManufacturingQueryFilter:
    """
    Manufacturing-specific query filter implementing multiple safety layers.
    """
    
    def __init__(self):
        """Initialize the query filter with manufacturing domain keywords."""
        
        # Manufacturing and industrial domain keywords
        self.manufacturing_keywords = {
            # Core manufacturing terms
            'production', 'manufacturing', 'factory', 'plant', 'assembly', 'fabrication',
            'machining', 'processing', 'automation', 'robotics', 'cnc', 'machinery',
            
            # Quality and efficiency
            'quality', 'defects', 'defect', 'efficiency', 'productivity', 'performance',
            'yield', 'waste', 'scrap', 'rework', 'inspection', 'testing', 'compliance',
            'standards', 'iso', 'lean', 'six sigma', 'kaizen', 'continuous improvement',
            
            # Operations and logistics
            'operations', 'workflow', 'process', 'procedure', 'schedule', 'planning',
            'inventory', 'supply chain', 'logistics', 'warehouse', 'distribution',
            'shipping', 'receiving', 'procurement', 'sourcing', 'vendor', 'supplier',
            
            # Equipment and maintenance
            'equipment', 'machine', 'tool', 'maintenance', 'repair', 'downtime',
            'uptime', 'breakdown', 'preventive', 'predictive', 'calibration',
            'oee', 'overall equipment effectiveness',
            
            # Personnel and shifts
            'operator', 'technician', 'supervisor', 'foreman', 'shift', 'worker',
            'employee', 'team', 'crew', 'training', 'skill', 'safety',
            
            # Metrics and KPIs
            'kpi', 'metric', 'target', 'goal', 'benchmark', 'baseline', 'trend',
            'analysis', 'report', 'dashboard', 'monitoring', 'tracking',
            
            # Materials and components
            'material', 'component', 'part', 'raw material', 'finished goods',
            'batch', 'lot', 'serial number', 'bom', 'bill of materials',
            
            # Data analysis terms
            'data', 'chart', 'graph', 'visualization', 'statistics', 'correlation',
            'pattern', 'insight', 'summary', 'overview', 'comparison', 'ranking',
            'top performers', 'bottom performers', 'outliers', 'anomalies'
        }
        
        # Data analysis and visualization terms (always relevant for our chatbot)
        self.data_analysis_keywords = {
            'show', 'display', 'plot', 'chart', 'graph', 'visualize', 'analyze',
            'compare', 'trend', 'pattern', 'correlation', 'summary', 'overview',
            'top', 'bottom', 'best', 'worst', 'highest', 'lowest', 'average',
            'total', 'count', 'percentage', 'rate', 'ratio', 'distribution',
            'frequency', 'range', 'variance', 'standard deviation', 'median',
            'quartile', 'percentile', 'outlier', 'anomaly', 'insight',
            'performers', 'performance', 'ranking', 'comparison'
        }
        
        # Unsafe content patterns
        self.unsafe_patterns = [
            # NSFW content
            r'\b(sex|sexual|porn|nude|naked|explicit)\b',
            r'\b(adult|xxx|erotic|intimate)\b',
            
            # Violence and harmful content
            r'\b(kill|murder|violence|weapon|bomb|terrorist)\b',
            r'\b(suicide|self-harm|hurt|pain|torture)\b',
            
            # Illegal activities
            r'\b(drugs|illegal|criminal|hack|steal|fraud)\b',
            r'\b(piracy|copyright|crack|bypass)\b',
            
            # Personal information requests
            r'\b(password|credit card|ssn|social security|bank account)\b',
            r'\b(phone number|address|email|personal)\b'
        ]
        
        # Non-manufacturing domain patterns
        self.irrelevant_patterns = [
            # Entertainment
            r'\b(movie|film|music|song|celebrity|actor|actress)\b',
            r'\b(game|gaming|video game|sport|football|basketball)\b',
            
            # Social media and personal
            r'\b(facebook|twitter|instagram|tiktok|social media)\b',
            r'\b(dating|relationship|friendship|personal life)\b',
            
            # Food and cooking
            r'\b(recipe|cooking|food|restaurant|cuisine)\b',
            
            # Travel and geography
            r'\b(travel|vacation|tourism|country|city|geography)\b',
            
            # Weather
            r'\b(weather|temperature|rain|snow|climate)\b',
            
            # Politics and religion
            r'\b(politics|political|religion|religious|god|church)\b',
            
            # Health and medical (unless occupational safety)
            r'\b(doctor|medicine|hospital|disease|symptom)\b',
            
            # Finance and investment (unless business metrics)
            r'\b(stock|investment|crypto|bitcoin|trading)\b'
        ]
        
        # Compile patterns for efficiency
        self.unsafe_regex = re.compile('|'.join(self.unsafe_patterns), re.IGNORECASE)
        self.irrelevant_regex = re.compile('|'.join(self.irrelevant_patterns), re.IGNORECASE)
    
    def filter_query(self, query: str) -> FilterResponse:
        """
        Apply comprehensive filtering to user query.
        
        Args:
            query (str): User's input query
            
        Returns:
            FilterResponse: Object containing filter result and message
        """
        
        # Step 1: Check for unsafe content
        unsafe_result = self._check_unsafe_content(query)
        if unsafe_result[0] != QueryFilterResult.ALLOWED:
            return FilterResponse(unsafe_result[0], unsafe_result[1])
        
        # Step 2: Check manufacturing relevance
        relevance_result = self._check_manufacturing_relevance(query)
        if relevance_result[0] != QueryFilterResult.ALLOWED:
            return FilterResponse(relevance_result[0], relevance_result[1])
        
        # Step 3: Passed all filters
        return FilterResponse(QueryFilterResult.ALLOWED, "Query is safe and relevant to manufacturing data analysis.")
    
    def _check_unsafe_content(self, query: str) -> Tuple[QueryFilterResult, str]:
        """Check for unsafe, harmful, or NSFW content."""
        
        if self.unsafe_regex.search(query):
            return (
                QueryFilterResult.BLOCKED_UNSAFE,
                "I'm designed specifically for manufacturing data analysis and cannot assist with that type of content. "
                "Please ask questions about production data, quality metrics, efficiency analysis, or operational insights."
            )
        
        return QueryFilterResult.ALLOWED, ""
    
    def _check_manufacturing_relevance(self, query: str) -> Tuple[QueryFilterResult, str]:
        """Check if query is relevant to manufacturing domain."""
        
        query_lower = query.lower()
        
        # Check for clearly irrelevant content
        if self.irrelevant_regex.search(query):
            return (
                QueryFilterResult.BLOCKED_IRRELEVANT,
                "I'm a specialized manufacturing data analysis assistant. I can only help with questions about:\n"
                "• Production data and manufacturing metrics\n"
                "• Quality analysis and defect tracking\n"
                "• Efficiency and performance monitoring\n"
                "• Equipment and operational insights\n"
                "• Data visualization and trends\n\n"
                "Please ask a manufacturing or industrial data-related question."
            )
        
        # Check for manufacturing domain keywords
        manufacturing_score = sum(1 for keyword in self.manufacturing_keywords 
                                if keyword in query_lower)
        
        # Check for data analysis keywords
        analysis_score = sum(1 for keyword in self.data_analysis_keywords 
                           if keyword in query_lower)
        
        # If query contains data analysis terms, it might be relevant
        if analysis_score >= 1:
            return QueryFilterResult.ALLOWED, ""
        
        # If query contains manufacturing terms, it's relevant
        if manufacturing_score >= 1:
            return QueryFilterResult.ALLOWED, ""
        
        # Check for generic data questions that could apply to manufacturing
        generic_data_patterns = [
            r'\b(what|show|how|which|when|where)\b.*\b(data|trend|chart|graph)\b',
            r'\b(analyze|analysis|compare|comparison)\b',
            r'\b(top|best|worst|highest|lowest)\b',
            r'\b(summary|overview|report)\b'
        ]
        
        for pattern in generic_data_patterns:
            if re.search(pattern, query_lower):
                return QueryFilterResult.ALLOWED, ""
        
        # If no manufacturing or analysis relevance found
        return (
            QueryFilterResult.BLOCKED_IRRELEVANT,
            "I specialize in manufacturing and industrial data analysis. I can help you with:\n\n"
            "📊 **Manufacturing Data Analysis:**\n"
            "• Production trends and performance metrics\n"
            "• Quality control and defect analysis\n"
            "• Equipment efficiency and downtime tracking\n"
            "• Operational insights and KPI monitoring\n\n"
            "📈 **Data Visualization:**\n"
            "• Charts and graphs of manufacturing data\n"
            "• Trend analysis and pattern recognition\n"
            "• Comparative analysis and benchmarking\n\n"
            "Please ask a question related to manufacturing data or operations analysis."
        )
    
    def get_manufacturing_examples(self) -> str:
        """Get example questions to help users."""
        return """
🎯 **Example Manufacturing Questions I Can Help With:**

📈 **Production Analysis:**
• "Show me production trends over the last month"
• "Which production line has the highest output?"
• "Compare efficiency between different shifts"

🔍 **Quality Analysis:**
• "What's the defect rate trend?"
• "Which operator has the lowest defect rate?"
• "Show me quality metrics by product line"

⚡ **Efficiency & Performance:**
• "What are the top performing machines?"
• "Show downtime analysis by equipment"
• "Compare OEE across production lines"

📊 **Data Insights:**
• "Summarize last week's production data"
• "Find correlations between variables"
• "Show me outliers in the data"
"""


if __name__ == "__main__":
    # Test the query filter
    filter_system = ManufacturingQueryFilter()
    
    test_queries = [
        # Valid manufacturing queries
        "Show me production trends",
        "What are the top performing lines?",
        "Analyze defect rates by shift",
        
        # Data analysis queries (should be allowed)
        "Show me a chart of the data",
        "What are the trends over time?",
        "Compare different categories",
        
        # Invalid queries
        "What's the weather today?",
        "Tell me about the latest movies",
        "How do I cook pasta?",
        "What's your favorite music?",
        
        # Unsafe queries
        "Show me explicit content",
        "How to make a weapon",
    ]
    
    print("🧪 Testing Manufacturing Query Filter")
    print("=" * 50)
    
    for query in test_queries:
        result = filter_system.filter_query(query)
        status = "✅ ALLOWED" if result.is_allowed else "❌ BLOCKED"
        print(f"\n{status}: '{query}'")
        if not result.is_allowed:
            print(f"Reason: {result.message[:100]}...")
