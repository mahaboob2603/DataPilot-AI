import { FiMessageSquare, FiPlus, FiDatabase, FiLayers } from 'react-icons/fi';
import './Sidebar.css';

function Sidebar({ sessionsList, currentSessionId, onSelectSession, onNewSession, activeFile }) {
  return (
    <aside className="sidebar glass-panel animate-fade-in">
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={onNewSession}>
          <FiPlus /> New Analysis
        </button>
      </div>



      <div className="sidebar-section sessions-history">
        <h3><FiDatabase /> Session History</h3>
        <ul className="session-list">
          {sessionsList.map(session => (
            <li 
              key={session.id} 
              className={`session-item ${session.id === currentSessionId ? 'active' : ''}`}
              onClick={() => onSelectSession(session.id)}
            >
               <FiMessageSquare />
               <div className="session-info">
                 <span className="session-title">{session.title}</span>
                 <span className="session-date">{new Date(session.updated_at).toLocaleDateString()}</span>
               </div>
            </li>
          ))}
          {sessionsList.length === 0 && (
            <div className="empty-text">No history yet.</div>
          )}
        </ul>
      </div>
    </aside>
  );
}

export default Sidebar;
