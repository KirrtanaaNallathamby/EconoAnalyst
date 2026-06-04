ECONOANALYST SETUP GUIDE

1. Clone the repository

git clone <repo-url>
cd EconoAnanlyst

2. Create virtual environment

python -m venv venv
venv\Scripts\activate

3. Install Python dependencies

pip install -r requirements.txt

4. Create .env file

Create a file named .env in the project root.

Add:

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
BACKEND_URL=http://127.0.0.1:8000
OPENCLAW_PATH=C:\Users\ishwa\AppData\Roaming\npm\openclaw.ps1

5. Install OpenClaw

npm install -g openclaw
openclaw onboard

During setup:

* Choose QuickStart
* Choose OpenAI provider
* Skip unrelated API keys
* Enable local terminal mode

6. Add EcoResearch OpenClaw skill

Copy the ecoresearch-bot skill folder into:

C:\Users<YOUR_USERNAME>.openclaw\workspace\skills\ecoresearch-bot

The folder should contain:

SKILL.md
scripts/client.py
references/api-contract.md

7. Start OpenClaw

openclaw tui

Keep this terminal running.

8. Start FastAPI backend

Open a new terminal in the project folder:

venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000

9. Start Telegram bot

Open another terminal in the project folder:

venv\Scripts\activate
python run.py

10. Use the Telegram bot

Send a task first.

Example:
Analyse Malaysia unemployment trend

Then upload the Markdown instruction file.

The bot should return:

* a short research summary
* an HTML dashboard file

IMPORTANT NOTES

* Do not push .env to GitHub.
* Each teammate needs their own Telegram bot token or must use the shared demo token privately.
* OpenClaw must be installed and running locally.
* Backend must be running on port 8000.
* The current prototype is tested mainly for Malaysia unemployment / labour force analysis.
