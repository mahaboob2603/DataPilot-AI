import { useRef } from 'react';
import { FiUploadCloud, FiBarChart2, FiMessageSquare, FiTrendingUp } from 'react-icons/fi';
import './FileUpload.css';

function FileUpload({ onUpload, isUploading }) {
  const fileInputRef = useRef(null);

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="upload-wrapper animate-fade-in">
      <div className="hero-section">
        <div className="landing-badge">AI-POWERED DATA ANALYSIS</div>
        <h1 className="hero-title">
          The <span className="gradient-text">Smartest way</span> to handle your CSV data.
        </h1>
        <p className="hero-subtitle">
          DataPilot turns your raw spreadsheets into interactive insights, 
          automated visualizations, and intelligent forecasts in one click.
        </p>
        
        <div className="feature-grid">
          <div className="feature-card">
            <FiBarChart2 className="f-icon" />
            <span>Smart Charts</span>
          </div>
          <div className="feature-card">
            <FiMessageSquare className="f-icon" />
            <span>AI Chat</span>
          </div>
          <div className="feature-card">
            <FiTrendingUp className="f-icon" />
            <span>Forecasting</span>
          </div>
        </div>
      </div>

      <div className="upload-container glass-panel">
        <div 
          className="upload-dropzone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current.click()}
        >
          <div className="upload-content">
            {isUploading ? (
              <div className="upload-loading">
                <div className="spinner upload-spinner"></div>
                <p>Processing your data...</p>
              </div>
            ) : (
              <>
                <div className="icon-wrapper">
                  <FiUploadCloud className="upload-icon" />
                </div>
                <h2>Drop your CSV here</h2>
                <p>or <span className="browse-text">select a file</span> to begin your journey</p>
                <div className="upload-hint">Supported formats: .csv (Max 10MB)</div>
              </>
            )}
          </div>
          <input 
            type="file" 
            accept=".csv" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                onUpload(e.target.files[0]);
              }
            }} 
          />
        </div>
      </div>
    </div>
  );
}

export default FileUpload;
