████████╗███████╗██╗     ███████╗ ██████╗ ██████╗  █████╗ ██████╗ 
╚══██╔══╝██╔════╝██║     ██╔════╝██╔════╝ ██╔══██╗██╔══██╗██╔══██╗
   ██║   █████╗  ██║     █████╗  ██║  ███╗██████╔╝███████║██████╔╝
   ██║   ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██╔══██║██╔══██╗
   ██║   ███████╗███████╗███████╗╚██████╔╝██║  ██║██║  ██║██████╔╝
   ╚═╝   ╚══════╝╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 

# Telegrab - A phone number checker for Telegram

A Python tool for investigative journalists to check if phone numbers are registered on Telegram. This tool provides a user-friendly terminal interface but does require some technical knowledge to install. This tool builds on the telegram-phone-number-checker built by Bellingcat. 

## Prerequisites

- Python 3.7 or higher
- A Telegram account
- Telegram API credentials (API ID and API Hash)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/telegrab.git
cd telegrab
```

2. Create and activate a virtual environment:

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Get your Telegram API credentials:
   - Visit [https://my.telegram.org/auth](https://my.telegram.org/auth)
   - Log in with your phone number
   - Go to 'API development tools'
   - Fill in your application details:
     - App title: Can be anything (e.g., "My Checker")
     - Short name: Can be anything (e.g., "mychecker")
     - URL: Can be blank
     - Platform: Choose "Desktop"
     - Description: Can be brief (e.g., "Personal usage")
   - Accept the terms of service
   - Copy your API ID (a number) and API Hash (a long string)
   - Keep these credentials secure and never share them

5. Create a `.env` file in the project directory with your credentials:
```plaintext
API_ID=your_api_id
API_KEY=your_api_hash
YOUR_PHONE=your_phone_number  # Format: 1234567890 (remove the +)
```

## Usage

When you first run the tool, Telegram will send a verification code to your Telegram account. You'll need to enter this code in the terminal to authenticate. This is a one-time process for each session.

You can run Telegrab in several ways:

1. Basic interactive mode (will prompt for numbers):
```bash
python telegrab.py
```

2. Check specific numbers directly:
```bash
python telegrab.py -n "447755570626,447755570627"
```

3. Check numbers from a file:
```bash
python telegrab.py -f numbers.txt
```
Your numbers.txt file should contain one phone number per line:
```plaintext
447755570626
447755570627
447755570628
```

4. Run without colors (useful for logging):
```bash
python telegrab.py --no-color
```

5. Get help about available options:
```bash
python telegrab.py -h
```

**Important Notes:**
- Phone numbers should be in international format WITHOUT the '+' symbol (e.g., if your number is +44-775-557-0626, enter it as 447755570626)
- Make sure your `.env` file is in the same directory
- Ensure you're in your virtual environment before running
- Rate limiting may occur if checking many numbers quickly

## Contributing

[Contributing guidelines to be added]

## License

See LICENSE.md 