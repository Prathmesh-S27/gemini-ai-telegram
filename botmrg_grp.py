# This scripts contains use cases for simple bots
# import requirements 
import os
import asyncio
import PIL.Image
import google.generativeai as genai
from pathlib import Path
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from ad_config import ad_config, should_show_ad

generation_config_cook = {
  "temperature": 0.35,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 1024,
}

# API KEYS
# Gemini Ai API KEY
API_KEY= os.environ['API_KEY']
# Telegram Auth API ID
API_ID = os.environ['API_ID']
# Telegram Auth API HASH
API_HASH = os.environ['API_HASH']
# Telegram Bot API TOKEN generated from @botfather
BOT_TOKEN = os.environ['BOT_TOKEN']

genai.configure(api_key=API_KEY)

# Setup models
model = genai.GenerativeModel("gemini-1.5-flash")
model_text = genai.GenerativeModel("gemini-1.5-flash")
model_cook = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=generation_config_cook)
# configure pyrogram client 
app = Client("gemini_ai", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("askai") & filters.group)
async def say(_, message: Message):
    try:
        i = await message.reply_text("<code>Please Wait...</code>")


        if len(message.command) > 1:
         prompt = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
         prompt = message.reply_to_message.text
        else:
         await i.delete()
         await message.reply_text(
            f"<b>Usage: </b><code>/askai [prompt/reply to message]</code>"
        )
         return

        chat = model_text.start_chat()
        response = chat.send_message(prompt)
        await i.delete()

        response_text = f"**Answer:** {response.text}"
        
        # Add ad if needed
        if should_show_ad():
            ad_message = ad_config.get_ad_message()
            if ad_message:
                response_text += f"\n\n{ad_message}"

        await message.reply_text(response_text, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await i.delete()
        await message.reply_text(f"An error occurred: {str(e)}")

@app.on_message(filters.text & filters.private)
async def say(_, message: Message):
    try:
        await message.reply_chat_action(enums.ChatAction.TYPING)
        prompt = message.text
        chat = model_text.start_chat()
        response = chat.send_message(prompt)

        response_text = f"{response.text}"
        
        # Add ad if needed
        if should_show_ad():
            ad_message = ad_config.get_ad_message()
            if ad_message:
                response_text += f"\n\n{ad_message}"

        await message.reply_text(response_text, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@app.on_message(filters.command("getai") & filters.group)
async def say(_, message: Message):
    try:
        i = await message.reply_text("<code>Please Wait...</code>")

        base_img = await message.reply_to_message.download()

        img = PIL.Image.open(base_img)

        response = model.generate_content(img)
        await i.delete()

        await message.reply_text(
            f"**Detail Of Image:** {response.parts[0].text}", parse_mode=enums.ParseMode.MARKDOWN
        )
        os.remove(base_img)
    except Exception as e:
        await i.delete()
        await message.reply_text(str(e))

@app.on_message(filters.command("aicook") & filters.group)
async def say(_, message: Message):
    try:
        i = await message.reply_text("<code>Cooking...</code>")

        base_img = await message.reply_to_message.download()

        img = PIL.Image.open(base_img)
        cook_img = [
        "Accurately identify the baked good in the image and provide an appropriate and recipe consistent with your analysis. ",
        img,
        ]

        response = model_cook.generate_content(cook_img)
        await i.delete()

        await message.reply_text(
            f"{response.text}", parse_mode=enums.ParseMode.MARKDOWN
        )
        os.remove(base_img)
    except Exception as e:
        await i.delete()
        await message.reply_text(str(e))

@app.on_message(filters.command("aiseller") & filters.group)
async def say(_, message: Message):
    try:
        i = await message.reply_text("<code>Generating...</code>")
        if len(message.command) > 1:
         taud = message.text.split(maxsplit=1)[1]
        else:
         await i.delete()
         await message.reply_text(
            f"<b>Usage: </b><code>/aiseller [target audience] [reply to product image]</code>"
        )
         return

        base_img = await message.reply_to_message.download()

        img = PIL.Image.open(base_img)
        sell_img = [
        "Given an image of a product and its target audience, write an engaging marketing description",
        "Product Image: ",
        img,
        "Target Audience: ",
        taud
        ]

        response = model.generate_content(sell_img)
        await i.delete()

        await message.reply_text(
            f"{response.text}", parse_mode=enums.ParseMode.MARKDOWN
        )
        os.remove(base_img)
    except Exception as e:
        await i.delete()
        await message.reply_text(f"<b>Usage: </b><code>/aiseller [target audience] [reply to product image]</code>")

@app.on_message(filters.command("webapp") & (filters.private | filters.group))
async def webapp_command(_, message: Message):
    """Handle /webapp command to show web app"""
    try:
        # Get the web app URL from ad_config
        web_app_url = ad_config.web_app_url or ad_config.suggest_web_app_url()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "🌐 Open Web App", 
                web_app=WebAppInfo(url=web_app_url)
            )],
            [InlineKeyboardButton(
                "📱 Bot Link", 
                url=ad_config.bot_url
            )] if ad_config.bot_url else []
        ])
        
        webapp_message = f"""
🤖 **Gemini AI Web App**

Experience our AI assistant in a beautiful web interface!

✨ **Features:**
- Interactive chat interface
- Telegram Web App integration  
- Optimized for mobile
- Ad-supported free service

Click the button below to launch the web app:
"""
        
        await message.reply_text(
            webapp_message, 
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await message.reply_text(f"Error opening web app: {str(e)}")

# Add configuration commands from ad_config
@app.on_message(filters.command("config") & filters.private)
async def config_command(client, message: Message):
    from ad_config import handle_config_command
    await handle_config_command(client, message)

@app.on_message(filters.command("network") & filters.private)  
async def network_command(client, message: Message):
    from ad_config import handle_network_info
    await handle_network_info(client, message)

@app.on_message(filters.command("autoconfig") & filters.private)
async def autoconfig_command(client, message: Message):
    from ad_config import handle_auto_config
    await handle_auto_config(client, message)

# Handle config input
@app.on_message(filters.text & filters.private)
async def handle_private_message(client, message: Message):
    from ad_config import handle_config_input
    
    # Check if user is in config session first
    if await handle_config_input(client, message):
        return  # Message was handled as config input
    
    # Otherwise, process as normal AI chat
    try:
        await message.reply_chat_action(enums.ChatAction.TYPING)
        prompt = message.text
        chat = model_text.start_chat()
        response = chat.send_message(prompt)

        response_text = f"{response.text}"
        
        # Add ad if needed
        if should_show_ad():
            ad_message = ad_config.get_ad_message()
            if ad_message:
                response_text += f"\n\n{ad_message}"

        await message.reply_text(response_text, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# Run the bot
if __name__ == "__main__":
    app.run()
