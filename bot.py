import os
import asyncio
import discord
import openai
import whisper

from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
model = whisper.load_model("medium")

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

def transcribe_audio_file(audio_file_path: str) -> str:
    result = model.transcribe(audio_file_path)
    return result["text"]

async def transcribe_audio_file_async(audio_file_path: str) -> str:
    loop = asyncio.get_event_loop()
    transcription = await loop.run_in_executor(None, transcribe_audio_file, audio_file_path)
    return transcription

@bot.event
async def on_ready():
    print("Bot is ready.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    ctx = await bot.get_context(message)

    if message.content.startswith('!ask') or bot.user in message.mentions:
        query = message.content.lstrip('!ask').strip()
        await process_query(ctx, query)

    # Check if an audio file is attached to the message
    if message.attachments:
        attachment = message.attachments[0]
        if attachment.content_type.startswith("audio/"):
            # Answer
            await message.channel.send("Opa, parece que você mandou um audio. Deixa eu só escutar aqui e já retorno...", reference=message)
            # Download the audio file
            audio_file_path = f"./temp_audio/{attachment.filename}"
            await attachment.save(audio_file_path)

            # Transcribe the audio file
            transcription = await transcribe_audio_file_async(audio_file_path)

            # Remove the temporary audio file
            os.remove(audio_file_path)

            # Process the transcribed audio query
            await process_audio_query(ctx, transcription, reply=message)

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


async def process_audio_query(ctx, transcription, reply=None):
    system_message_content = "Você acabou de receber essa transcrição de um audio e deve responder com suas considerações pessoais sobre o assunto."
    context = f"{current_persona}\n{system_message_content}"

    system_message = {"role": "system", "content": context}
    user_message = {"role": "user", "content": transcription}

    messages = [system_message, user_message]

    async with ctx.typing():
        response = await query_gpt4(messages)
    
    if reply:
        await reply.channel.send(response, reference=reply)
    else:
        await ctx.send(response)

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
