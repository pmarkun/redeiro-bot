import os
import discord
import openai

from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up GPT-4 API credentials
openai.api_key = os.getenv("GPT4_API_KEY")
default_persona = os.getenv("PERSONA")
current_persona = default_persona


# Define intents for the bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Initialize Discord bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize bot_memory (you can use a dictionary, database, or file storage)
bot_memory = []

async def fetch_chat_history(channel, n):
    messages = []
    async for message in channel.history(limit=n):
        messages.append(message)
    messages.reverse()

    chat_history = ""
    for message in messages:
        chat_history += f"{message.author}: {message.content}\n"

    return chat_history


def fetch_memory_documents():
    return "\n".join(bot_memory)

async def query_gpt4(messages):
    model_engine = "gpt-3.5-turbo"

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages
    )

    return response['choices'][0]['message']['content'].strip()

@bot.event
async def on_ready():
    print("Bot is ready.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        ctx = await bot.get_context(message)
        query = message.content.strip()
        await process_query(ctx, query)
    await bot.process_commands(message)

@bot.command()
async def ask(ctx, *, query):
    await process_query(ctx, query)

@bot.command()
async def persona(ctx, *, new_persona=None):
    global current_persona

    if new_persona:
        current_persona = new_persona
        await ctx.send(f"Persona updated to: {current_persona}")
    else:
        await ctx.send(f"Current persona: {current_persona}")


async def process_query(ctx, query):
    chat_history = await fetch_chat_history(ctx.channel, 10)
    memory_documents = fetch_memory_documents()
    context = f"{current_persona}\n{chat_history}\n{memory_documents}"

    system_message = {"role": "system", "content": context}
    user_message = {"role": "user", "content": query}

    messages = [system_message, user_message]

    async with ctx.typing():
        response = await query_gpt4(messages)
    
    await ctx.send(response)

# Run the bot using the Discord bot token
bot.run(os.getenv("DISCORD_TOKEN"))
