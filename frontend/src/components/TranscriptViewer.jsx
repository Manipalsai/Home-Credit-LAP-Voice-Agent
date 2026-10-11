import React, { useState } from 'react';
import { FileText, Download, Copy, Check } from 'lucide-react';

export default function TranscriptViewer({ messages = [], state = {} }) {
  const [copied, setCopied] = useState(false);

  const generateTextTranscript = () => {
    let out = `========================================================\n`;
    out += `HOME CREDIT LAP VOICE AGENT — CALL TRANSCRIPT\n`;
    out += `Customer: ${state.customer_name || 'Rajesh Sharma'}\n`;
    out += `Session ID: ${state.session_id || 'sim'}\n`;
    out += `Stage: ${state.stage || 'unknown'}\n`;
    out += `Final Outcome: ${state.outcome || 'in_progress'}\n`;
    out += `========================================================\n\n`;

    messages.forEach((m, idx) => {
      const sender = m.sender === 'agent' ? 'AGENT (Pooja)' : 'CUSTOMER';
      out += `[Turn ${idx + 1}] ${sender}:\n${m.text}\n\n`;
    });
    return out;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateTextTranscript());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadTxt = () => {
    const text = generateTextTranscript();
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${state.session_id || 'session'}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadJson = () => {
    const data = {
      session_id: state.session_id,
      customer_name: state.customer_name,
      stage: state.stage,
      outcome: state.outcome,
      state: state,
      messages: messages,
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${state.session_id || 'session'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText size={18} color="var(--accent-cyan)" />
          <h2 style={{ fontSize: '1rem', fontWeight: '700', color: '#ffffff' }}>Conversation Transcript</h2>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={handleCopy} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
            {copied ? <Check size={14} color="var(--status-qualified)" /> : <Copy size={14} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
          <button onClick={handleDownloadTxt} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
            <Download size={14} /> TXT
          </button>
          <button onClick={handleDownloadJson} className="btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
            <Download size={14} /> JSON
          </button>
        </div>
      </div>

      <div style={{
        padding: '16px',
        background: 'rgba(10, 13, 20, 0.7)',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--border-subtle)',
        fontFamily: 'var(--font-mono)',
        fontSize: '0.8rem',
        color: 'var(--text-secondary)',
        maxHeight: '300px',
        overflowY: 'auto',
        whiteSpace: 'pre-wrap',
        lineHeight: '1.6'
      }}>
        {messages.length === 0 ? (
          <span style={{ color: 'var(--text-muted)' }}>No messages recorded in current session yet.</span>
        ) : (
          generateTextTranscript()
        )}
      </div>
    </div>
  );
}
