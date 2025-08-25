import React from 'react';
import styled from 'styled-components';
import { Bot, User, Clock } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import ChartDisplay from './ChartDisplay';

const MessageContainer = styled.div`
  display: flex;
  gap: 12px;
  padding: 20px 0;
  animation: fadeIn 0.3s ease-in;
  
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
`;

const Avatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background-color: ${props => props.type === 'user' ? '#58a6ff' : '#238636'};
  color: white;
`;

const MessageContent = styled.div`
  flex: 1;
  max-width: calc(100% - 44px);
`;

const MessageBubble = styled.div`
  background-color: ${props => props.type === 'user' ? '#161b22' : '#21262d'};
  border: 1px solid ${props => props.type === 'user' ? '#30363d' : '#30363d'};
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 8px;
  line-height: 1.5;
  
  ${props => props.type === 'user' && `
    background-color: #0c2d6b;
    border-color: #1f6feb;
  `}
`;

const MessageText = styled.div`
  color: #c9d1d9;
  font-size: 14px;
  
  p {
    margin: 0 0 12px 0;
    
    &:last-child {
      margin-bottom: 0;
    }
  }
  
  code {
    background-color: #161b22;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 13px;
    color: #79c0ff;
  }
  
  pre {
    background-color: #161b22;
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 12px 0;
    
    code {
      background: none;
      padding: 0;
    }
  }
  
  ul, ol {
    margin: 8px 0;
    padding-left: 20px;
  }
  
  li {
    margin: 4px 0;
  }
  
  strong {
    color: #f0f6fc;
    font-weight: 600;
  }
  
  em {
    color: #7d8590;
    font-style: italic;
  }
`;

const Timestamp = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #7d8590;
  margin-top: 4px;
`;

const LoadingDots = styled.div`
  display: flex;
  gap: 4px;
  align-items: center;
  
  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: #7d8590;
    animation: pulse 1.4s ease-in-out infinite both;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0s; }
  }
  
  @keyframes pulse {
    0%, 80%, 100% {
      transform: scale(0.8);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
`;

const ChartContainer = styled.div`
  margin-top: 16px;
  background-color: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 16px;
`;

function ChatMessage({ message, isLoading = false }) {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (isLoading) {
    return (
      <MessageContainer>
        <Avatar type="bot">
          <Bot size={16} />
        </Avatar>
        <MessageContent>
          <MessageBubble type="bot">
            <LoadingDots>
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </LoadingDots>
          </MessageBubble>
        </MessageContent>
      </MessageContainer>
    );
  }

  return (
    <MessageContainer>
      <Avatar type={message.type}>
        {message.type === 'user' ? <User size={16} /> : <Bot size={16} />}
      </Avatar>
      <MessageContent>
        <MessageBubble type={message.type}>
          <MessageText>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </MessageText>
        </MessageBubble>
        
        {message.chart && (
          <ChartContainer>
            {(() => {
              // Handle new Chart.js data format
              if (typeof message.chart === 'object' && message.chart.type) {
                console.log('📊 Chart Data Processing:', message.chart);
                return <ChartDisplay chartData={message.chart} />;
              }
              
              // Legacy: Handle old chart URL format
              if (typeof message.chart === 'string') {
                const fullChartUrl = message.chart.startsWith('http') ? message.chart : `http://localhost:8000${message.chart}`;
                console.log('🖼️ Chart URL Processing:', {
                  original: message.chart,
                  converted: fullChartUrl
                });
                return (
                  <ChartDisplay chartData={{
                    type: 'image',
                    data: null,
                    title: 'Generated Chart',
                    url: fullChartUrl
                  }} />
                );
              }
              
              return null;
            })()}
          </ChartContainer>
        )}
        
        <Timestamp>
          <Clock size={12} />
          {formatTime(message.timestamp)}
        </Timestamp>
      </MessageContent>
    </MessageContainer>
  );
}

export default ChatMessage; 