import React from 'react';
import styled from 'styled-components';
import { Database, Eye } from 'lucide-react';

const PreviewContainer = styled.div`
  background-color: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 12px;
`;

const PreviewHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #c9d1d9;
`;

const PreviewContent = styled.div`
  font-size: 12px;
  color: #7d8590;
`;

const DataInfo = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const Label = styled.span`
  color: #7d8590;
`;

const Value = styled.span`
  color: #c9d1d9;
  font-weight: 500;
`;

const ColumnsList = styled.div`
  margin-top: 8px;
  max-height: 120px;
  overflow-y: auto;
`;

const ColumnItem = styled.div`
  padding: 4px 8px;
  background-color: #0d1117;
  border-radius: 4px;
  margin-bottom: 4px;
  font-size: 11px;
  color: #c9d1d9;
  border-left: 3px solid #58a6ff;
`;

const SampleData = styled.div`
  margin-top: 8px;
  max-height: 100px;
  overflow-y: auto;
  background-color: #0d1117;
  border-radius: 4px;
  padding: 8px;
`;

const SampleRow = styled.div`
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #7d8590;
  margin-bottom: 4px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const SampleCell = styled.span`
  color: #c9d1d9;
  min-width: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

function DataPreview({ data }) {
  if (!data) return null;

  const { columns, rows } = data;

  return (
    <PreviewContainer>
      <PreviewHeader>
        <Database size={14} />
        Data Preview
      </PreviewHeader>
      
      <PreviewContent>
        <DataInfo>
          <Label>Columns:</Label>
          <Value>{columns.length}</Value>
        </DataInfo>
        
        <DataInfo>
          <Label>Rows:</Label>
          <Value>{rows.length}</Value>
        </DataInfo>
        
        <ColumnsList>
          {columns.map((column, index) => (
            <ColumnItem key={index}>
              {column}
            </ColumnItem>
          ))}
        </ColumnsList>
        
        {rows.length > 0 && (
          <SampleData>
            <div style={{ marginBottom: '6px', color: '#7d8590', fontSize: '10px' }}>
              Sample Data:
            </div>
            {rows.slice(0, 3).map((row, index) => (
              <SampleRow key={index}>
                {row.map((cell, cellIndex) => (
                  <SampleCell key={cellIndex} title={cell}>
                    {cell}
                  </SampleCell>
                ))}
              </SampleRow>
            ))}
            {rows.length > 3 && (
              <div style={{ fontSize: '10px', color: '#7d8590', textAlign: 'center', marginTop: '4px' }}>
                ... and {rows.length - 3} more rows
              </div>
            )}
          </SampleData>
        )}
      </PreviewContent>
    </PreviewContainer>
  );
}

export default DataPreview; 