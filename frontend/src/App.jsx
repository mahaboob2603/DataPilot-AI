import { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import FileUpload from './components/FileUpload';
import ColumnsPanel from './components/ColumnsPanel';
import './App.css';

const API_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeFile, setActiveFile] = useState(null);
  const [columns, setColumns] = useState([]);
  const [sessionsList, setSessionsList] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [query, setQuery] = useState('');

  // Fetch all sessions on mount
  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/sessions`);
      setSessionsList(res.data.sessions);
    } catch (err) {
      console.error("Failed to fetch sessions", err);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/sessions/${sessionId}`);
      setSession(res.data.session);
      setMessages(res.data.messages || []);
      if (res.data.session.filename) {
        setActiveFile(res.data.session.filename);
        fetchColumns(res.data.session.filename);
      }
    } catch (err) {
      console.error("Failed to load session", err);
    }
  };

  const createNewSession = async (filename = null) => {
    try {
      const res = await axios.post(`${API_BASE_URL}/sessions?title=Analysis&filename=${filename || ''}`);
      setSession(res.data);
      setMessages([]);
      fetchSessions();
    } catch (err) {
      console.error("Failed to create session", err);
    }
  };

  const fetchColumns = async (filename) => {
    try {
      const res = await axios.get(`${API_BASE_URL}/columns/${filename}`);
      setColumns(res.data.columns.map(c => c.name));
    } catch (err) {
      console.error("Failed to fetch columns", err);
    }
  };

  const handleFileUpload = async (file) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(`${API_BASE_URL}/upload`, formData);
      const filename = res.data.filename;
      setActiveFile(filename);
      setColumns(res.data.columns);
      
      // Update current session or create new one
      if (session) {
        await axios.post(`${API_BASE_URL}/sessions?title=Analysis for ${filename}&filename=${filename}`);
        fetchSessions();
      } else {
        await createNewSession(filename);
      }

      setMessages(prev => [...prev, {
        role: 'system',
        content: res.data.message
      }]);

    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className={`app-container ${!activeFile ? 'landing-state' : ''}`}>
      <div className="background-decor">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
        <div className="blob blob-3"></div>
      </div>

      {activeFile && (
        <Sidebar 
          sessionsList={sessionsList} 
          currentSessionId={session?.id}
          onSelectSession={loadSession}
          onNewSession={() => {setActiveFile(null); createNewSession();}}
          columns={columns}
          activeFile={activeFile}
        />
      )}
      
      <main className="main-content">
        {activeFile && (
          <header className="header glass-panel">
            <h1>DataPilot AI ✦ <span>Pro</span></h1>
            {activeFile && (
               <div className="active-file-chip">
                 <span>{activeFile}</span>
                 <button onClick={() => {setActiveFile(null); setColumns([]);}} className="clear-btn">&times;</button>
               </div>
            )}
          </header>
        )}

        <div className="workspace">
          {activeFile ? (
            <>
              <ChatArea 
                session={session}
                messages={messages}
                setMessages={setMessages}
                activeFile={activeFile}
                apiBaseUrl={API_BASE_URL}
                query={query}
                setQuery={setQuery}
              />
              <ColumnsPanel 
                columns={columns} 
                onColumnClick={(col) => setQuery(`Summarize and show the distribution of "${col}"`)} 
              />
            </>
          ) : (
            <FileUpload 
              onUpload={handleFileUpload} 
              isUploading={isUploading} 
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
