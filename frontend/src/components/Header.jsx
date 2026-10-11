import React from 'react';
import { PhoneCall, ShieldCheck, Zap, Activity, Radio } from 'lucide-react';

export default function Header({ health, voiceStatus }) {
  const isHealthy = health?.status === 'healthy';
  const activeProvider = voiceStatus?.active_platform || 'Retell AI';

  return (
    <header className="glass-panel" style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: 'var(--radius-md)',
          background: 'linear-gradient(135deg, #e31c25 0%, #990f16 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(227, 28, 37, 0.4)'
        }}>
          <PhoneCall size={22} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em', color: '#ffffff' }}>
              Home Credit LAP Voice Agent
            </h1>
            <span className="badge badge-simulated" style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <Radio size={12} className="animate-pulse" /> Local Simulation Mode
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Loan Against Property Qualification Engine & Interactive Conversational Testbed
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Engine Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: isHealthy ? 'var(--status-qualified)' : 'var(--status-disqualified)',
            boxShadow: isHealthy ? '0 0 8px var(--status-qualified)' : '0 0 8px var(--status-disqualified)'
          }} />
          <span>Engine: <strong style={{ color: '#ffffff' }}>{isHealthy ? 'Online' : 'Connecting'}</strong></span>
        </div>

        {/* Telephony Adapter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span className="badge badge-voice">
            <Zap size={12} /> Provider: {activeProvider.toUpperCase()}
          </span>
        </div>
      </div>
    </header>
  );
}
