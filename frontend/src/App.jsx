import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import CallSimulator from './components/CallSimulator';
import ChecklistStatus from './components/ChecklistStatus';
import StateInspector from './components/StateInspector';
import ScenarioRunner from './components/ScenarioRunner';
import TranscriptViewer from './components/TranscriptViewer';
import VoiceProviderPanel from './components/VoiceProviderPanel';

import {
  fetchHealth,
  startConversation,
  sendTurn,
  resetConversation,
  fetchScenarios,
  fetchVoiceStatus,
} from './api';

import { PhoneCall, PlaySquare, FileText, Radio, Layers } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('simulator'); // 'simulator' | 'scenarios' | 'transcript' | 'voice'
  const [health, setHealth] = useState(null);
  const [voiceStatus, setVoiceStatus] = useState(null);
  const [scenarios, setScenarios] = useState([]);

  // Call state
  const [sessionId, setSessionId] = useState(null);
  const [state, setState] = useState({});
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Initialize
  useEffect(() => {
    fetchHealth().then(setHealth).catch(console.error);
    fetchVoiceStatus().then(setVoiceStatus).catch(console.error);
    fetchScenarios().then(setScenarios).catch(console.error);

    initNewCall('Rajesh Sharma');
  }, []);

  const initNewCall = async (customerName = 'Rajesh Sharma') => {
    try {
      setLoading(true);
      const res = await startConversation(customerName);
      setSessionId(res.session_id);
      setState(res.state);
      setMessages([
        {
          id: 'msg_init',
          sender: 'agent',
          text: res.greeting,
          metadata: { stage: res.stage },
        },
      ]);
    } catch (err) {
      console.error('Failed to init call:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendUtterance = async (utterance) => {
    if (!sessionId || !utterance.trim()) return;

    // Optimistically add user message
    const userMsg = {
      id: `usr_${Date.now()}`,
      sender: 'user',
      text: utterance,
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      setLoading(true);
      const turnRes = await sendTurn(sessionId, utterance);
      setState(turnRes.state);

      const agentMsg = {
        id: `agt_${Date.now()}`,
        sender: 'agent',
        text: turnRes.agent_response,
        metadata: {
          stage: turnRes.current_stage,
          outcome: turnRes.outcome,
          next_question: turnRes.next_question,
        },
      };
      setMessages(prev => [...prev, agentMsg]);
    } catch (err) {
      alert(`Error processing speech: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!sessionId) return initNewCall();
    try {
      setLoading(true);
      const res = await resetConversation(sessionId, state.customer_name || 'Rajesh Sharma');
      setState(res.state);
      setMessages([
        {
          id: 'msg_reset',
          sender: 'agent',
          text: res.greeting,
          metadata: { stage: res.state.stage },
        },
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <Header health={health} voiceStatus={voiceStatus} />

      {/* Main Tabs Navigation */}
      <nav className="tabs-header">
        <button
          onClick={() => setActiveTab('simulator')}
          className={`tab-btn ${activeTab === 'simulator' ? 'active' : ''}`}
        >
          <PhoneCall size={16} /> Live Simulation & Qualification
        </button>
        <button
          onClick={() => setActiveTab('scenarios')}
          className={`tab-btn ${activeTab === 'scenarios' ? 'active' : ''}`}
        >
          <PlaySquare size={16} /> Predefined Test Scenarios ({scenarios.length})
        </button>
        <button
          onClick={() => setActiveTab('transcript')}
          className={`tab-btn ${activeTab === 'transcript' ? 'active' : ''}`}
        >
          <FileText size={16} /> Call Transcript & Export
        </button>
        <button
          onClick={() => setActiveTab('voice')}
          className={`tab-btn ${activeTab === 'voice' ? 'active' : ''}`}
        >
          <Radio size={16} /> Telephony Integration (Retell/Bolna)
        </button>
      </nav>

      {/* Tab 1: Simulator & Qualification */}
      {activeTab === 'simulator' && (
        <div className="dashboard-grid">
          {/* Left Column: Interactive Voice Simulator */}
          <div>
            <CallSimulator
              messages={messages}
              onSend={handleSendUtterance}
              onReset={handleReset}
              loading={loading}
              isTerminal={state.is_terminal}
              currentPrompt={state.current_prompt}
            />
          </div>

          {/* Right Column: 7-Point Checklist & State Inspector */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <ChecklistStatus checklist={state.checklist} state={state} />
            <StateInspector state={state} />
          </div>
        </div>
      )}

      {/* Tab 2: Predefined Scenarios Runner */}
      {activeTab === 'scenarios' && (
        <ScenarioRunner scenarios={scenarios} />
      )}

      {/* Tab 3: Transcript Viewer */}
      {activeTab === 'transcript' && (
        <TranscriptViewer messages={messages} state={state} />
      )}

      {/* Tab 4: Voice Platform Panel */}
      {activeTab === 'voice' && (
        <VoiceProviderPanel voiceStatus={voiceStatus} />
      )}
    </div>
  );
}
