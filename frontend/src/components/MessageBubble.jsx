import { FiUser, FiCpu, FiTool, FiPieChart } from 'react-icons/fi';
import PlotlyChart from './PlotlyChart';
import ExportButton from './ExportButton';
import ErrorBoundary from './ErrorBoundary';
import './MessageBubble.css';

function MessageBubble({ msg, apiBaseUrl }) {
  if (msg.role === 'system') {
    return (
      <div className="message system-msg animate-fade-in">
        <div className="msg-content">{msg.content}</div>
      </div>
    );
  }

  const isUser = msg.role === 'user';

  // Safeguard against missing data_preview format
  let previewKeys = [];
  let previewRows = [];
  try {
    if (!isUser && msg.data_preview) {
      const firstVal = Object.values(msg.data_preview)[0];
      if (Array.isArray(firstVal) && firstVal.length > 0) {
        previewKeys = Object.keys(firstVal[0] || {});
        previewRows = firstVal;
      }
    }
  } catch (e) {
    console.error("Error parsing data preview", e);
  }

  return (
    <ErrorBoundary>
      <div className={`message ${isUser ? 'user-msg' : 'assistant-msg'} animate-fade-in`}>
        <div className="avatar glass-panel">
          {isUser ? <FiUser /> : <FiCpu className="ai-icon" />}
        </div>
        
        <div className="msg-body">
          {/* Tool calls display for AI */}
          {!isUser && msg.tool_calls && msg.tool_calls.length > 0 && (
            <div className="tool-calls-container">
              {msg.tool_calls.map((tc, idx) => {
                let params = '...';
                try {
                  params = Object.values(tc.parameters || {}).map(v => typeof v === 'object' ? JSON.stringify(v) : v).join(', ');
                } catch(e) {}
                return (
                  <div key={idx} className="tool-chip glass-panel">
                    <FiTool />
                    <span>{tc.tool_name}({params.substring(0, 30)}{params.length > 30 ? '...' : ''})</span>
                  </div>
                );
              })}
            </div>
          )}

          {/* Insight content */}
          {msg.content && (
            <div className="insight-section">
              {!isUser && <h4><FiPieChart /> Insight</h4>}
              <div className="msg-content markdown-body" dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br/>') }} />
            </div>
          )}

          {/* Data Preview */}
          {!isUser && previewKeys.length > 0 && (
            <div className="data-preview mt-3">
               <div className="table-responsive">
                  <table>
                    <thead>
                      <tr>
                        {previewKeys.map(k => (
                          <th key={k}>{k}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {previewRows.map((row, i) => (
                        <tr key={i}>
                          {previewKeys.map((k, j) => (
                            <td key={j}>{row[k] !== null && row[k] !== undefined ? String(row[k]) : 'null'}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
               </div>
            </div>
          )}

          {/* Chart Visualization */}
          {!isUser && msg.chart_json && (
            <div className="chart-container glass-panel mt-3">
              <ErrorBoundary>
                <PlotlyChart chartJsonStr={msg.chart_json} />
              </ErrorBoundary>
            </div>
          )}
          
          {/* Fallback image chart if no JSON (for backwards compat) */}
          {!isUser && msg.chart_url && !msg.chart_json && (
            <div className="chart-container glass-panel mt-3">
              <img src={`${apiBaseUrl}${msg.chart_url}`} alt="Chart" style={{ maxWidth: '100%', borderRadius: '8px' }} />
            </div>
          )}

          {/* Export Button */}
          {!isUser && msg.export_url && (
              <ExportButton url={`${apiBaseUrl}${msg.export_url}`} />
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default MessageBubble;
