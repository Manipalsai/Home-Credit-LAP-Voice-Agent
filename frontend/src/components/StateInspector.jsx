import React from 'react';
import { Cpu, ShieldAlert, CheckCircle, ArrowRight, UserCheck, PhoneForwarded, CalendarClock } from 'lucide-react';

export default function StateInspector({ state = {} }) {
  const stage = state.stage || 'greeting_verification';
  const outcome = state.outcome || 'in_progress';
  const isTerminal = state.is_terminal || false;
  const handoffPassed = state.handoff_gate_passed || false;

  const getStagePill = (stg) => {
    const formatted = stg.replace(/_/g, ' ').toUpperCase();
    return (
      <span style={{
        padding: '4px 10px',
        borderRadius: 'var(--radius-sm)',
        background: 'rgba(56, 189, 248, 0.12)',
        color: 'var(--accent-cyan)',
        fontWeight: '700',
        fontSize: '0.75rem',
        border: '1px solid rgba(56, 189, 248, 0.25)',
      }}>
        {formatted}
      </span>
    );
  };

  const getOutcomeBadge = (outc) => {
    switch (outc) {
      case 'qualified_handoff':
        return <span className="badge badge-qualified">Qualified for Expert Handoff</span>;
      case 'disqualified':
        return <span className="badge badge-disqualified">Disqualified</span>;
      case 'routed_transfer_specialist':
        return <span className="badge badge-transfer">Routed to Loan Transfer Desk</span>;
      case 'busy_callback_scheduled':
        return <span className="badge badge-busy">Callback Scheduled</span>;
      case 'wrong_person':
        return <span className="badge badge-disqualified">Wrong Person Exit</span>;
      case 'amount_cap_rejected':
        return <span className="badge badge-disqualified">75L Cap Declined</span>;
      case 'customer_declined':
        return <span className="badge badge-disqualified">Customer Declined</span>;
      default:
        return <span className="badge badge-progress">Call In Progress</span>;
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Cpu size={18} color="var(--status-transfer)" />
          <h2 style={{ fontSize: '1rem', fontWeight: '700', color: '#ffffff' }}>Engine State Inspector</h2>
        </div>
        <div>{getOutcomeBadge(outcome)}</div>
      </div>

      {/* Stage Banner */}
      <div style={{
        padding: '12px 16px',
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>CURRENT STAGE:</span>
          {getStagePill(stage)}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>Session Lifecycle:</span>
          <strong style={{ color: isTerminal ? 'var(--status-disqualified)' : 'var(--status-qualified)' }}>
            {isTerminal ? 'TERMINAL (CALL ENDED)' : 'ACTIVE CONVERSATION'}
          </strong>
        </div>
      </div>

      {/* Handoff Gate Indicator */}
      <div style={{
        padding: '12px 16px',
        borderRadius: 'var(--radius-sm)',
        background: handoffPassed ? 'rgba(16, 185, 129, 0.08)' : 'rgba(255, 255, 255, 0.02)',
        border: `1px solid ${handoffPassed ? 'rgba(16, 185, 129, 0.3)' : 'var(--border-subtle)'}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {handoffPassed ? (
            <CheckCircle size={20} color="var(--status-qualified)" />
          ) : (
            <ShieldAlert size={20} color="var(--text-muted)" />
          )}
          <div>
            <div style={{ fontSize: '0.82rem', fontWeight: '700', color: '#ffffff' }}>
              Senior Loan Expert Gate
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              {handoffPassed ? 'All 7 mandatory criteria verified & passed' : 'Gate locked until all 7 criteria pass'}
            </div>
          </div>
        </div>
        <span style={{
          fontSize: '0.75rem',
          fontWeight: '700',
          color: handoffPassed ? 'var(--status-qualified)' : 'var(--text-muted)'
        }}>
          {handoffPassed ? 'UNLOCKED' : 'LOCKED'}
        </span>
      </div>

      {/* Disqualification or Transfer Notice */}
      {state.disqualification_reason && (
        <div style={{
          padding: '12px',
          borderRadius: 'var(--radius-sm)',
          background: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--status-disqualified)', fontWeight: '700', fontSize: '0.8rem' }}>
            <ShieldAlert size={16} /> Disqualification Triggered
          </div>
          <div style={{ fontSize: '0.75rem', color: '#fca5a5' }}>
            {state.disqualification_detail || state.disqualification_reason}
          </div>
        </div>
      )}

      {state.transfer_intent && state.transfer_intent !== 'none' && (
        <div style={{
          padding: '12px',
          borderRadius: 'var(--radius-sm)',
          background: 'rgba(139, 92, 246, 0.08)',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          display: 'flex',
          flexDirection: 'column',
          gap: '4px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#c084fc', fontWeight: '700', fontSize: '0.8rem' }}>
            <PhoneForwarded size={16} /> Loan Transfer Route Triggered
          </div>
          <div style={{ fontSize: '0.75rem', color: '#e9d5ff' }}>
            {state.transfer_reason || 'Customer requested balance transfer or EMI reduction.'}
          </div>
        </div>
      )}

      {state.callback_preference && (
        <div style={{
          padding: '12px',
          borderRadius: 'var(--radius-sm)',
          background: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.3)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <CalendarClock size={18} color="var(--status-busy)" />
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--status-busy)' }}>Callback Preference</div>
            <div style={{ fontSize: '0.75rem', color: '#ffffff' }}>{state.callback_preference}</div>
          </div>
        </div>
      )}

      {/* Extracted Facts Matrix */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.78rem' }}>
        <span style={{ fontSize: '0.72rem', fontWeight: '700', color: 'var(--text-muted)' }}>EXTRACTED FACTS:</span>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          <div className="glass-panel" style={{ padding: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Customer: </span>
            <strong>{state.customer_name || '—'}</strong>
          </div>
          <div className="glass-panel" style={{ padding: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Verification: </span>
            <strong style={{ color: state.verification_status === 'verified' ? 'var(--status-qualified)' : 'inherit' }}>
              {state.verification_status || 'unverified'}
            </strong>
          </div>
          <div className="glass-panel" style={{ padding: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Loan Req: </span>
            <strong>{state.requested_amount ? `₹${state.requested_amount.toLocaleString('en-IN')}` : '—'}</strong>
          </div>
          <div className="glass-panel" style={{ padding: '8px' }}>
            <span style={{ color: 'var(--text-muted)' }}>Tenure: </span>
            <strong>{state.tenure_years ? `${state.tenure_years} Years` : '—'}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
