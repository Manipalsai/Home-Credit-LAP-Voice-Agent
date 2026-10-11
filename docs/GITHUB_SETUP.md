# Home Credit LAP Voice Agent — GitHub Setup & Delivery Guide

This document explains how to safely authenticate, create or link a remote repository, and publish the project to GitHub without leaking tokens or private credentials.

---

## 1. Security First — No Token Leakage

> **CRITICAL SECURITY RULE:** Never paste a GitHub Personal Access Token (PAT), password, or SSH private key into AI chat prompts, source code files, or committed artifacts.

The project `.gitignore` automatically excludes:
- `.env` and `.env.*`
- Virtual environments (`.venv/`, `env/`)
- Audio recordings (`*.wav`, `*.mp3`)
- Node modules and build caches

---

## 2. Windows GitHub Authentication Workflow

### Option A: Using GitHub CLI (`gh`) [Recommended]
If GitHub CLI is installed:
1. Run in PowerShell:
   ```powershell
   gh auth login
   ```
2. Select **GitHub.com** -> **HTTPS** -> Authenticate with your browser.
3. Once authenticated, verify:
   ```powershell
   gh auth status
   ```
4. Create a new repository:
   ```powershell
   gh repo create home-credit-lap-voice-agent --public --source=. --remote=origin --push
   ```

### Option B: Using Git Credential Manager (Native Git for Windows)
If `gh` is not installed:
1. Initialize commit locally:
   ```powershell
   git add .
   git commit -m "feat: complete Home Credit LAP AI voice agent qualification engine"
   ```
2. Create an empty repository on [GitHub](https://github.com/new).
3. Link your remote:
   ```powershell
   git remote add origin https://github.com/<your-username>/home-credit-lap-voice-agent.git
   git branch -M main
   git push -u origin main
   ```
4. Git Credential Manager will open a secure browser login window. Sign in there directly.

---

## 3. Post-Push Verification Checklist

After pushing:
- [ ] Verify repository visibility and remote URL.
- [ ] Confirm `README.md`, `prompts/`, `backend/`, and `frontend/` are present on GitHub.
- [ ] Confirm `.env` is NOT present on GitHub.
- [ ] Verify GitHub Actions or tests can run cleanly.
