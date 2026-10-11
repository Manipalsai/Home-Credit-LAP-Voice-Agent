# Home Credit LAP Voice Agent — Voice Platform Setup Guide

This guide provides step-by-step instructions for integrating the qualification engine with **Retell AI** (primary) and **Bolna**.

---

## 1. Why Retell AI as Primary Voice Target

- **Sub-600ms Conversational Latency:** Natural turn-taking with ambient noise cancellation and backchannel support ("uh-huh", "got it").
- **Indian English & Hindi Voices:** Native professional Indian voices (e.g. `11labs-Pooja`, `11labs-Adrian`) matching Home Credit India's customer demographic.
- **Dynamic Variables & Custom LLM:** Direct injection of `{{customer_name}}`, `{{company_name}}`, `{{current_date}}`, and grounded RAG knowledge.
- **Automated Recording & Transcripts:** Post-call webhooks dispatch audio recording URLs and timestamped diarized transcripts.

---

## 2. Retell AI Setup Instructions

### Step 1: Create Account & Get API Key
1. Go to [https://beta.retellai.com](https://beta.retellai.com) and sign in.
2. In the left sidebar, navigate to **API Keys**.
3. Click **Create New Key**, copy your secret key.
4. Add it to your local `.env` file (do not commit `.env`):
   ```env
   VOICE_PLATFORM=retell
   RETELL_API_KEY=key_xxxxxxxxxxxxxxxxxxxxxx
   ```

### Step 2: Export Platform Agent Schema
The project includes an automatic agent schema exporter:
```powershell
.venv\Scripts\python scripts\export_retell_agent.py
```
This generates `prompts/retell_agent_schema.json` with the complete system prompt, voice parameters, and dynamic variables.

Alternatively, create the agent via cURL / PowerShell:
```powershell
curl -X POST https://api.retellai.com/create-agent `
  -H "Authorization: Bearer $env:RETELL_API_KEY" `
  -H "Content-Type: application/json" `
  -d "@prompts/retell_agent_schema.json"
```
Copy the returned `agent_id` into your `.env`:
```env
RETELL_AGENT_ID=agent_xxxxxxxxxxxxxxxxxxxxxx
```

### Step 3: Configure Webhook & Cryptographic Signature
1. In the Retell Console, navigate to **Settings** > **Webhooks**.
2. Set Webhook URL to:
   ```
   https://<your-public-url>/api/voice/webhook/retell
   ```
   *(For local testing, use ngrok: `ngrok http 8000`)*
3. Copy the **Signing Secret** provided by Retell and set it in `.env`:
   ```env
   RETELL_WEBHOOK_SECRET=your_signing_secret_here
   ```
4. Incoming webhooks are automatically verified using constant-time HMAC-SHA256 signature verification in `backend/app/voice/webhook_verifier.py`.

### Step 4: Outbound / Inbound Test Call
1. In the Retell Console, go to **Phone Numbers**.
2. Buy or allocate a test telephone number.
3. Link the number to your **Home Credit India LAP Qualification Agent**.
4. To test, trigger an outbound call to your verified test mobile number via Retell's dashboard.
5. Speak naturally as a customer (e.g. Test an eligible flow or agricultural property exit).
6. Once the call terminates, view the recording audio URL and transcript in the Retell dashboard or in the local dashboard under the **Telephony Integration** tab.

---

## 3. Alternative: Bolna Platform Setup

If you prefer using **Bolna**:
1. Sign up at [https://bolna.dev](https://bolna.dev).
2. Obtain your Bolna API Key.
3. In your `.env`:
   ```env
   VOICE_PLATFORM=bolna
   BOLNA_API_KEY=your_bolna_api_key_here
   ```
4. Export Bolna configuration by calling `GET /api/voice/export/bolna` or through the dashboard.
5. Set Bolna Webhook to:
   ```
   https://<your-public-url>/api/voice/webhook/bolna
   ```

---

## 4. Real-Call Troubleshooting Guide

| Issue | Cause | Solution |
|---|---|---|
| Webhook returns `401 Unauthorized` | Signature mismatch | Ensure `RETELL_WEBHOOK_SECRET` matches the signing secret in Retell Console. |
| Agent interrupts too quickly | Interruption sensitivity too high | Lower `interruption_sensitivity` from `0.8` to `0.6` in the exported agent config. |
| Hindi numbers misheard | Audio codec distortion | Use `en-IN` or `hi-IN` language configuration in Retell agent settings. |
| Recording URL empty | Call in progress | Retell dispatches the recording URL on the `call_ended` / `call_analyzed` event. |
