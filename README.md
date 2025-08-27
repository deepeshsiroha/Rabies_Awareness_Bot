Rabies Information Telegram Bot
This is a rule-based, bilingual (English and Hindi) Telegram chatbot designed to provide critical first-aid information after a potential rabies exposure and answer frequently asked questions about the disease.

Features
Bilingual Support: The entire user journey is available in both English and Hindi.

Menu-Driven Interface: Relies on interactive buttons to guide the user, minimizing the need for text input.

Primary Path:

General Information Path: For users seeking general knowledge about rabies.

Clear & Actionable Information: Content is simple, medically accurate, and easy to understand.

Medical Disclaimer: A clear disclaimer is shown to the user at the start of every interaction.

Setup and Installation
Follow these steps to get the bot running on your local machine.

Prerequisites

Python 3.8+

A Telegram Bot Token. You can get one by talking to @BotFather on Telegram.

Installation Steps

Clone the repository:

git clone <your-repository-url>
cd rabies-telegram-bot

Create and activate a virtual environment:

Windows:

python -m venv venv
.\venv\Scripts\activate

macOS/Linux:

python3 -m venv venv
source venv/bin/activate

Install the required dependencies:

pip install -r requirements.txt

Add your Bot Token:
Open the rabies_bot.py file and replace the placeholder text YOUR_TELEGRAM_BOT_TOKEN with your actual Telegram bot token.

# in rabies_bot.py, around line 240
application = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

Running the Bot
Once the setup is complete, you can start the bot with the following command:

python rabies_bot.py

You should see the message "Bot is running..." in your terminal. You can now interact with your bot on Telegram.

Project Structure
.
├── .gitignore          # Specifies files for Git to ignore
├── README.md           # This instruction file
├── content.json        # Contains all English and Hindi text for the bot
├── rabies_bot.py       # The main Python script with all the bot's logic
└── requirements.txt    # Lists the Python packages required for the project
