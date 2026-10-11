import React, { useState, useEffect } from 'react';
import { Radio, Zap, ExternalLink, Copy, Check, ShieldCheck, Download, AlertTriangle } from 'lucide-react';
import { fetchRetellExport, fetchBolnaExport } from '../api';

export default function VoiceProviderPanel({ voiceStatus }) {
  const [retellSchema, setRetellSchema] = useState(null);
  const [bolnaSchema, setBolnaSchema] = useState(null);
  const [activeTab, setActiveTab] = useState('retell');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchRetellExport().then(setRetellSchema).catch(() => {});
    fetchBolnaExport().then(setBolnaSchema).catch(() => {});
  }, []);

  const handleCopySchema = (schema) => {
    navigator.clipboard.writeText(JSON.stringify(schema, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#ffffff' }}>
            Voice Telephony Platform Integration (Retell AI & Bolna)
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Configure production voice providers, export platform-ready agent schemas, and verify real-call test status.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setActiveTab('retell')}
            className={`tab-btn ${activeTab === 'retell' ? 'active' : ''}`}
          >
            <Zap size={14} /> Retell AI (Recommended)
          </button>
          <button
            onClick={() => setActiveTab('bolna')}
            className={`tab-btn ${activeTab === 'bolna' ? 'active' : ''}`}
          >
            <Radio size={14} /> Bolna Platform
          </button>
        </div>
      </div>

      {/* Retell Tab */}
      {activeTab === 'retell' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{
            padding: '16px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(56, 189, 248, 0.05)',
            border: '1px solid rgba(56, 189, 248, 0.2)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: '700', fontSize: '0.9rem', color: 'var(--accent-cyan)' }}>
                Retell AI Agent Deployment Specification
              </span>
              <a
                href="https://beta.retellai.com"
                target="_blank"
                rel="noreferrer"
                style={{ color: 'var(--accent-cyan)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
              >
                Retell Dashboard <ExternalLink size={12} />
              </a>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Retell AI offers low-latency conversational audio (~500ms) with native Indian English / Hindi voices (e.g. 11labs-Pooja).
              The System Prompt and 11 dynamic variables map directly into Retell's Agent Prompt schema.
            </p>
          </div>

          {/* Setup Checklist */}
          <div style={{
            padding: '16px',
            background: 'rgba(255, 255, 255, 0.02)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
            display: 'flex',
            flexDirection: 'column',
            gap: '10px'
          }}>
            <span style={{ fontSize: '0.82rem', fontWeight: '700', color: '#ffffff' }}>
              Real Call Validation Checklist (Level 5):
            </span>
            <ul style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <li>1. Obtain API key from Retell AI Console (or set in local <code>.env</code> file).</li>
              <li>2. Create Agent using the exported JSON configuration below or run <code>python scripts/export_retell_agent.py</code>.</li>
              <li>3. Configure Webhook URL in Retell to <code>https://your-domain/api/voice/webhook/retell</code> with secret verification.</li>
              <li>4. Purchase or assign a trial telephony DID phone number in Retell console.</li>
              <li>5. Conduct authorized test call to synthetic customer test number.</li>
              <li>6. Verify recording audio URL and real transcript in dashboard.</li>
            </ul>
          </div>

          {/* JSON Schema Viewer */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-muted)' }}>
                RETELL AGENT CREATION SCHEMA (POST /create-agent):
              </span>
              <button
                onClick={() => handleCopySchema(retellSchema)}
                className="btn-secondary"
                style={{ padding: '4px 10px', fontSize: '0.75rem' }}
              >
                {copied ? <Check size={12} color="var(--status-qualified)" /> : <Copy size={12} />}
                {copied ? 'Copied' : 'Copy JSON'}
              </button>
            </div>
            <pre style={{
              padding: '16px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(10, 13, 20, 0.8)',
              border: '1px solid var(--border-subtle)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem',
              color: 'var(--accent-cyan)',
              maxHeight: '260px',
              overflowY: 'auto'
            }}>
              {retellSchema ? JSON.stringify(retellSchema, null, 2) : 'Loading schema...'}
            </pre>
          </div>
        </div>
      )}

      {/* Bolna Tab */}
      {activeTab === 'bolna' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{
            padding: '16px',
            borderRadius: 'var(--radius-sm)',
            background: 'rgba(168, 85, 247, 0.05)',
            border: '1px solid rgba(168, 85, 247, 0.2)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: '700', fontSize: '0.9rem', color: '#c084fc' }}>
                Bolna Open-Source Voice Engine Specification
              </span>
              <a
                href="https://bolna.dev"
                target="_blank"
                rel="noreferrer"
                style={{ color: '#c084fc', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
              >
                Bolna Documentation <ExternalLink size={12} />
              </a>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
              Bolna provides modular conversational agent graphs supporting Indian language models, Twilio / Exotel telephony, and custom webhook callbacks.
            </p>
          </div>

          {/* JSON Schema Viewer */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-muted)' }}>
                BOLNA AGENT SPECIFICATION JSON:
              </span>
              <button
                onClick={() => handleCopySchema(bolnaSchema)}
                className="btn-secondary"
                style={{ padding: '4px 10px', fontSize: '0.75rem' }}
              >
                {copied ? <Check size={12} color="var(--status-qualified)" /> : <Copy size={12} />}
                {copied ? 'Copied' : 'Copy JSON'}
              </button>
            </div>
            <pre style={{
              padding: '16px',
              borderRadius: 'var(--radius-sm)',
              background: 'rgba(10, 13, 20, 0.8)',
              border: '1px solid var(--border-subtle)',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.75rem',
              color: '#c084fc',
              maxHeight: '260px',
              overflowY: 'auto'
            }}>
              {bolnaSchema ? JSON.stringify(bolnaSchema, null, 2) : 'Loading schema...'}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
