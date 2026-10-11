import React, { useState, useRef, useEffect } from 'react';
import { Send, RotateCcw, Bot, User, Mic, Sparkles, Volume2, ArrowRight } from 'lucide-react';

const SUGGESTED_UTTERANCES = [
  { label: 'Verify Identity', text: 'Yes, Rajesh Sharma speaking.' },
  { label: 'Accept Offer', text: 'Yes, I would like to explore the LAP offer.' },
  { label: 'Residential Property', text: 'It is a residential house in Noida.' },
  { label: 'Sole Ownership', text: 'I am the sole owner.' },
  { label: 'Original Papers Available', text: 'Yes, the original papers are safely kept at my home.' },
  { label: 'Loan Amount 50L', text: 'I need fifty lakhs.' },
  { label: 'Salaried + Bank', text: 'I am salaried and receive my salary directly into my bank account.' },
  { label: 'Market Value 1.2 Cr', text: 'The estimated market value is roughly one crore twenty lakhs.' },
  { label: 'Tenure 10 Years', text: 'Ten years.' },
  { label: 'Ask Interest Rate', text: 'What is your interest rate on this loan?' },
  { label: 'Transfer Property Loan', text: 'I already have a loan against this property and want to transfer it to reduce my EMI.' },
  { label: 'Busy Customer', text: 'I am in a meeting right now, please call me back tomorrow evening.' },
  { label: 'Agricultural Land', text: 'It is an agricultural farmland in Punjab.' },
  { label: 'Cash Income', text: 'I run a local shop and all my earnings are strictly cash in hand.' },
];

export default function CallSimulator({
  messages = [],
  onSend,
  onReset,
  loading = false,
  isTerminal = false,
  currentPrompt = null,
}) {
  const [inputText, setInputText] = useState('');
  const chatBottomRef = useRef(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputText.trim() || loading || isTerminal) return;
    onSend(inputText.trim());
    setInputText('');
  };

  const handleChipClick = (chipText) => {
    if (loading || isTerminal) return;
    onSend(chipText);
  };

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '620px', overflow: 'hidden' }}>
      {/* Simulator Bar */}
      <div style={{
        padding: '14px 20px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(255, 255, 255, 0.02)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: '50%',
            background: 'var(--hc-red-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(227, 28, 37, 0.3)'
          }}>
            <Bot size={16} color="var(--hc-red)" />
          </div>
          <div>
            <span style={{ fontSize: '0.9rem', fontWeight: '700', color: '#ffffff' }}>Live Voice Simulation Call</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginLeft: '8px' }}>
              Agent: Pooja (Home Credit India)
            </span>
          </div>
        </div>

        <button
          onClick={onReset}
          className="btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.8rem' }}
          title="Reset conversation to greeting stage"
        >
          <RotateCcw size={14} /> New Call
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div style={{
        flex: 1,
        padding: '20px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        background: 'rgba(10, 13, 20, 0.4)'
      }}>
        {messages.map((msg, index) => {
          const isAgent = msg.sender === 'agent';
          return (
            <div
              key={msg.id || index}
              style={{
                display: 'flex',
                gap: '12px',
                alignSelf: isAgent ? 'flex-start' : 'flex-end',
                maxWidth: '85%',
                flexDirection: isAgent ? 'row' : 'row-reverse',
              }}
            >
              {/* Avatar */}
              <div style={{
                width: '34px',
                height: '34px',
                borderRadius: '50%',
                background: isAgent ? 'var(--hc-red-subtle)' : 'rgba(56, 189, 248, 0.15)',
                border: `1px solid ${isAgent ? 'rgba(227, 28, 37, 0.4)' : 'rgba(56, 189, 248, 0.4)'}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}>
                {isAgent ? <Volume2 size={16} color="var(--hc-red)" /> : <User size={16} color="var(--accent-cyan)" />}
              </div>

              {/* Message Bubble */}
              <div style={{
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                background: isAgent ? 'rgba(24, 32, 50, 0.9)' : 'rgba(227, 28, 37, 0.12)',
                border: `1px solid ${isAgent ? 'var(--border-subtle)' : 'rgba(227, 28, 37, 0.3)'}`,
                boxShadow: 'var(--shadow-sm)',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '0.72rem', fontWeight: '700', color: isAgent ? 'var(--hc-red)' : 'var(--accent-cyan)' }}>
                    {isAgent ? 'POOJA (VOICE AGENT)' : 'CUSTOMER'}
                  </span>
                  {msg.metadata?.stage && (
                    <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                      {msg.metadata.stage}
                    </span>
                  )}
                </div>
                <p style={{ fontSize: '0.9rem', color: '#ffffff', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                  {msg.text}
                </p>
              </div>
            </div>
          );
        })}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            <Bot size={16} className="animate-spin" /> Processing customer speech and evaluating rules...
          </div>
        )}

        <div ref={chatBottomRef} />
      </div>

      {/* Suggested Quick Utterances */}
      {!isTerminal && (
        <div style={{
          padding: '8px 16px',
          borderTop: '1px solid var(--border-subtle)',
          background: 'rgba(16, 22, 34, 0.6)',
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          whiteSpace: 'nowrap'
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Sparkles size={12} /> Test Chips:
          </span>
          {SUGGESTED_UTTERANCES.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleChipClick(chip.text)}
              style={{
                fontSize: '0.72rem',
                padding: '4px 10px',
                borderRadius: 'var(--radius-full)',
                background: 'rgba(255, 255, 255, 0.05)',
                color: 'var(--text-secondary)',
                border: '1px solid var(--border-subtle)',
                cursor: 'pointer',
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(227, 28, 37, 0.15)';
                e.target.style.color = '#ffffff';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(255, 255, 255, 0.05)';
                e.target.style.color = 'var(--text-secondary)';
              }}
            >
              {chip.label}
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{
        padding: '14px 20px',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        gap: '12px',
        background: 'rgba(16, 22, 34, 0.95)',
        alignItems: 'center'
      }}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder={isTerminal ? "Call has ended with terminal outcome. Click 'New Call' to test again." : "Speak as customer (e.g., 'It's my residential house worth 1.5 Cr')..."}
          disabled={isTerminal || loading}
          style={{ flex: 1, fontSize: '0.9rem' }}
        />
        <button
          type="submit"
          disabled={isTerminal || loading || !inputText.trim()}
          className="btn-primary"
          style={{ opacity: isTerminal || !inputText.trim() ? 0.5 : 1 }}
        >
          <Send size={16} /> Send
        </button>
      </form>
    </div>
  );
}
