const BASE_URL = '/api';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function startConversation(customerName = 'Rajesh Sharma') {
  const res = await fetch(`${BASE_URL}/conversation/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ customer_name: customerName }),
  });
  if (!res.ok) throw new Error('Failed to start conversation');
  return res.json();
}

export async function sendTurn(sessionId, utterance) {
  const res = await fetch(`${BASE_URL}/conversation/turn`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, utterance }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to process utterance');
  }
  return res.json();
}

export async function resetConversation(sessionId, customerName = 'Rajesh Sharma') {
  const res = await fetch(`${BASE_URL}/conversation/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, customer_name: customerName }),
  });
  if (!res.ok) throw new Error('Failed to reset conversation');
  return res.json();
}

export async function fetchSessionState(sessionId) {
  const res = await fetch(`${BASE_URL}/conversation/${sessionId}`);
  if (!res.ok) throw new Error('Failed to fetch state');
  return res.json();
}

export async function fetchRenderedPrompt(sessionId) {
  const res = await fetch(`${BASE_URL}/conversation/${sessionId}/prompt`);
  if (!res.ok) throw new Error('Failed to fetch prompt');
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch(`${BASE_URL}/simulator/scenarios`);
  if (!res.ok) throw new Error('Failed to load scenarios');
  return res.json();
}

export async function runSimulation(scenarioId, customScenario = null) {
  const res = await fetch(`${BASE_URL}/simulator/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_id: scenarioId, custom_scenario: customScenario }),
  });
  if (!res.ok) throw new Error('Failed to run simulation');
  return res.json();
}

export async function fetchVoiceStatus() {
  const res = await fetch(`${BASE_URL}/voice/status`);
  if (!res.ok) throw new Error('Failed to fetch voice status');
  return res.json();
}

export async function fetchRetellExport() {
  const res = await fetch(`${BASE_URL}/voice/export/retell`);
  if (!res.ok) throw new Error('Failed to export Retell schema');
  return res.json();
}

export async function fetchBolnaExport() {
  const res = await fetch(`${BASE_URL}/voice/export/bolna`);
  if (!res.ok) throw new Error('Failed to export Bolna schema');
  return res.json();
}
