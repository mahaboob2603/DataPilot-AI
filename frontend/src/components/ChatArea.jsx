import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { FiSend } from 'react-icons/fi';
import MessageBubble from './MessageBubble';
import './ChatArea.css';

function ChatArea({ session, messages, setMessages, activeFile, apiBaseUrl, query, setQuery }) {
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const userMessage = { role: 'user', content: query };
    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setIsLoading(true);

    try {
      const res = await axios.post(`${apiBaseUrl}/analyze`, {
        query: userMessage.content,
        filename: activeFile,
        session_id: session?.id
      });

      const assistantMessage = {
        role: 'assistant',
        content: res.data.insight,
        chart_url: res.data.chart_url,
        chart_json: res.data.chart_json,
        export_url: res.data.export_url,
        data_preview: res.data.data_preview,
        tool_calls: res.data.tool_calls_made
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, {
        role: 'system',
        content: `Error: ${err.response?.data?.detail || err.message}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const suggestions = [
    "Plot the distribution of the status column",
    "Show the top 5 values by count",
    "Clean the dataset",
    "Forecast trends for 30 days"
  ];

  return (
    <div className="chat-container">
      <div className="messages-area glass-panel">
        {messages.length === 0 && (
          <div className="empty-chat-state">
            <div className="suggestions">
              {suggestions.map((s, i) => (
                <button key={i} className="suggestion-chip" onClick={() => setQuery(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <MessageBubble key={idx} msg={msg} apiBaseUrl={apiBaseUrl} />
        ))}
        
        {isLoading && (
          <div className="loading-bubble">
            <div className="spinner"></div>
            <span>Analyzing...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area glass-panel">
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Ask anything about ${activeFile}...`}
            disabled={isLoading}
          />
          <button type="submit" disabled={!query.trim() || isLoading} className="send-btn">
            <FiSend />
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatArea;
