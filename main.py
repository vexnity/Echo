import os
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
# helo
# load frmo .env
load_dotenv()

# bot token frmo env
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# wip user choice remembering, somewhat working, different users can use different models at the same time
user_models = {}

# conf model
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "max_output_tokens": 10192,
    "response_mime_type": "text/plain",
}

# reset model
model = None

# bot setup
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
        user_models[interaction.user.id] = 'tunedModels/big-nachi-cz3x2g4q1xag'
        await interaction.response.send_message("Personality set to 'Nachiket'.", ephemeral=True)

    @discord.ui.button(label="Regular old gemini", style=discord.ButtonStyle.secondary)
    async def set_gemini(self, interaction: discord.Interaction, button: Button):
        # Regular gemini model
        user_models[interaction.user.id] = 'gemini-1.5-flash'
        await interaction.response.send_message("Personality set to 'Regular old gemini'.", ephemeral=True)


@bot.command()
async def stop(ctx):
    # Reset model
    user_id = ctx.author.id
    if user_id in user_models:
        del user_models[user_id]
        await ctx.send("Conversation over.")
    else:
        await ctx.send("You haven't chosen a model yet.")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore self messages

    await bot.process_commands(message)  #pProcesses commands so that they get processed before being processed

    if message.content.strip() == '!start':
        view = MyView()
        await message.channel.send('Choose my personality:', view=view)
    elif message.author.id in user_models:
        chosen_model_name = user_models[message.author.id]
        model = genai.GenerativeModel(
            model_name=chosen_model_name,
            generation_config=generation_config,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                },
            ]
        )

        try:
            response = model.generate_content([
                f"input: {message.content}",
                "output: ",
            ])
            print(f"Generated response: {response.text}")
            await message.channel.send(response.text)
        except Exception as e:
            print(f"Error generating content: {e}")
            await message.channel.send('There was an error processing your request.')
    else:
        print(f"Ignored message: {message.content}")


# run with token frmo env
bot.run(DISCORD_BOT_TOKEN)
