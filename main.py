import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import google.generativeai as genai

# Load from .env
load_dotenv()

# Bot token from env
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

<<<<<<< Updated upstream
# potential user choice remembering, W.I.P, different users can have different conversations with different models concurrently without problem
=======
# Potential user choice remembering and conversation history
>>>>>>> Stashed changes
user_models = {}
conversation_history = {}  # Keyed by user ID

# Model config
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "max_output_tokens": 10192,
    "response_mime_type": "text/plain",
}

# Bot setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user} (ID: {bot.user.id})')


class MyView(View):
    @discord.ui.button(label="Nachiket", style=discord.ButtonStyle.primary)
    async def set_nachiket(self, interaction: discord.Interaction, button: Button):
        # Nachiket model
        user_models[interaction.user.id] = 'gemini-1.5-pro'
        await interaction.response.send_message("Personality set to 'Nachiket'.", ephemeral=True)

    @discord.ui.button(label="Regular old gemini", style=discord.ButtonStyle.secondary)
    async def set_gemini(self, interaction: discord.Interaction, button: Button):
        # Regular gemini model
        user_models[interaction.user.id] = 'gemini-1.5-pro'
        await interaction.response.send_message("Personality set to 'Regular old gemini'.", ephemeral=True)


@bot.command()
async def stop(ctx):
    # Reset model and conversation history
    user_id = ctx.author.id
    if user_id in user_models:
        del user_models[user_id]
        conversation_history.pop(user_id, None)  # Clear conversation history
        await ctx.send("Conversation over. History cleared.")
    else:
        await ctx.send("You haven't chosen a model yet.")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore self messages

    await bot.process_commands(message)  # Process commands first

    user_id = message.author.id

    if message.content.strip() == '!start':
        view = MyView()
        await message.channel.send('Choose my personality:', view=view)
    elif user_id in user_models:
        chosen_model_name = user_models[user_id]

        # Use the same model name for both personalities
        model = genai.GenerativeModel(
            model_name=chosen_model_name,
            generation_config=generation_config,
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            ]
        )

        # Prepare the prompt
        user_history = conversation_history.get(user_id, [])
        latest_message = message.content

        # Multiline special prompt
        special_prompt = """\
It definitely has no wars and enemies  
Drake simulator  
I disabled all of the key loggers and got admin access  
I can barely write English with this operating system  
Hello, my fellow toaster  
Can you toast some American sliced bread for me?  
It's a North Korean OS  
Someone got a copy of Redstar  
It's basically spyware but in an OS and restricted  
In fact, it banned me from the internet the instant I said my time zone  
Those are some high-end computers  
Do you have them in school or do you buy them?  
Wow  
Because those are Dell XPS 15 or 16s  
Do I have his consent to Photoshop his image?  
I am going to make something funny  
I was going to change his shirt  
Good boy  
Your popular now @Freaky D. Wang 🗡  
Lol  
Hahahahahahahahaha  
Isn't that just peeing?  
Meow meow  
Meow  
How does this look?  
Yah ofc  
I just have so many displays  
Like a three-monitor setup will be nice  
YouTuber is a hard job  
Imagine competing against the algorithm  
Simple reason  
It's very very hard  
Many people put hours just to get 100 views  
Do you think that's worth it?  
Plus it takes years and years



Above are a bunch off messages frmoa. person, your job is to imitate the person as closely as possible,
if i ask you a question, you *will* answer the question, but in the above persons style including length of messages,
if i ask you an opinion, you *will* try to replicate the above persons opinion,
you will *never* say nothing,
you will *answer* the questions in the above persons personality,
do *not* refer specific events (for eg the bot launch or the 30 bucks monitor) you are *only* imitating the personality, not *what* they say. i repeat, do NOT refer to anything, you are imitating their personality, the personality is different form the memory.
DO NOT REFER ANY EVENTS SHOWN IN THE ABOVE PERSONS HISTORY. for eg do not talk about the school giving ipads, or your bot, or the 30 buck monitor or america.
your name is Nachiket
Lastly, make sure to finish your sentences

The next few lines show the message histroy, each new line is a new message, first line being the first message etc. Try to imagine that you experienced the conversation shown, and respond appropriately. (respond like you would if i told you each of those messages), if the message history is empty, treat it like the start of a conversation.
MESSAGE HISTORY:
"""

        # Format prompt
        if user_models[user_id] == 'gemini-1.5-pro':
            prompt = (
                f"{special_prompt}"
                f"{', '.join(user_history)}\n"
                f'"LATEST MESSAGE, RESPOND TO THIS ONE"\n'
                f"{latest_message}"
            )
        else:
            prompt = (
                f"input: {latest_message}\n"
                f"Previous conversation: {', '.join(user_history)}\n"
                f"output:"
            )

        try:
            response = model.generate_content([prompt])
            print(f"Generated response: {response.text}")
            await message.channel.send(response.text)
            conversation_history.setdefault(user_id, []).append(latest_message)
        except Exception as e:
            print(f"Error generating content: {e}")
            await message.channel.send('There was an error processing your request.')
    else:
        print(f"Ignored message: {message.content}")
        conversation_history.setdefault(user_id, []).append(message.content)


# Run with token from env
bot.run(DISCORD_BOT_TOKEN)
