# 📱 Telegrab - A Telegram Phone Number Checker

A Python OSINT tool for investigative journalists to check if phone numbers are registered on Telegram. This tool provides a user-friendly terminal interface with colored output and multiple input methods.

## 🖼️ Screenshots

![Telegrab CLI Interface](screenshots/telegrab_cli.png)

*The Telegrab command-line interface showing search results*

## 🔧 Prerequisites

- Python 3.7 or higher
- A Telegram account
- Telegram API credentials (API ID and API Hash)

## ⚙️ Setup

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

## 🚀 Usage

When you first run the tool, Telegram will send a verification code to your Telegram account. You'll need to enter this code in the terminal to authenticate. This is a one-time process for each session.

### Single Number Search
```bash
python telegrab.py
```
When prompted, enter a single phone number. The tool automatically removes spaces and special characters, so these formats all work:
- 447755570626
- +44 7755 570626
- +44-7755-570626

### Batch Searching

You can check multiple numbers at once in two ways:

1. **Comma-separated input:**
```bash
python telegrab.py -n "447755570626,447755570627,447755570628"
```
Or when prompted, enter multiple numbers separated by commas:
```
Enter phone number (or comma-separated numbers): +44 7755 570626, +44 7755 570627
```

2. **Text file input:**
Create a file (e.g., `numbers.txt`) with one number per line:
```plaintext
+44 7755 570626
+44 7755 570627
447755570628
```
Then run:
```bash
python telegrab.py -f numbers.txt
```

![Telegrab Batch Search](screenshots/telegrab_batch.png)

*The Telegrab interface showing batch search results using Russian numbers from breach data*

### Additional Options

1. Run without colors (useful for logging):
```bash
python telegrab.py --no-color
```

2. Enable debug mode (shows detailed API responses):
```bash
python telegrab.py --debug
```

3. Get help about available options:
```bash
python telegrab.py -h
```

## ✨ Features

- Check if phone numbers are registered on Telegram
- Detect whether accounts are bots or human users
- View user's last seen status
- See user bio information when available
- Debug mode for detailed API responses
- Rate limiting protection with exponential backoff
- Colored terminal output
- Multiple input methods (interactive, file, command line)

**⚠️ Important Notes:**
- Phone numbers should be in international format WITHOUT the '+' symbol (e.g., if your number is +44-775-557-0626, enter it as 447755570626)
- Make sure your `.env` file is in the same directory
- Ensure you're in your virtual environment before running
- Rate limiting may occur if checking many numbers quickly

## 🤝 Contributing

I plan to add more Telegram python tools to Telegrab in the future. Feel free to reach out for suggestions or contributions.

## 📄 License

See LICENSE.md 