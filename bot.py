import os
import asyncio
import discord
import openai
import whisper

from discord.ext import commands
from voice import synthesize_text_with_watson
from dotenv import load_dotenv

# Load environment variables from .env file
model = whisper.load_model("small")

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
bot.audio_responses = False
# Initialize bot_memory (you can use a dictionary, database, or file storage)
bot.memory = []

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
    return "\n".join(bot.memory)

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
            audio_file_path = f"./tmp/in/{attachment.filename}"
            await attachment.save(audio_file_path)

            # Transcribe the audio file async
            loop = asyncio.get_event_loop()
            transcription = await loop.run_in_executor(None, transcribe_audio_file, audio_file_path)

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

# Add the new command !audio
@bot.command(name="audio")
async def toggle_audio_responses(ctx):
    bot.audio_responses = not bot.audio_responses
    response = "Respostas em áudio ligadas." if bot.audio_responses else "Respostas em áudiod desligadas."
    await ctx.send(response)

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

    async with ctx.typing():
        if bot.audio_responses:
            #Synthetize voice async
            loop = asyncio.get_event_loop()
            audio_file_path = await loop.run_in_executor(None, synthesize_text_with_watson, response)
            await reply.channel.send(file=discord.File(audio_file_path), reference=reply)
        
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
