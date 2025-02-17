import logging
import os
import asyncio
import re
from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import instaloader
from dotenv import dotenv_values

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram bot token (place the token you received from BotFather here)
TOKEN = dotenv_values('.env.secret')['BOT_TOKEN']


# Function to check if the Instagram link is valid
def is_valid_instagram_url(url):
    pattern = r"^https?://(www\.)?instagram\.com/(p|reel|stories)/[a-zA-Z0-9_-]+(/)?(\?.*)?$"
    return re.match(pattern, url) is not None


# Function to download video (without downloading images)
async def download_video(download_path, update: Update, context: CallbackContext) -> None:
    files = os.listdir(download_path)
    for file in files:
        file_path = os.path.join(download_path, file)
        if file.endswith(".mp4"):
            with open(file_path, "rb") as video:
                await update.message.reply_video(video=InputFile(video), caption="Video downloaded!")


# Function to download story
async def download_story(url, update: Update, context: CallbackContext) -> None:
    L = instaloader.Instaloader()
    try:
        # Extract shortcode from story link
        shortcode = url.split("/")[-2]
        story = instaloader.StoryItem.from_shortcode(L.context, shortcode)

        # Download story
        download_path = f"story_{story.owner_username}_{story.shortcode}"
        L.download_storyitem(story, target=download_path)

        await update.message.reply_text("Please wait... 🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%")

        # Send video to user
        await download_video(download_path, update, context)

        # Delete progress bar messages
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=wait_message.message_id)

    except Exception as e:
        logger.error(f"Error downloading story: {e}")
        await update.message.reply_text(f"Error downloading story: {e}")


# Function to download reels
async def download_reel(url, update: Update, context: CallbackContext) -> None:
    L = instaloader.Instaloader()
    try:
        # Send "Please wait" message with progress bar
        wait_message = await update.message.reply_text("Please wait... 🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%")

        # Extract shortcode from reel link
        shortcode = url.split("/")[-2]
        reel = instaloader.Post.from_shortcode(L.context, shortcode)

        # Download reel
        download_path = f"reel_{reel.owner_username}_{reel.shortcode}"
        L.download_post(reel, target=download_path)

        # Display progress bar in Telegram
        for i in range(1, 11):
            await asyncio.sleep(1)  # 1 second delay
            progress = "🟩" * i + "⬜" * (10 - i)  # Progress bar
            await wait_message.edit_text(f"Please wait... {progress} {i * 10}%")

        # Send video to user
        await download_video(download_path, update, context)

        # Delete progress bar messages
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=wait_message.message_id)

    except Exception as e:
        logger.error(f"Error downloading reel: {e}")
        await update.message.reply_text(f"Problem downloading reel. Please check the link.\nError: {e}")


# Function to download from Instagram and send file
async def download_instagram(update: Update, context: CallbackContext) -> None:
    url = update.message.text

    # Check if the link is valid
    if not is_valid_instagram_url(url):
        return  # If the link is not valid, do nothing

    L = instaloader.Instaloader()

    try:
        # Send "Please wait" message with progress bar
        wait_message = await update.message.reply_text("Please wait... 🟩⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%")

        # Detect content type (post, story, or reel)
        if "/p/" in url:  # Post
            shortcode = url.split("/")[-2]
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            download_path = f"post_{post.owner_username}_{post.shortcode}"
            L.download_post(post, target=download_path)

            # Display progress bar in Telegram
            for i in range(1, 11):
                await asyncio.sleep(1)  # 1 second delay
                progress = "🟩" * i + "⬜" * (10 - i)  # Progress bar
                await wait_message.edit_text(f"Please wait... {progress} {i * 10}%")

            # Send video to user
            await download_video(download_path, update, context)

        elif "/stories/" in url:  # Story
            await download_story(url, update, context)

        elif "/reel/" in url:  # Reel
            await download_reel(url, update, context)

        # Delete progress bar messages
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=wait_message.message_id)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)  # Display full error
        await update.message.reply_text(f"Problem downloading content. Please check the link.\nError: {e}")


# Main function
def main() -> None:
    # Create Application with increased allowed times
    application = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()

    # Commands
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))

    # Start the bot
    application.run_polling()


if __name__ == '__main__':
    main()
