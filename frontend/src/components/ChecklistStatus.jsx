import React from 'react';
import { CheckCircle2, XCircle, AlertCircle, Clock, HelpCircle, Layers } from 'lucide-react';

const CHECKLIST_ORDER = [
  { key: 'property_type', label: '1. Property Type', desc: 'Residential, Commercial, Industrial (No Agri)' },
  { key: 'ownership_status', label: '2. Ownership Status', desc: 'Sole or Joint Ownership permitted' },
  { key: 'original_documents', label: '3. Original Documents', desc: 'Original title deeds must be available' },
  { key: 'requested_amount', label: '4. Requested Amount', desc: 'Max ₹75,00,000 limit' },
  { key: 'occupation_and_income_mode', label: '5. Occupation & Income', desc: 'Salaried / Self-Employed with Bank credit' },
  { key: 'market_value', label: '6. Current Market Value', desc: 'Estimated property market value' },
  { key: 'tenure', label: '7. Repayment Tenure', desc: '3 to 15 years inclusive' },
];

export default function ChecklistStatus({ checklist = {}, state = {} }) {
  const items = CHECKLIST_ORDER.map(itemDef => {
    const itemData = checklist[itemDef.key] || {};
    return {
      ...itemDef,
      state: itemData.state || 'UNKNOWN',
      value: itemData.value,
      clarificationNote: itemData.clarification_note,
    };
  });

  const answeredCount = items.filter(i => i.state === 'ANSWERED').length;
  const progressPercent = Math.round((answeredCount / 7) * 100);

  const getStatusBadge = (itemState) => {
    switch (itemState) {
      case 'ANSWERED':
        return (
          <span className="badge badge-qualified" style={{ fontSize: '0.7rem' }}>
            <CheckCircle2 size={12} /> Passed
          </span>
        );
      case 'DISQUALIFIED':
        return (
          <span className="badge badge-disqualified" style={{ fontSize: '0.7rem' }}>
            <XCircle size={12} /> Ineligible
          </span>
        );
      case 'NEEDS_CLARIFICATION':
        return (
          <span className="badge badge-busy" style={{ fontSize: '0.7rem' }}>
            <AlertCircle size={12} /> Clarify
          </span>
        );
      case 'PENDING_CONFIRMATION':
        return (
          <span className="badge badge-transfer" style={{ fontSize: '0.7rem' }}>
            <Clock size={12} /> Cap Pending
          </span>
        );
      default:
        return (
          <span className="badge" style={{ background: 'rgba(255,255,255,0.06)', color: 'var(--text-muted)', fontSize: '0.7rem' }}>
            <HelpCircle size={12} /> Unanswered
          </span>
        );
    }
  };

  const formatValue = (key, val) => {
    if (val === null || val === undefined) return null;
    if (key === 'requested_amount' || key === 'market_value') {
      return `₹${Number(val).toLocaleString('en-IN')}`;
    }
    if (key === 'tenure') {
      return `${val} Years`;
    }
    if (typeof val === 'object') {
      return `${val.occupation || ''} (${val.income_mode || ''})`;
    }
    return String(val).toUpperCase();
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Layers size={18} color="var(--accent-cyan)" />
          <h2 style={{ fontSize: '1rem', fontWeight: '700', color: '#ffffff' }}>7-Point Qualification Checklist</h2>
        </div>
        <span style={{ fontSize: '0.85rem', fontWeight: '700', color: answeredCount === 7 ? 'var(--status-qualified)' : 'var(--text-secondary)' }}>
          {answeredCount} / 7 Completed ({progressPercent}%)
        </span>
      </div>

      {/* Progress Bar */}
      <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: 'var(--radius-full)', overflow: 'hidden' }}>
        <div style={{
          width: `${progressPercent}%`,
          height: '100%',
          background: answeredCount === 7 ? 'linear-gradient(90deg, #10b981, #059669)' : 'linear-gradient(90deg, var(--hc-red), #ff4d58)',
          borderRadius: 'var(--radius-full)',
          transition: 'width 0.4s ease'
        }} />
      </div>

      {/* Checklist Items */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {items.map(item => {
          const valDisplay = formatValue(item.key, item.value);
          const isAnswered = item.state === 'ANSWERED';
          const isDisq = item.state === 'DISQUALIFIED';

          return (
            <div
              key={item.key}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '10px 14px',
                borderRadius: 'var(--radius-sm)',
                background: isAnswered ? 'rgba(16, 185, 129, 0.04)' : isDisq ? 'rgba(239, 68, 68, 0.05)' : 'rgba(255, 255, 255, 0.02)',
                border: `1px solid ${isAnswered ? 'rgba(16, 185, 129, 0.2)' : isDisq ? 'rgba(239, 68, 68, 0.2)' : 'var(--border-subtle)'}`,
              }}
            >
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: '600', color: '#ffffff' }}>
                  {item.label}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {valDisplay ? <strong style={{ color: 'var(--accent-cyan)' }}>Value: {valDisplay}</strong> : item.desc}
                </div>
                {item.clarificationNote && (
                  <div style={{ fontSize: '0.72rem', color: 'var(--status-busy)', marginTop: '2px' }}>
                    Note: {item.clarificationNote}
                  </div>
                )}
              </div>
              <div>{getStatusBadge(item.state)}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
