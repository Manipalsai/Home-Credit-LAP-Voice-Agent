import React, { useState } from 'react';
import { Play, CheckCircle2, XCircle, ChevronDown, ChevronRight, ListFilter, ArrowRight } from 'lucide-react';
import { runSimulation } from '../api';

export default function ScenarioRunner({ scenarios = [], onApplySession }) {
  const [runningId, setRunningId] = useState(null);
  const [results, setResults] = useState({});
  const [expandedId, setExpandedId] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');

  const handleRun = async (scenarioId) => {
    try {
      setRunningId(scenarioId);
      const res = await runSimulation(scenarioId);
      setResults(prev => ({ ...prev, [scenarioId]: res }));
      setExpandedId(scenarioId);
    } catch (err) {
      alert(`Error running scenario: ${err.message}`);
    } finally {
      setRunningId(null);
    }
  };

  const handleRunAll = async () => {
    for (const sc of scenarios) {
      await handleRun(sc.id);
    }
  };

  const categories = ['all', ...new Set(scenarios.map(s => s.category))];
  const filtered = filterCategory === 'all' ? scenarios : scenarios.filter(s => s.category === filterCategory);

  return (
    <div className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#ffffff' }}>Predefined Automated Test Scenarios</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            Execute multi-turn synthetic customer scenarios to verify business rules, disqualification exits, and cap negotiation.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={handleRunAll}
            className="btn-primary"
            style={{ fontSize: '0.82rem', padding: '8px 14px' }}
          >
            <Play size={14} /> Run All Scenarios
          </button>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            style={{
              padding: '6px 12px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.75rem',
              fontWeight: '600',
              background: filterCategory === cat ? 'var(--hc-red-subtle)' : 'rgba(255, 255, 255, 0.04)',
              color: filterCategory === cat ? '#ffffff' : 'var(--text-secondary)',
              border: `1px solid ${filterCategory === cat ? 'rgba(227, 28, 37, 0.4)' : 'var(--border-subtle)'}`,
            }}
          >
            {cat.replace(/_/g, ' ').toUpperCase()}
          </button>
        ))}
      </div>

      {/* Scenarios List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filtered.map(sc => {
          const runRes = results[sc.id];
          const isExpanded = expandedId === sc.id;

          return (
            <div
              key={sc.id}
              style={{
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
                background: 'rgba(255, 255, 255, 0.02)',
                overflow: 'hidden'
              }}
            >
              <div style={{
                padding: '14px 18px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '12px',
                cursor: 'pointer'
              }}
                onClick={() => setExpandedId(isExpanded ? null : sc.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {isExpanded ? <ChevronDown size={18} color="var(--text-muted)" /> : <ChevronRight size={18} color="var(--text-muted)" />}
                  <div>
                    <div style={{ fontSize: '0.9rem', fontWeight: '700', color: '#ffffff' }}>
                      {sc.name}
                    </div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                      {sc.description}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    Expected: <strong style={{ color: 'var(--accent-cyan)' }}>{sc.expected_outcome}</strong>
                  </span>

                  {runRes && (
                    <span className={`badge ${runRes.passed ? 'badge-qualified' : 'badge-disqualified'}`}>
                      {runRes.passed ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                      {runRes.passed ? 'PASSED' : 'FAILED'}
                    </span>
                  )}

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRun(sc.id);
                    }}
                    disabled={runningId === sc.id}
                    className="btn-secondary"
                    style={{ padding: '6px 12px', fontSize: '0.75rem' }}
                  >
                    <Play size={12} /> {runningId === sc.id ? 'Running...' : 'Run'}
                  </button>
                </div>
              </div>

              {/* Expanded Simulation Result */}
              {isExpanded && runRes && (
                <div style={{
                  padding: '16px 20px',
                  background: 'rgba(10, 13, 20, 0.6)',
                  borderTop: '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '12px'
                }}>
                  <div style={{
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-sm)',
                    background: runRes.passed ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    border: `1px solid ${runRes.passed ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    fontSize: '0.85rem'
                  }}>
                    <span>
                      Outcome: <strong style={{ color: '#ffffff' }}>{runRes.actual_outcome}</strong> | Total Turns: <strong>{runRes.total_turns}</strong>
                    </span>
                    <span style={{ fontWeight: '700', color: runRes.passed ? 'var(--status-qualified)' : 'var(--status-disqualified)' }}>
                      {runRes.passed ? 'VERIFIED PASSED' : runRes.failure_reason}
                    </span>
                  </div>

                  {/* Step by Step turns */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: '700', color: 'var(--text-muted)' }}>
                      TURN EXECUTION TRAJECTORY:
                    </span>
                    {runRes.steps.map((st) => (
                      <div
                        key={st.turn_index}
                        style={{
                          padding: '10px 14px',
                          borderRadius: 'var(--radius-sm)',
                          background: 'rgba(255, 255, 255, 0.02)',
                          border: '1px solid var(--border-subtle)',
                          fontSize: '0.82rem',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '4px'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--accent-cyan)', fontWeight: '600' }}>
                          <span>Turn #{st.turn_index}: "{st.customer_utterance}"</span>
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Stage: {st.stage}</span>
                        </div>
                        <div style={{ color: 'var(--text-secondary)' }}>
                          <strong style={{ color: 'var(--hc-red)' }}>Agent:</strong> {st.agent_response}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
