import React, { useCallback } from 'react';
import styled from 'styled-components';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X } from 'lucide-react';

const UploadContainer = styled.div`
  border: 2px dashed #30363d;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background-color: #0d1117;
  
  &:hover {
    border-color: #58a6ff;
    background-color: #161b22;
  }
  
  &.drag-active {
    border-color: #238636;
    background-color: #0c2d6b;
  }
`;

const UploadIcon = styled.div`
  margin-bottom: 10px;
  color: #7d8590;
`;

const UploadText = styled.div`
  font-size: 14px;
  color: #c9d1d9;
  margin-bottom: 5px;
`;

const UploadSubtext = styled.div`
  font-size: 12px;
  color: #7d8590;
`;

const FileInfo = styled.div`
  margin-top: 15px;
  padding: 10px;
  background-color: #161b22;
  border-radius: 6px;
  border: 1px solid #30363d;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const FileDetails = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
`;

const FileName = styled.span`
  font-size: 13px;
  color: #c9d1d9;
  font-weight: 500;
`;

const FileSize = styled.span`
  font-size: 12px;
  color: #7d8590;
`;

const RemoveButton = styled.button`
  background: none;
  border: none;
  color: #7d8590;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    color: #f85149;
    background-color: #21262d;
  }
`;

const SupportedFormats = styled.div`
  margin-top: 10px;
  font-size: 11px;
  color: #7d8590;
`;

function FileUpload({ onFileUpload, uploadedFile, onRemoveFile }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc']
    },
    multiple: false
  });

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (uploadedFile) {
    return (
      <div>
        <FileInfo>
          <FileDetails>
            <FileText size={16} color="#58a6ff" />
            <div>
              <FileName>{uploadedFile.name}</FileName>
              <br />
              <FileSize>{formatFileSize(uploadedFile.size)}</FileSize>
            </div>
          </FileDetails>
          <RemoveButton onClick={onRemoveFile}>
            <X size={14} />
          </RemoveButton>
        </FileInfo>
      </div>
    );
  }

  return (
    <div>
      <UploadContainer 
        {...getRootProps()} 
        className={isDragActive ? 'drag-active' : ''}
      >
        <input {...getInputProps()} />
        <UploadIcon>
          <Upload size={32} />
        </UploadIcon>
        <UploadText>
          {isDragActive ? 'Drop your file here' : 'Upload a data file'}
        </UploadText>
        <UploadSubtext>
          or click to browse
        </UploadSubtext>
        <SupportedFormats>
          Supports: CSV, Excel (.xlsx, .xls), Text (.txt), Word (.doc)
        </SupportedFormats>
      </UploadContainer>
    </div>
  );
}

export default FileUpload; 