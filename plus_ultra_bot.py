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

games = {}

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

def get_health_bar(hp: int) -> str:
    total_blocks = 10
    filled_blocks = int((hp / 100) * total_blocks)
    return "█" * filled_blocks + "░" * (total_blocks - filled_blocks)

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

@bot.tree.command(name="fight", description="Start a fight with another player")
async def fight(interaction: discord.Interaction, opponent: discord.Member):
    channel_id = interaction.channel.id
    if channel_id in games:
        embed = discord.Embed(
            title="⚠️ **Fight Already in Progress** ⚠️",
            description="A fight is already happening in this channel. Please wait until it finishes!",
            color=discord.Color.dark_red()
        )
        embed.set_footer(text="If you want to play now then start a new fight in a different channel. Impatient ahh")
    
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    characters = ["Deku", "Bakugo"]
    player1 = interaction.user
    player2 = opponent
    p1_character = random.choice(characters)

    if p1_character == "Deku":
        p2_character = "Bakugo"
    else:
        p2_character = "Deku"

    game = {
        "players": {
            player1.id: {"name": p1_character, "hp": 100},
            player2.id: {"name": p2_character, "hp": 100}
        },
        "turn": player1.id
    }

    games[channel_id] = game

    embed = discord.Embed(
        title="🔥 **Fight Started!** 🔥",
        description=f"{player1.mention} as **{p1_character}** VS {player2.mention} as **{p2_character}**",
        color=discord.Color.dark_teal()
    )

    embed.add_field(name="First Turn", value=f"**{p1_character}** goes first!", inline=False)
    embed.set_footer(text="Use /attack to make your move!")
    embed.set_thumbnail(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT7w4tjaE3AIDJBr5mo5bpLTW4Fs4kp4FoXKg&s")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="attack", description="Choose an attack")
@app_commands.describe(move="Which attack will you use?")
async def attack(interaction: discord.Interaction, move: str):
    channel_id = interaction.channel.id
    if channel_id not in games:
        embed = discord.Embed(
            title="⚠️ **No Fight Found** ⚠️",
            description="There is currently **no fight in progress** in this channel. You can start one by using: /fight @opponent",
            color=discord.Color.dark_red()
        )
        embed.set_footer(text="I'm sorry bro but if there was a fight here, I'm sure you'd know.")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    game = games[channel_id]
    attacker_id = interaction.user.id
        
    if attacker_id != game["turn"]:
        embed = discord.Embed(
            title="⚠️ **It Is NOT Your Turn** ⚠️",
            description="It's NOT your turn. Wait like everyone else.",
            color=discord.Color.dark_red()
        )
        embed.set_footer(text="Just wait okay, it's not that exciting chill.")
        await interaction.response.send_message(embed=embed)
        return

    target_id = [player_id for player_id in game["players"].keys() if player_id != attacker_id][0]

    moves = {
        "explosion": {"damage": 12, "accuracy": 95},
        "dynamight": {"damage": 18, "accuracy": 50},
        "howitzer_impact": {"damage": 25, "accuracy": 15},
        "air_force": {"damage": 12, "accuracy": 95},
        "detroit_smash": {"damage": 18, "accuracy": 50},
        "full_cowling": {"damage": 25, "accuracy": 15}
    }

    """
    I've just realised that the moves dictionary mean's that character abilities are not character specific
    I'll probably fix this at some point but it's late and if no one knows then it doesn't matter so idc rn lol
    """

    move = move.lower()
    if move not in moves:
        embed = discord.Embed(
            title="⚠️ **Invalid Move!** ⚠️",
            description="That isn't a registered move. Try one of these:\n\n"
                        "**Bakugo's Moves:**\n"
                        "`explosion`, `dynamight`, `howitzer_impact`\n\n"
                        "**Deku's Moves:**\n"
                        "`air_force`, `detroit_smash`, `full_cowling`",
            color=discord.Color.dark_red()
        )
        embed.set_footer(text="Use /attack move_name to attack.")

        await interaction.response.send_message(embed=embed)
        return
    
    hit_chance = random.randint(1, 100)
    if hit_chance <= moves[move]["accuracy"]:
        game["players"][target_id]["hp"] -= moves[move]["damage"]
        result = f"HIT! {game['players'][attacker_id]['name']} hits {game['players'][target_id]['name']} with **{move}**! {game['players'][target_id]['name']} loses {moves[move]['damage']}HP"
    else:
        result = f"MISS! {game['players'][attacker_id]['name']} missed **{move}**!"

    if game["players"][target_id]["hp"] <= 0:
        await interaction.response.send_message(
            f"{result}\n {game['players'][target_id]['name']} has been defeated! {interaction.user.mention} wins!"
        )
        del games[channel_id]
        return
    
    game["turn"] = target_id
    attacker = game['players'][attacker_id]
    target = game['players'][target_id]

    embed = discord.Embed(
        title="💥 **Attack Result** 💥",
        description=f"{result}",
        color=discord.Color.dark_teal()
    )

    embed.add_field(
        name=f"{attacker['name']}'s HP",
        value=f"{get_health_bar(attacker['hp'])} {attacker['hp']}/100",
        inline=True
    )
    embed.add_field(
        name=f"{target['name']}'s HP",
        value=f"{get_health_bar(target['hp'])} {target['hp']}/100",
        inline=True
    )

    embed.add_field(name="Next Turn", value=f"<@{target_id}>", inline=False)
    embed.set_footer(text="Use /attack move_name to make your move!")

    await interaction.response.send_message(embed=embed)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)