import { FiLayers } from 'react-icons/fi';
import './ColumnsPanel.css';

function ColumnsPanel({ columns, onColumnClick }) {
  if (!columns || columns.length === 0) return null;

  return (
    <aside className="columns-panel glass-panel animate-fade-in">
      <div className="sidebar-section">
        <h3><FiLayers /> Dataset Columns</h3>
        <p className="columns-hint">Click a column to ask a question</p>
        <ul className="column-list">
          {columns.map((col, idx) => (
            <li 
              key={idx} 
              className="column-item clickable"
              onClick={() => onColumnClick(col)}
            >
              <span className="col-icon">#</span>
              <span className="col-name">{col}</span>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}

export default ColumnsPanel;
