# EconoAnalyst

EconoAnalyst is a Telegram-based economics research assistant that combines a Telegram bot, FastAPI backend, OpenClaw skill, and automated dashboard generation.

The current prototype is mainly tested for Malaysia unemployment and labour-force analysis.

## Main Features

* Accepts economics research tasks through Telegram
* Generates a short research summary
* Produces an interactive HTML dashboard
* Generates a screenshot preview of the dashboard
* Uses OpenClaw for local AI-assisted task processing
* Uses FastAPI as the backend service

---

# Setup Guide

## 1. Clone the Repository

```bash
git clone https://github.com/KirrtanaaNallathamby/EconoAnalyst.git
cd EconoAnalyst
```

---

## 2. Create a Virtual Environment

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

After activation, the terminal should display `(venv)`.

---

## 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Install the Chromium browser required by Playwright:

```bash
python -m playwright install chromium
```

---

## 4. Create the Environment File

Create a file named `.env` in the project root folder.

Add the following configuration:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
BACKEND_URL=http://127.0.0.1:8000
OPENCLAW_PATH=your_openclaw_executable_path
```

### Windows OpenClaw Path Example

```env
OPENCLAW_PATH=C:\Users\YOUR_USERNAME\AppData\Roaming\npm\openclaw.ps1
```

### macOS OpenClaw Path

Find the OpenClaw path by running:

```bash
which openclaw
```

The result may look similar to:

```text
/opt/homebrew/bin/openclaw
```

or:

```text
/usr/local/bin/openclaw
```

Add the returned path to `.env`:

```env
OPENCLAW_PATH=/opt/homebrew/bin/openclaw
```

Do not upload the `.env` file to GitHub.

---

## 5. Install and Configure OpenClaw

OpenClaw requires Node.js and npm.

Install OpenClaw globally:

```bash
npm install -g openclaw
```

Start the initial configuration:

```bash
openclaw onboard
```

During the setup:

* Choose **QuickStart**
* Select the model provider configured for the project
* Enter the required API key when requested
* Skip unrelated API keys
* Enable local terminal mode

---

## 6. Install the EcoResearch OpenClaw Skill

The skill folder is located inside the repository:

```text
openclaw_skill/ecoresearch-bot
```

It must be copied into the OpenClaw workspace.

### macOS / Linux

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -R openclaw_skill/ecoresearch-bot ~/.openclaw/workspace/skills/
```

The final location should be:

```text
~/.openclaw/workspace/skills/ecoresearch-bot
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force "$HOME\.openclaw\workspace\skills"
Copy-Item -Recurse -Force "openclaw_skill\ecoresearch-bot" "$HOME\.openclaw\workspace\skills\"
```

The final location should be:

```text
C:\Users\YOUR_USERNAME\.openclaw\workspace\skills\ecoresearch-bot
```

The skill folder should contain:

```text
ecoresearch-bot/
├── SKILL.md
├── scripts/
│   └── client.py
└── references/
    └── api-contract.md
```

---

# Running the System

The system requires three terminals to run at the same time.

## Terminal 1: Start OpenClaw

```bash
openclaw tui
```

Keep this terminal running.

---

## Terminal 2: Start the FastAPI Backend

Open a new terminal and enter the project folder:

```bash
cd EconoAnalyst
```

Activate the virtual environment.

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```powershell
venv\Scripts\activate
```

Start the backend:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

A successful startup should show:

```text
Uvicorn running on http://127.0.0.1:8000
```

Keep this terminal running.

---

## Terminal 3: Start the Telegram Bot

Open another terminal and enter the project folder:

```bash
cd EconoAnalyst
```

Activate the virtual environment.

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```powershell
venv\Scripts\activate
```

Start the bot:

```bash
python run.py
```

A successful startup should show:

```text
EcoResearch Telegram Bot is running...
```

Keep this terminal running.

---

# Using the Telegram Bot

Open the Telegram bot and send a research task.

Example:

```text
Analyse Malaysia unemployment trend
```

Then upload the required Markdown instruction file.

The bot should return:

* A short research summary
* An HTML dashboard file
* A screenshot preview of the dashboard

All three terminals must remain running while using the bot.

---

# Project Structure

```text
EconoAnalyst/
├── backend/
├── bot/
├── brain/
├── dashboard/
├── data_engine/
├── examples/
├── openclaw_skill/
│   └── ecoresearch-bot/
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

---

# Important Notes

* Never commit the `.env` file to GitHub.
* Never upload Telegram bot tokens or API keys.
* Each teammate should use their own Telegram bot token, or share the demo token privately.
* OpenClaw must be installed and running locally.
* The FastAPI backend must run on port `8000`.
* The Telegram bot, backend, and OpenClaw must run simultaneously.
* The current prototype is mainly tested for Malaysia unemployment and labour-force analysis.
* Dashboard screenshot generation requires Playwright Chromium.

---

# Troubleshooting

## `openclaw: command not found`

Reinstall OpenClaw:

```bash
npm install -g openclaw
```

Then check its location:

```bash
which openclaw
```

On Windows:

```powershell
where openclaw
```

## Telegram Bot Does Not Respond

Check that:

* `TELEGRAM_BOT_TOKEN` is correct
* The FastAPI backend is running
* OpenClaw TUI is running
* `BACKEND_URL` is set to `http://127.0.0.1:8000`
* All three terminals remain open

## Dashboard Screenshot Is Missing

Install Chromium again:

```bash
python -m playwright install chromium
```

Then restart the backend and Telegram bot.

## Port 8000 Is Already in Use

Stop the existing backend process with:

```text
Control + C
```

Then restart:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```
