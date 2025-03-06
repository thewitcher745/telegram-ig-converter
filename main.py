import os
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import instaloader
from dotenv import dotenv_values

# Configure logging with more detailed information
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Instagram URL pattern
INSTAGRAM_URL_PATTERN = r'https?://(?:www\.)?instagram\.com/(?:p|reel)/([^/?]+)'

# Configure download directory
DOWNLOAD_DIR = 'instagram_downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        'Hi! I am an Instagram Downloader Bot. Add me to a group, and I will download any Instagram posts or reels shared there.'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'Just share an Instagram post or reel link in a group where I am a member, and I will download it for you!'
    )


async def debug_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Debug handler to log message details."""
    if update.message and update.effective_chat:
        chat_type = update.effective_chat.type
        chat_id = update.effective_chat.id
        message_text = update.message.text if update.message.text else "No text"

        logger.info(f"DEBUG - Message received: '{message_text}' in chat type: {chat_type}, chat ID: {chat_id}")

        # Process the message for Instagram links
        await process_instagram_links(update, context)


async def process_instagram_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process message for Instagram links."""
    if not update.message or not update.message.text:
        return

    # Find Instagram URLs in the message
    instagram_urls = re.findall(INSTAGRAM_URL_PATTERN, update.message.text)

    if not instagram_urls:
        return

    chat_id = update.effective_chat.id

    for shortcode in instagram_urls:
        # Notify that download has started
        status_message = await update.message.reply_text(f"Downloading Instagram content with ID: {shortcode}...")

        # Download in a non-blocking way
        await download_and_send_instagram_content(shortcode, chat_id, status_message, context)


async def download_and_send_instagram_content(shortcode, chat_id, status_message, context):
    """Download and send Instagram content in a non-blocking way."""
    try:
        # Get full URL
        url = f"https://www.instagram.com/p/{shortcode}/"

        # Download in a separate thread to not block the bot
        file_path = await asyncio.to_thread(download_from_instagram, url)

        if not file_path:
            await status_message.edit_text(f"Failed to download content with ID: {shortcode}")
            return

        # Send the file
        if file_path.endswith('.mp4'):
            await context.bot.send_video(
                chat_id=chat_id,
                video=open(file_path, 'rb'),
                caption=f"Downloaded from Instagram (ID: {shortcode})"
            )
        else:
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=open(file_path, 'rb'),
                caption=f"Downloaded from Instagram (ID: {shortcode})"
            )

        await status_message.delete()

        # Clean up - delete the file after sending
        os.remove(file_path)

    except Exception as e:
        logger.error(f"Error processing Instagram content: {e}")
        await status_message.edit_text(f"Error downloading content: {str(e)[:100]}...")


def download_from_instagram(url):
    """Download content from Instagram using instaloader."""
    try:
        # Create a unique subdirectory for this download
        shortcode_match = re.search(r'instagram.com/(?:p|reel)/([^/]+)', url)
        if not shortcode_match:
            logger.error("Could not extract post shortcode from URL")
            return None

        shortcode = shortcode_match.group(1)
        # Remove any query parameters
        shortcode = shortcode.split('?')[0]

        download_path = os.path.join(DOWNLOAD_DIR, shortcode)
        os.makedirs(download_path, exist_ok=True)

        # Create an instaloader instance
        L = instaloader.Instaloader(
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=download_path
        )

        # Get the post from the shortcode
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Download the post
        L.download_post(post, target=shortcode)

        # Find the media file (video or image)
        if post.is_video:
            media_files = [f for f in os.listdir(download_path) if f.endswith('.mp4')]
        else:
            media_files = [f for f in os.listdir(download_path) if f.endswith('.jpg')]

        if not media_files:
            logger.error("No media file found after download")
            return None

        return os.path.join(download_path, media_files[0])

    except instaloader.exceptions.InstaloaderException as e:
        logger.error(f"Instagram error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error downloading content: {e}")
        return None


def main() -> None:
    """Start the bot."""
    # Get token from environment variable for security
    TOKEN = dotenv_values(".env.secret")["BOT_TOKEN"]
    if not TOKEN:
        logger.error("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")
        return

    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Handle ALL updates with the debug handler to diagnose the issue
    # This ensures we capture and process every message regardless of type or filter
    application.add_handler(MessageHandler(filters.ALL, debug_message))

    # Log startup information
    logger.info("Bot started")

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()