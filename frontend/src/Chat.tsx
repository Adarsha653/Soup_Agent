import React, { useState } from 'react';

interface Message {
  role: 'user' | 'agent';
  content: string;
  trace?: any[];
  sources?: string[];
}

function parseSummaryToList(summary: string): string[] {
  // Split on newlines or dash+space, filter out empty and repeated dashes
  return summary
    .split(/\n| - |• /)
    .map(s => s.replace(/^[-•\s]+/, '').trim())
    .filter(s => s && !s.toLowerCase().startsWith('agent:'));
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg: Message = { role: 'user', content: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/agent-chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs,
        { role: 'agent', content: data.response || data.error || 'No response', trace: data.trace, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { role: 'agent', content: 'Error contacting backend.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div style={{ maxWidth: 1100, margin: '2rem auto', padding: 24, background: '#fff', borderRadius: 12, color: '#222', fontFamily: 'Inter, sans-serif', boxShadow: '0 2px 16px rgba(0,0,0,0.07)' }}>
      <h2 style={{ textAlign: 'center', marginBottom: 24, color: '#222', fontWeight: 800, fontSize: 32 }}>Agent Chat</h2>
      <div style={{ minHeight: 200, marginBottom: 16 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            display: 'flex',
            flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
            alignItems: 'flex-start',
            margin: '18px 0'
          }}>
            <div style={{
              background: msg.role === 'user' ? '#e3f0ff' : '#f5f5f5',
              color: '#222',
              borderRadius: 16,
              padding: '20px 32px',
              maxWidth: '95%',
              minWidth: 350,
              boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
              wordBreak: 'break-word',
              position: 'relative',
              border: msg.role === 'user' ? '1.5px solid #4e8cff' : '1.5px solid #e0e0e0',
              marginLeft: msg.role === 'user' ? 32 : 8,
              marginRight: msg.role === 'agent' ? 32 : 0,
              textAlign: 'left',
            }}>
              <div style={{ fontWeight: 700, marginBottom: 8, fontSize: 16, color: msg.role === 'user' ? '#4e8cff' : '#222' }}>{msg.role === 'user' ? 'You' : 'Agent'}</div>
              {/* Render agent summary as bullet list if possible */}
              {msg.role === 'agent' && msg.content && parseSummaryToList(msg.content).length > 1 ? (
                <>
                  <div style={{ fontWeight: 700, fontSize: 20, marginBottom: 8, color: '#222' }}>Today's News Highlights</div>
                  <ul style={{ paddingLeft: 28, margin: 0, fontSize: 17, lineHeight: 1.7, textAlign: 'left' }}>
                    {parseSummaryToList(msg.content).map((item, idx) => <li key={idx} style={{ marginBottom: 8 }}>{item}</li>)}
                  </ul>
                </>
              ) : (
                <span style={{ fontSize: 17 }}>{msg.content}</span>
              )}
              {/* Sources as links */}
              {msg.role === 'agent' && msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: 18 }}>
                  <b style={{ fontSize: 16 }}>Top sources:</b>{' '}
                  {msg.sources.map((src, idx) => (
                    <a key={idx} href={src} target="_blank" rel="noopener noreferrer" style={{
                      marginRight: 16,
                      color: '#1976d2',
                      textDecoration: 'underline',
                      fontWeight: 500,
                      fontSize: 16
                    }}>
                      {src.replace(/^https?:\/\//, '').replace(/\/$/, '')}
                    </a>
                  ))}
                  <div style={{ color: '#888', fontSize: '1em', marginTop: 2 }}>For more news, visit the sources above.</div>
                </div>
              )}
              {/* Tool trace, collapsible */}
              {msg.role === 'agent' && msg.trace && msg.trace.length > 0 && (
                <details style={{ fontSize: '1em', marginTop: 18, background: '#f7f7f7', padding: 12, borderRadius: 8, color: '#333' }}>
                  <summary style={{ cursor: 'pointer', fontWeight: 500 }}>Tool Trace</summary>
                  <ul style={{ margin: 0, paddingLeft: 18, fontFamily: 'monospace', color: '#1976d2' }}>
                    {msg.trace.map((step, j) => (
                      <li key={j} style={{ marginBottom: 8 }}>
                        <b>{step.tool}</b><br />
                        <b>Input:</b> {JSON.stringify(step.input)}<br />
                        <b>Output:</b> {Array.isArray(step.output) ? step.output.join(', ') : JSON.stringify(step.output)}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          </div>
        ))}
        {loading && <div style={{ textAlign: 'center', marginTop: 24, color: '#1976d2' }}><i>Agent is typing...</i></div>}
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          style={{ flex: 1, padding: '16px 18px', borderRadius: 8, border: '1.5px solid #e0e0e0', fontSize: 18, background: '#fff', color: '#222' }}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{ padding: '16px 32px', borderRadius: 8, background: '#1976d2', color: '#fff', border: 'none', fontWeight: 700, fontSize: 18, cursor: loading ? 'not-allowed' : 'pointer' }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default Chat; 