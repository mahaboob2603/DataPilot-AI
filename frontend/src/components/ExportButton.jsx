import { FiDownload } from 'react-icons/fi';

function ExportButton({ url, label = "Download Data" }) {
  if (!url) return null;

  const downloadFile = (e) => {
    e.preventDefault();
    window.location.href = url;
  };

  return (
    <button 
      onClick={downloadFile}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 16px',
        background: 'rgba(168, 85, 247, 0.15)',
        border: '1px solid rgba(168, 85, 247, 0.4)',
        color: '#e9d5ff',
        borderRadius: '8px',
        cursor: 'pointer',
        fontSize: '0.85rem',
        fontWeight: '500',
        transition: 'all 0.2s',
        marginTop: '12px'
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.background = 'rgba(168, 85, 247, 0.25)';
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.background = 'rgba(168, 85, 247, 0.15)';
      }}
    >
      <FiDownload /> {label}
    </button>
  );
}

export default ExportButton;
