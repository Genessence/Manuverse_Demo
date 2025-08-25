import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Bar, Line, Pie, Doughnut } from 'react-chartjs-2';
import { BarChart3, TrendingUp, PieChart as PieIcon } from 'lucide-react';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const ChartWrapper = styled.div`
  width: 100%;
  min-height: 400px;
  background-color: #0d1117;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
`;

const ChartContainer = styled.div`
  width: 100%;
  height: 350px;
  position: relative;
`;

const ChartHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  font-weight: 600;
  color: #c9d1d9;
  flex-shrink: 0;
`;

const NoChartMessage = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #7d8590;
  font-size: 14px;
  text-align: center;
`;

const CHART_COLORS = {
  primary: '#58a6ff',
  secondary: '#238636',
  tertiary: '#f85149',
  quaternary: '#d29922',
  quinary: '#a371f7',
  senary: '#7d8590',
  background: '#0d1117',
  grid: '#30363d',
  text: '#c9d1d9'
};

const COLORS_ARRAY = [
  '#58a6ff', '#238636', '#f85149', '#d29922', 
  '#a371f7', '#7d8590', '#ff7b72', '#79c0ff',
  '#56d364', '#ffa657', '#f2cc60', '#b392f0'
];

function ChartDisplay({ chartData }) {
  const chartRef = useRef(null);

  // Chart.js options with dark theme
  const getChartOptions = (chartType) => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: CHART_COLORS.text,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: '#161b22',
        titleColor: CHART_COLORS.text,
        bodyColor: CHART_COLORS.text,
        borderColor: CHART_COLORS.grid,
        borderWidth: 1,
      }
    },
    scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
      x: {
        grid: {
          color: CHART_COLORS.grid,
        },
        ticks: {
          color: CHART_COLORS.text,
          font: {
            size: 11
          }
        }
      },
      y: {
        grid: {
          color: CHART_COLORS.grid,
        },
        ticks: {
          color: CHART_COLORS.text,
          font: {
            size: 11
          }
        }
      }
    } : undefined
  });

  // Convert backend data to Chart.js format
  const processChartData = (data, type) => {
    if (!data || !Array.isArray(data)) return null;

    let labels = [];
    let datasets = [];

    if (type === 'bar' || type === 'line') {
      labels = data.map(item => item.name || item.label || item.x || 'Unknown');
      
      datasets = [{
        label: 'Value',
        data: data.map(item => item.value || item.y || 0),
        backgroundColor: type === 'bar' ? CHART_COLORS.primary : 'transparent',
        borderColor: CHART_COLORS.primary,
        borderWidth: 2,
        fill: type === 'line' ? false : true,
        tension: type === 'line' ? 0.4 : 0,
        pointBackgroundColor: CHART_COLORS.primary,
        pointBorderColor: CHART_COLORS.primary,
        pointRadius: type === 'line' ? 4 : 0,
      }];
    } else if (type === 'pie' || type === 'doughnut') {
      labels = data.map(item => item.name || item.label || 'Unknown');
      
      datasets = [{
        data: data.map(item => item.value || 0),
        backgroundColor: COLORS_ARRAY.slice(0, data.length),
        borderColor: CHART_COLORS.background,
        borderWidth: 2,
      }];
    }

    return { labels, datasets };
  };

  if (!chartData) {
    return (
      <ChartWrapper>
        <NoChartMessage>
          <BarChart3 size={20} style={{ marginRight: '8px' }} />
          No chart data available
        </NoChartMessage>
      </ChartWrapper>
    );
  }

  const { type, data, title, url } = chartData;

  const renderChart = () => {
    // Handle image type (fallback for backend-generated charts)
    if (type === 'image' && url) {
      return (
        <div style={{ 
          width: '100%', 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          padding: '10px'
        }}>
          <img 
            src={url} 
            alt="Generated Chart" 
            style={{ 
              width: '125%',
              height: 'auto',
              maxHeight: '320px',
              objectFit: 'contain',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
              marginLeft: '-12.5%'
            }} 
            onError={(e) => {
              console.error('Chart image failed to load:', url);
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'block';
            }}
          />
          <div style={{ display: 'none', color: '#7d8590', fontSize: '12px', marginTop: '8px' }}>
            Chart image failed to load. URL: {url}
          </div>
        </div>
      );
    }

    // Process data for Chart.js
    const chartJsData = processChartData(data, type);
    
    if (!chartJsData) {
      return (
        <NoChartMessage>
          <BarChart3 size={20} style={{ marginRight: '8px' }} />
          Invalid chart data format
        </NoChartMessage>
      );
    }

    const options = getChartOptions(type);

    switch (type) {
      case 'bar':
        return (
          <ChartContainer>
            <Bar ref={chartRef} data={chartJsData} options={options} />
          </ChartContainer>
        );

      case 'line':
        return (
          <ChartContainer>
            <Line ref={chartRef} data={chartJsData} options={options} />
          </ChartContainer>
        );

      case 'pie':
        return (
          <ChartContainer>
            <Pie ref={chartRef} data={chartJsData} options={options} />
          </ChartContainer>
        );

      case 'doughnut':
        return (
          <ChartContainer>
            <Doughnut ref={chartRef} data={chartJsData} options={options} />
          </ChartContainer>
        );

      default:
        return (
          <NoChartMessage>
            <BarChart3 size={20} style={{ marginRight: '8px' }} />
            Unsupported chart type: {type}
          </NoChartMessage>
        );
    }
  };

  const getChartIcon = () => {
    switch (type) {
      case 'bar':
        return <BarChart3 size={16} />;
      case 'line':
        return <TrendingUp size={16} />;
      case 'pie':
      case 'doughnut':
        return <PieIcon size={16} />;
      case 'image':
        return <BarChart3 size={16} />;
      default:
        return <BarChart3 size={16} />;
    }
  };

  return (
    <ChartWrapper>
      <ChartHeader>
        {getChartIcon()}
        {title || (type ? `${type.charAt(0).toUpperCase() + type.slice(1)} Chart` : 'Chart')}
      </ChartHeader>
      {renderChart()}
    </ChartWrapper>
  );
}

export default ChartDisplay; 