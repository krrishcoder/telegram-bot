import os
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# Initialize S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# In-memory storage for user classes (consider using a database for production)
user_class_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.message.from_user
    user_id = user.id
    username = user.username
    print(f"User ID: {user_id}, Username: {username}")
    
    welcome_message = (
        f"Hello {username or user.first_name}! 👋\n\n"
        "I'm your image classification bot. Here's how to use me:\n"
        "1. Use /class <name> to set a class\n"
        "2. Send me images to upload them to that class\n"
        "3. Use /help for more information"
    )
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler"""
    help_text = (
        "🤖 **Bot Commands:**\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/class <name> - Set the current class for image uploads\n"
        "/status - Check your current class setting\n\n"
        "**How to use:**\n"
        "1. First, set a class with `/class MyClassName`\n"
        "2. Then send me images - they'll be uploaded to S3 under that class\n"
        "3. All images are organized by user ID and class name"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set class command handler"""
    user_id = update.message.from_user.id
    class_name = ' '.join(context.args)
    
    if class_name:
        user_class_map[user_id] = class_name
        await update.message.reply_text(
            f"✅ Class set to: **{class_name}**\n"
            f"Now send me images to upload them to this class!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Please provide a class name.\n"
            "Example: `/class Shoes`",
            parse_mode='Markdown'
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command handler"""
    user_id = update.message.from_user.id
    class_name = user_class_map.get(user_id)
    
    if class_name:
        await update.message.reply_text(
            f"📊 **Current Status:**\n"
            f"Active class: **{class_name}**\n"
            f"Ready to receive images! 📸",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "📊 **Current Status:**\n"
            "No class set. Use `/class <name>` to set one first.",
            parse_mode='Markdown'
        )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image uploads"""
    user_id = update.message.from_user.id
    class_name = user_class_map.get(user_id)

    if not class_name:
        await update.message.reply_text(
            "❌ Please first set a class using `/class <name>`\n"
            "Example: `/class Shoes`",
            parse_mode='Markdown'
        )
        return

    try:
        # Get the largest photo (best quality)
        photo_file = await update.message.photo[-1].get_file()
        file_name = f"{photo_file.file_id}.jpg"
        s3_key = f"{user_id}/{class_name}/{file_name}"

        # Send processing message
        processing_msg = await update.message.reply_text("📤 Uploading image...")

        # Download temporarily
        await photo_file.download_to_drive(file_name)

        # Upload to S3
        s3.upload_file(file_name, S3_BUCKET_NAME, s3_key)

        # Clean up local file
        os.remove(file_name)

        # Update success message
        await processing_msg.edit_text(
            f"✅ **Image uploaded successfully!**\n"
            f"📁 Path: `{s3_key}`\n"
            f"🏷️ Class: **{class_name}**",
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"Error uploading image: {e}")
        await update.message.reply_text(
            f"❌ Error uploading image: {str(e)}\n"
            "Please try again or contact support."
        )

async def handle_other_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-command, non-image messages"""
    await update.message.reply_text(
        "🤔 I can only process images and commands.\n"
        "Send /help to see available commands."
    )

def create_app():
    """Create and configure the bot application"""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("class", set_class))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other_messages))

    return app

async def main():
    """Main function to run the bot"""
    print("🚀 Starting Telegram Bot...")
    
    # Validate environment variables
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'S3_BUCKET_NAME'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return
    
    try:
        app = create_app()
        print("✅ Bot is running and ready to receive messages...")
        await app.run_polling()
    except Exception as e:
        print(f"❌ Error running bot: {e}")

if __name__ == "__main__":
    # Apply nest_asyncio for environments that need it
    nest_asyncio.apply()
    
    # Run the bot
    asyncio.run(main())