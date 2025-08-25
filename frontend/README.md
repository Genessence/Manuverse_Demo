# Manuverse AI Frontend

A modern, ChatGPT-style dark themed React frontend for the Multi-Agent Data Analysis system.

## 🎨 Features

- **ChatGPT-style Dark Theme**: Beautiful dark UI with GitHub-inspired colors
- **Real-time Chat Interface**: Interactive chat with AI agents
- **File Upload**: Drag & drop support for CSV, Excel, and text files
- **Data Preview**: Sidebar showing uploaded file information
- **Chart Visualization**: Dynamic charts using Recharts library
- **Responsive Design**: Works on desktop and mobile devices
- **Markdown Support**: Rich text formatting in chat messages

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn
- Python backend running (see main project README)

### Installation

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

4. **Open your browser** and go to `http://localhost:3000`

## 🏗️ Architecture

### Components Structure
```
src/
├── App.js                 # Main application component
├── components/
│   ├── FileUpload.js      # File upload with drag & drop
│   ├── ChatMessage.js     # Individual chat messages
│   ├── DataPreview.js     # Sidebar data preview
│   └── ChartDisplay.js    # Chart visualization
└── index.js              # React entry point
```

### Key Features

#### File Upload
- Supports CSV, Excel (.xlsx, .xls), Text (.txt), Word (.doc)
- Drag & drop interface
- File size and type validation
- Preview of uploaded data

#### Chat Interface
- Real-time message display
- Loading states with animated dots
- Markdown rendering for rich text
- Timestamp display
- Auto-scroll to latest messages

#### Data Visualization
- Bar charts, line charts, pie charts, area charts
- Dark theme optimized
- Responsive design
- Interactive tooltips

## 🎨 Theme Colors

The UI uses a GitHub-inspired dark theme:

- **Background**: `#0d1117` (main), `#161b22` (sidebar)
- **Text**: `#c9d1d9` (primary), `#7d8590` (secondary)
- **Borders**: `#30363d`
- **Accent**: `#58a6ff` (blue), `#238636` (green)
- **Error**: `#f85149` (red)

## 🔧 Configuration

### Backend Integration
The frontend is configured to proxy requests to the Python backend at `http://localhost:8501`. Update the proxy in `package.json` if your backend runs on a different port.

### API Endpoints
The frontend expects the following API endpoints:
- `POST /api/analyze` - Send analysis queries
- `POST /api/upload` - Upload files

## 📱 Responsive Design

The interface is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## 🛠️ Development

### Available Scripts
- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Adding New Chart Types
To add new chart types, update the `ChartDisplay.js` component and add new cases to the `renderChart()` function.

### Styling
The app uses styled-components for styling. All components follow the dark theme color scheme defined above.

## 🔗 Backend Integration

This frontend is designed to work with the Python Streamlit backend. Make sure your backend is running and accessible at the configured proxy URL.

## 📄 License

This project is part of the Manuverse AI Multi-Agent Data Analysis system. 