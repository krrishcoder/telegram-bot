# Telegram Image Classification Bot

A Telegram bot that allows users to upload images and organize them by class/category on AWS S3.

## Features

- 📸 Upload images to AWS S3
- 🏷️ Organize images by user-defined classes
- 👤 User-specific folders
- 🤖 Simple command interface
- ☁️ Cloud deployment ready (Vercel/Render)

## Commands

- `/start` - Start the bot and get welcome message
- `/help` - Show help information
- `/class <n>` - Set the current class for image uploads
- `/status` - Check your current class setting

## Setup

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd telegram-bot
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file with your credentials**
   - Get your Telegram bot token from [@BotFather](https://t.me/BotFather)
   - Add your AWS credentials and S3 bucket name

4. **Make start script executable**
   ```bash
   chmod +x start.sh
   ```

5. **Run the bot**
   ```bash
   ./start.sh
   ```

### Manual Setup

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the bot**
   ```bash
   python app.py
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Yes |
| `AWS_ACCESS_KEY_ID` | AWS access key ID | Yes |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | Yes |
| `AWS_REGION` | AWS region (default: ap-south-1) | No |
| `S3_BUCKET_NAME` | S3 bucket name | Yes |

## Deployment

### Deploy to Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

3. **Set environment variables in Vercel dashboard**
   - Go to your project settings
   - Add all required environment variables

### Deploy to Render

1. **Connect your GitHub repository to Render**

2. **Create a new Web Service**
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

3. **Set environment variables in Render dashboard**

## File Structure

```
telegram-bot/
├── app.py              # Main bot application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (local)
├── .env.example       # Example environment file
├── .gitignore         # Git ignore rules
├── start.sh           # Development start script
├── vercel.json        # Vercel configuration
├── render.yaml        # Render configuration
└── README.md          # This file
```

## How It Works

1. **User sets a class**: `/class Shoes`
2. **User sends images**: Bot uploads them to S3 under `{user_id}/Shoes/`
3. **Organization**: Each user's images are organized by class in separate folders

## S3 Folder Structure

```
s3://your-bucket/
├── {user_id_1}/
│   ├── Shoes/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   └── Clothes/
│       └── image3.jpg
└── {user_id_2}/
    └── Electronics/
        └── image4.jpg
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues:
1. Check the logs for error messages
2. Verify all environment variables are set correctly
3. Ensure your AWS credentials have S3 permissions
4. Make sure your Telegram bot token is valid

## Security Notes

- Never commit your `.env` file to version control
- Use IAM roles with minimal required permissions for AWS
- Regularly rotate your API keys
- Monitor your S3 bucket for unexpected usage