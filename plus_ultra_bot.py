import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
from webserver import keep_alive

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

plus_ultra = True

plus_ultra_quotes = [
     '“Go beyond! Plus Ultra!” ― Kohei Horikoshi, 僕のヒーローアカデミア 11 [Boku No Hero Academia 11]',
     '“Even heroes must cry sometimes” ― Kohei Horikoshi, 僕のヒーローアカデミア 15 [Boku No Hero Academia 15]',
     '“But you know, meddling when you dont need to is the essence of being a hero.” ― Kohei Horikoshi, My Hero Academia Vol 6-15 Kohei Horikoshi Collection Set 10',
     '“If I dont act now, forget being a hero, Im not even a man!” ― Kohei Horikoshi',
]

mha_characters = {
    "Izuku Midoriya": {"quirk": "One For All", "aliases": ["deku", "izuku", "midoriya", "izuku midoriya"]},
    "Katsuki Bakugo": {"quirk": "Explosion", "aliases": ["bakugo", "kacchan", "katsuki", "katsuki bakugo"]},
    "Shoto Todoroki": {"quirk": "Half-Cold Half-Hot", "aliases": ["todoroki", "shoto", "shouto", "shoto todoroki"]},
    "Ochaco Uraraka": {"quirk": "Zero Gravity", "aliases": ["uraraka", "ochaco", "ochako"]},
    "Tenya Iida": {"quirk": "Engine", "aliases": ["iida", "tenya"]},
    "Tsuyu Asui": {"quirk": "Frog", "aliases": ["tsuyu", "asui", "froppy"]},
    "Momo Yaoyorozu": {"quirk": "Creation", "aliases": ["momo", "yaoyorozu"]},
    "Eijiro Kirishima": {"quirk": "Hardening", "aliases": ["kirishima", "eijiro", "red riot"]},
    "Denki Kaminari": {"quirk": "Electrification", "aliases": ["kaminari", "denki", "chargebolt"]},
    "Fumikage Tokoyami": {"quirk": "Dark Shadow", "aliases": ["tokoyami", "fumikage"]},
    "Minoru Mineta": {"quirk": "Pop Off", "aliases": ["mineta", "minoru"]},
    "Mezo Shoji": {"quirk": "Dupli-Arms", "aliases": ["shoji", "mezo"]},
    "All Might": {"quirk": "One For All", "aliases": ["all might", "toshinori", "yagi"]},
    "Endeavor": {"quirk": "Hellflame", "aliases": ["endeavor", "enji todoroki"]},
    "Hawks": {"quirk": "Fierce Wings", "aliases": ["hawks", "keigo takami"]},
    "Tomura Shigaraki": {"quirk": "Decay", "aliases": ["shigaraki", "tomura", "tenko shimura"]},
    "Dabi": {"quirk": "Blueflame", "aliases": ["dabi", "touya todoroki"]},
    "Himiko Toga": {"quirk": "Transform", "aliases": ["toga", "himiko"]},
    "Twice": {"quirk": "Double", "aliases": ["twice", "jin bubaigawara"]},
    "All For One": {"quirk": "All For One", "aliases": ["all for one", "afo"]},
}

alias_find = {alias: name for name, data in mha_characters.items() for alias in data["aliases"]}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

@bot.tree.command(name='help', description="List all of Plus Ultra Bot's Commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title = 'Bot Commands',
        description ="Welcome to Plus Ultra Bot's Help Section!",
        color = discord.Colour.dark_teal()
    )

    embed.set_thumbnail(url = "https://cdn.discordapp.com/avatars/1395898496086708254/92099f2beeb0470f323325f615d5573f.webp?size=80")

    embed.add_field(
        name = "/help",
        value = "List all of Plus Ultra Bot's Commands",
        inline= False
    )

    embed.add_field(
        name = "/quirk",
        value = "Name a character and find out their quirk!",
        inline= False
    )

    embed.add_field(
        name = "/plus_ultra",
        value = "Displays a Plus Ultra Quote!",
        inline= False
    )

    embed.add_field(
        name = "/hero_ranking",
        value = "Displays the current Top 10 hero ranking",
        inline = False
    )

    embed.add_field(
        name = "/smash",
        value = 'Randomly says a % power of “Detroit Smash!”',
        inline = False
    )

    embed.add_field(
        name = "/smash_someone",
        value = 'Hit someone with a smash!',
        inline = False
    )

    embed.add_field(
    name = "/symbol_of_peace",
    value = "Displays All Might's iconic speech",
    inline = False
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='plus_ultra', description="Displays a Plus Ultra Quote!")
async def plus_ultra_command(interaction: discord.Interaction):
    global quote
    quote = random.choice(plus_ultra_quotes)
    await interaction.response.send_message(f"**{quote}**")

@bot.tree.command(name='quirk', description='Name a character and find out their quirk!')
@app_commands.describe(character_input="Enter the character name")
async def quirk(interaction: discord.Interaction, *, character_input: str):
    character_input = character_input.lower()
    character_name = alias_find.get(character_input)

    if character_name:
        global quirk 
        quirk = mha_characters[character_name]["quirk"]
        await interaction.response.send_message(f"**{character_name}**'s quirk is **{quirk}**!")
    else:
        await interaction.response.send_message("Character not found! Try using their real or hero name.")

@bot.tree.command(name='hero_ranking', description="Displays the current Top 10 hero ranking")
async def hero_ranking(interaction: discord.Interaction):
    global hero_ranks
    hero_ranks = ['Number 1, Flame Hero: Endeavor',
                  'Number 2, Wing Hero: Hawks',
                  'Number 3, Fiber Hero: Best Jeanist',
                  'Number 4, Ninja Hero: Edgeshot',
                  'Number 5, Rabbit Hero: Mirko',
                  'Number 6, Shield Hero: Crust',
                  'Number 7, Wood Hero: Kamui Woods',
                  'Number 8, Laundry Hero: Wash',
                  'Number 9, Equipped Hero: Yoroi Musha',
                  'Number 10, Dragon Hero: Ryukyu'
                  ]
    heroes_list = "\n".join([f"**{hero}**" for hero in hero_ranks])
    await interaction.response.send_message(heroes_list)

@bot.tree.command(name='smash_someone', description='Hit someone with a smash')
@app_commands.describe(smash_someone="ping someone")
async def smash_someone(interaction: discord.Interaction, *, smash_someone: str):
    global states
    states = [
        "WYOMING",
        "DELAWARE",
        "TEXAS",
        "DETROIT",
        "UNITED STATES OF",
        "MANCHESTER",
        "MISSOURI",
        "CALIFORNIA"
    ]
    global randstate
    randstate = random.choice(states)
    smash = random.randint(0, 100)
    if smash_someone:
        await interaction.response.send_message(f"{smash_someone} was hit with a **{smash}% {randstate} SMASH!!!**")

@bot.tree.command(name='smash', description='Randomly says a % power of “Detroit Smash!”')
async def smash(interaction: discord.Interaction):
    randstate = random.choice(states)
    smash = random.randint(0, 100)
    await interaction.response.send_message(f"**{smash}% {randstate} SMASH!!!**")

@bot.tree.command(name="symbol_of_peace", description="Display All Might's iconic speech")
async def symbol_of_peace(interaction: discord.Interaction):
    speech = (
        "**Now, for a lesson. you may have heard these words before, but I'll teach you what they really mean.**\n\n"
        "**GO BEYOND!**\n"
        "**PLUS...ULTRAAAAAAAAAAAAAAAAAAAAA!!!**"
    )

    embed = discord.Embed(
        title="The Symbol of Peace",
        description=speech,
        color=discord.Color.gold()
    )

    embed.set_image(url="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZG5qaHppbHV2YTI4MzJlMnZ1eHI1OWR6c243aGU2czF0eDMxN3M3dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/QwH7v7J1tBrq0/giphy.gif")
    embed.set_footer(text="All Might - The Symbol of Peace")

    await interaction.response.send_message(embed=embed)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)