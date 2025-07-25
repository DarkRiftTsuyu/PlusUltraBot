import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
import asyncio
import traceback
import json
import psycopg2
from psycopg2.pool import SimpleConnectionPool
import time
from webserver import keep_alive

keep_alive()

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

DATABASE_URL = os.getenv("DATABASE_URL")
pool = SimpleConnectionPool(1, 10, DATABASE_URL, sslmode="require")

def get_connection():
    return pool.getconn()

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

def load_data():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT user_id, xp, level, coins, oc_name, oc_quirk, inventory FROM user_data;")
        rows = cursor.fetchall()

    user_data = {}
    for user_id, xp, level, coins, oc_name, oc_quirk, inventory_json in rows:
        user_data[user_id] = {
            "xp": xp,
            "level": level,
            "coins": coins,
            "oc": {
                "name": oc_name,
                "quirk": oc_quirk
            },
            "inventory": json.loads(inventory_json) if inventory_json else []
        }

    cursor.close()
    pool.putconn(conn)

    return user_data

def save_data(user_data):
    conn = get_connection()
    with conn.cursor() as cursor:
        for user_id, data in user_data.items():
            cursor.execute("""
                INSERT INTO user_data (user_id, xp, level, coins, oc_name, oc_quirk, inventory)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET
                    xp = EXCLUDED.xp,
                    level = EXCLUDED.level,
                    coins = EXCLUDED.coins,
                    oc_name = EXCLUDED.oc_name,
                    oc_quirk = EXCLUDED.oc_quirk,
                    inventory = EXCLUDED.inventory;
            """, (
                str(user_id),
                data.get("xp", 0),
                data.get("level", 0),
                data.get("coins", 0),
                data.get("oc", {}).get("name", None),
                data.get("oc", {}).get("quirk", None),
                json.dumps(data.get("inventory", []))
            ))
        conn.commit()

    cursor.close()
    pool.putconn(conn)

def get_level(xp):
    return xp // 500 + 1

with open("card_database.json", "r") as f:
    packs = json.load(f)

cooldowns = {}

games = {}

shop_items = {
    "1": {"name": "Plus Ultra Badge", "price": 200, "description": "Show off your Plus Ultra Spirit!"},
    "2": {"name": "League of Villians Pin", "price": 500, "description": "A collectible LOV pin"},
    "3": {"name": "All Might's Hair", "price": 1000, "description": "EAT THIS!!"},
    "4": {"name": "All Might Funko Pop", "price": 300, "description": "A Funko Pop of the Symbol of Peace"},
    "5": {"name": "Deku's Notebook", "price": 700, "description": "Izuku Midoriya's Hero Notebook"},
    "6": {"name": "Shigaraki's Hand Replica", "price": 1300, "description": "A creepy hand that sends chills down your spine."},
    "7": {"name": "Nomu DNA Sample", "price": 2500, "description": "For research purposes only... right?"},
    "8": {"name": "Hero Agency Poster", "price": 350, "description": "A signed poster from your favorite hero agency!"},
    "9": {"name": "Mineta's Grape Hair", "price": 50, "description": "A sticky souvenir from Minoru Mineta."},
    "10": {"name": "One For All Fragment", "price": 5000, "description": "A fragment of power passed through generations."}
}

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
        name = "/fight",
        value = 'Challenge someone to a fight!',
        inline = False
    )

    embed.add_field(
        name = "/cancel_fight",
        value = 'Cancel and on-going fight in that channel',
        inline = False
    )

    embed.add_field(
        name = "/attack",
        value = 'Attack someone in a fight or use "/attack move:help" to list all moves!',
        inline = False
    )

    embed.add_field(
        name = "/symbol_of_peace",
        value = "Displays All Might's iconic speech",
        inline = False
    )

    embed.add_field(
        name = "/shop",
        value = "Open the shop",
        inline = False

    )

    embed.add_field(
        name = "/buy",
        value = "Buy an item in the shop",
        inline = False
    )


    embed.add_field(
        name = "/inventory",
        value = "Open your inventory to view your items",
        inline = False
    )

    embed.add_field(
        name = "/create_oc",
        value = "create a custom hero to start earning coins and levelling up",
        inline = False
    )

    embed.add_field(
        name = "/leaderboard",
        value = "See the current hero leaderboard",
        inline = False
    )

    embed.add_field(
        name = "/profile",
        value = "See your custom hero's profile",
        inline = False
    )

    embed.add_field(
        name = "/train",
        value = "Train to gain XP every 30 minutes!",
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
    
    characters = ["Izuku Midoriya (Deku)", "Katsuki Bakugo (Dynamight)", "Ochaco Uraraka (Uravity)", "Tenya Iida (Ingenium)", "Eijiro Kirishima (Red Riot)", "Shoto Todoroki (Shoto)", "Tsuyu Asui (Froppy)", "Denki Kaminari (Chargebolt)", "Mina Ashido (Pinky)", "Kyoka Jiro (Earphone Jack)"]
    player1 = interaction.user
    player2 = opponent
    p1_character = random.choice(characters)
    characters.remove(p1_character)
    p2_character = random.choice(characters)

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
            description="There is currently **no fight in progress** in this channel. You can start one by using: `/fight @opponent`",
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

    target_id = [pid for pid in game["players"] if pid != attacker_id][0]

    moves = {
        "explosion": {"damage": 12, "accuracy": 95},
        "dynamight": {"damage": 18, "accuracy": 50},
        "howitzer_impact": {"damage": 25, "accuracy": 15},
        "air_force": {"damage": 12, "accuracy": 95},
        "detroit_smash": {"damage": 18, "accuracy": 50},
        "full_cowling": {"damage": 25, "accuracy": 15},
        "gunhead_martial_arts": {"damage": 12, "accuracy": 95},
        "float": {"damage": 18, "accuracy": 50},
        "meteor_shower": {"damage": 25, "accuracy": 15},
        "recipro_burst": {"damage": 12, "accuracy": 95},
        "recipro_extend": {"damage": 18, "accuracy": 50},
        "recipro_turbo": {"damage": 25, "accuracy": 15},
        "red_counter": {"damage": 12, "accuracy": 95},
        "red_gauntlet": {"damage": 18, "accuracy": 50},
        "unbreakable": {"damage": 25, "accuracy": 15},
        "half_cold": {"damage": 12, "accuracy": 95},
        "half_hot": {"damage": 18, "accuracy": 50},
        "prominence_burn": {"damage": 25, "accuracy": 15},
        "tongue_whip": {"damage": 12, "accuracy": 95},
        "camouflage": {"damage": 18, "accuracy": 55},
        "frog_frenzy": {"damage": 25, "accuracy": 15},
        "shock_discharge": {"damage": 12, "accuracy": 95},
        "lightning_burst": {"damage": 18, "accuracy": 50},
        "indiscriminate_shock": {"damage": 25, "accuracy": 15},
        "acid_spray": {"damage": 12, "accuracy": 95},
        "acid_rain": {"damage": 18, "accuracy": 50},
        "acid_man": {"damage": 25, "accuracy": 15},
        "earphone_jack": {"damage": 12, "accuracy": 95},
        "sound_wave": {"damage": 18, "accuracy": 50},
        "heartbeat_distortion": {"damage": 25, "accuracy": 15},
    }

    move = move.lower()
    if move not in moves:
        embed = discord.Embed(
            title="⚠️ **Invalid Move!** ⚠️",
            description="That isn't a registered move. Try one of these:\n\n"
                        "**Bakugo's Moves:**\n"
                        "`explosion`, `dynamight`, `howitzer_impact`\n\n"
                        "**Deku's Moves:**\n"
                        "`air_force`, `detroit_smash`, `full_cowling`\n\n"
                        "**Uravity's Moves:**\n"
                        "`gunhead_martial_arts`, `float`, `meteor_shower`\n\n"
                        "**Ingenium's Moves:**\n"
                        "`recipro_burst`, `recipro_extend`, `recipro_turbo`\n\n"
                        "**Red Riot's Moves:**\n"
                        "`red_counter`, `red_gauntlet`, `unbreakable`\n\n"
                        "**Todoroki's Moves:**\n"
                        "`half_cold`, `half_hot`, `prominence_burn`\n\n"
                        "**Froppy's Moves:**\n"
                        "`tongue_whip`, `camouflage`, `frog_frenzy`\n\n"
                        "**Kaminari's Moves:**\n"
                        "`shock_discharge`, `lightning_burst`, `indiscriminate_shock`\n\n"
                        "**Mina's Moves:**\n"
                        "`acid_spray`, `acid_rain`, `acid_man`\n\n"
                        "**Jiro's Moves:**\n"
                        "`earphone_jack`, `sound_wave`, `heartbeat_distortion`\n\n",
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
        reward_coins = random.randint(1, 100)
        user_id = str(interaction.user.id)

        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE user_data
                    SET coins = coins + %s
                    WHERE user_id = %s;
                """, (reward_coins, user_id))
            conn.commit()
        finally:
            pool.putconn(conn)

        embed = discord.Embed(
            title="🏆 Battle Over!",
            description=(
                f"{result}\n\n"
                f"**{game['players'][target_id]['name']}** has been **defeated!**\n"
                f"🎉 **{interaction.user.mention} wins the fight!** 🎉\n\n"
                f"💰 **You earned {reward_coins} coins!** 💰"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Thanks for playing!")
        embed.set_image(url="https://tenor.com/view/allmight-toshinori-yagi-yagi-toshinori-peace-anime-gif-6422195")

        await interaction.response.send_message(embed=embed)
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


@bot.tree.command(name="cancel_fight", description="Cancel the current fight in this channel")
async def cancel_fight(interaction: discord.Interaction):
    channel_id = interaction.channel.id

    if channel_id not in games:
        embed = discord.Embed(
            title="⚠️ **No Fight Found** ⚠️",
            description="There is no active fight in this channel to cancel.",
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed)
        return

    game = games[channel_id]

    if interaction.user.id not in game["players"].keys() and not interaction.user.guild_permissions.manage_guild:
        embed = discord.Embed(
            title="❌ **Permission Denied** ❌",
            description="Only the players in this fight or an admin can cancel it.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    else:
        embed = discord.Embed(
            title="🛑 **Fight Cancelled** 🛑",
            description=f"The fight in this channel has been **cancelled** by {interaction.user.mention}.",
            color=discord.Color.orange()
        )
        embed.set_footer(text="Use /fight to start a new battle!")
        await interaction.response.send_message(embed=embed)
        del games[channel_id]

@bot.tree.command(name="create_oc", description="Create your custom OC with a name and quirk")
@app_commands.describe(name="Your OC's name", quirk="Your OC's quirk")
async def create_oc(interaction: discord.Interaction, name: str, quirk: str):
    user_id = str(interaction.user.id)

    oc_exists = False
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT oc_name FROM user_data WHERE user_id = %s;", (user_id,))
            result = cursor.fetchone()
            if result and result[0] is not None:
                oc_exists = True
            else:
                cursor.execute("""
                    INSERT INTO user_data (user_id, xp, level, coins, oc_name, oc_quirk, inventory)
                    VALUES (%s, 0, 1, 0, %s, %s, '[]')
                    ON CONFLICT (user_id) DO UPDATE SET
                        oc_name = EXCLUDED.oc_name,
                        oc_quirk = EXCLUDED.oc_quirk;
                """, (user_id, name, quirk))
        conn.commit()
    finally:
        pool.putconn(conn)

    if oc_exists:
        await interaction.response.send_message("You already have an OC! Use /profile to view it.")
    else:
        await interaction.response.send_message(f"OC created! Name: **{name}**, Quirk: **{quirk}**")



@bot.tree.command(name="profile", description="Show your hero profile")
async def profile(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    result = None
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT xp, coins, oc_name, oc_quirk
                FROM user_data WHERE user_id = %s;
            """, (user_id,))
            result = cursor.fetchone()
    finally:
        pool.putconn(conn)

    if not result or result[2] is None:
        await interaction.response.send_message("You don't have an OC yet! Use /create_oc to create one.")
        return

    xp, coins, oc_name, oc_quirk = result
    level = get_level(xp)

    embed = discord.Embed(title=f"{interaction.user.display_name}'s Hero Profile", color=discord.Color.blue())
    embed.add_field(name="OC Name", value=oc_name, inline=False)
    embed.add_field(name="Quirk", value=oc_quirk, inline=False)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=xp, inline=True)
    embed.add_field(name="Coins", value=coins, inline=True)

    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="train", description="Train your hero to gain XP")
async def train(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    now = time.time()

    if user_id in cooldowns and now - cooldowns[user_id] < 1800:
        await interaction.response.send_message(f"{interaction.user.mention} is on cooldown for 30 minutes")
        return

    cooldowns[user_id] = now

    gained_xp = random.randint(10, 30)
    leveled_up = False
    new_level = None

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT xp, level FROM user_data WHERE user_id = %s;", (user_id,))
            result = cursor.fetchone()

            if not result:
                await interaction.response.send_message("You don't have an OC yet! Use /create_oc to create one.")
                return

            current_xp, current_level = result
            new_xp = current_xp + gained_xp
            new_level = get_level(new_xp)

            if new_level > current_level:
                leveled_up = True
                cursor.execute(
                    "UPDATE user_data SET xp = %s, level = %s WHERE user_id = %s;",
                    (new_xp, new_level, user_id)
                )
            else:
                cursor.execute("UPDATE user_data SET xp = %s WHERE user_id = %s;", (new_xp, user_id))

            conn.commit()
    finally:
        pool.putconn(conn)

    if leveled_up:
        await interaction.response.send_message(
            f"You trained hard and gained {gained_xp} XP! 🎉 You leveled up to **Level {new_level}**! "
            f"Come back in 30 minutes to train again!"
        )
    else:
        await interaction.response.send_message(
            f"You trained hard and gained {gained_xp} XP! Keep going! "
            f"Come back in 30 minutes to train again!"
        )


@bot.tree.command(name="leaderboard", description="Show the top 10 users by XP!")
async def leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, xp, level, coins
                FROM user_data
                ORDER BY xp DESC
                LIMIT 10;
            """)
            top_users = cursor.fetchall()
    finally:
        pool.putconn(conn)

    if not top_users:
        await interaction.followup.send("No data yet! Start chatting to gain XP.")
        return

    embed = discord.Embed(title="🏆 **PLUS ULTRA LEADERBOARD** 🏆", color=discord.Color.gold())

    for i, (user_id, xp, level, coins) in enumerate(top_users, start=1):
        try:
            user = await bot.fetch_user(int(user_id))
            name = user.name
        except:
            name = f"User ID {user_id}"

        embed.add_field(
            name=f"#{i} {name}",
            value=f"Level: **{level}** | XP: **{xp}** | Coins: **{coins}**",
            inline=False
        )

    await interaction.followup.send(embed=embed)



@bot.tree.command(name="shop", description="Purchase Collectable items and Boosts for fights!")
async def shop(interaction: discord.Interaction):
    if not shop_items:
        await interaction.response.send_message("Shop is empty, please come back later!")

    embed = discord.Embed(title="🛒 **Shop** 🛒", color=discord.Color.pink())

    for key, item in shop_items.items():
        embed.add_field(
            name=f"{key}. {item['name']}",
            value=f"Price: {item['price']} coins\n{item['description']}",
            inline=False
            )

    embed.set_footer(text="Use /buy <item_id> to purchase an item!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="buy", description="Buy an item from the shop")
@app_commands.describe(item_id="The ID number of the item you want to buy")
async def buy(interaction: discord.Interaction, item_id: str):
    await interaction.response.defer()

    user_id = str(interaction.user.id)

    if item_id not in shop_items:
        return await interaction.followup.send("❌ Invalid item ID!")

    item = shop_items[item_id]

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT coins, inventory FROM user_data WHERE user_id = %s FOR UPDATE;", (user_id,))
            result = cursor.fetchone()

            if not result:
                await interaction.followup.send("You don't have an OC yet! Use /create_oc to create one.")
                return

            coins, inventory = result
            inventory = inventory or []

            if coins < item["price"]:
                await interaction.followup.send("❌ You don't have enough coins!")
                return

            coins -= item["price"]
            inventory.append(item["name"])

            inventory_json = json.dumps(inventory)

            cursor.execute("""
                UPDATE user_data
                SET coins = %s, inventory = %s
                WHERE user_id = %s;
            """, (coins, inventory_json, user_id))
            conn.commit()

        await interaction.followup.send(f"✅ {interaction.user.mention} bought **{item['name']}** for {item['price']} coins!")
    except Exception as e:
        traceback.print_exc()
        await interaction.followup.send(f"⚠️ Something went wrong: `{e}`")
    finally:
        if conn:
            pool.putconn(conn)

@bot.tree.command(name="inventory", description="Open your inventory")
async def inventory(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)

    user_id = str(interaction.user.id)

    def fetch_inventory():
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT inventory FROM user_data WHERE user_id = %s;", (user_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    return json.loads(result[0]) if isinstance(result[0], str) else result[0]
                return []
        finally:
            pool.putconn(conn)

    inventory_list = await asyncio.to_thread(fetch_inventory)

    if not inventory_list:
        await interaction.followup.send("Your inventory is empty!")
        return
    embed = discord.Embed(
        title=f"{interaction.user.display_name}'s Inventory",
        color=discord.Color.dark_teal()
    )
    item_text = "\n".join([f"{index}. {item}" for index, item in enumerate(inventory_list, start=1)])
    embed.add_field(name="Items", value=item_text, inline=False)
    embed.set_footer(text=f"Total items: {len(inventory_list)}")

    await interaction.followup.send(embed=embed)



@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    xp_gain = random.randint(5, 15)
    coins_gain = random.randint(1, 3)
    level_up_message = None

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT xp, coins, level FROM user_data WHERE user_id = %s;", (user_id,))
            result = cursor.fetchone()

            if result:
                xp, coins, level = result
                new_xp = xp + xp_gain
                new_coins = coins + coins_gain
                new_level = get_level(new_xp)

                cursor.execute("""
                    UPDATE user_data
                    SET xp = %s, coins = %s, level = %s
                    WHERE user_id = %s;
                """, (new_xp, new_coins, new_level, user_id))

                if new_level > level:
                    level_up_message = f"🎉 {message.author.mention} leveled up to **Level {new_level}**! PLUS ULTRA!"
            else:
                cursor.execute("""
                    INSERT INTO user_data (user_id, xp, coins, level, oc_name, oc_quirk, inventory)
                    VALUES (%s, %s, %s, %s, NULL, NULL, '[]');
                """, (user_id, xp_gain, coins_gain, get_level(xp_gain)))

        conn.commit()
    finally:
        pool.putconn(conn)

    if level_up_message:
        await message.channel.send(level_up_message)

    await bot.process_commands(message)

def build_card_lookup(packs):
    lookup = {}
    for pack_name, pack_data in packs.items():
        for rarity_name, rarity_list in pack_data.items():
            if isinstance(rarity_list, list):
                for card in rarity_list:
                    lookup[card["name"]] = card
    return lookup

card_lookup = build_card_lookup(packs)

@bot.tree.command(name="cards", description="View all the cards you own with images")
async def cards(interaction: discord.Interaction):
    import time

    print("Reached cards command handler.")
    await interaction.response.defer(ephemeral=False)
    print("Deferred response.")

    user_id = str(interaction.user.id)
    print(f"User ID: {user_id}")

    def fetch_cards():
        print("Fetching cards from database.")
        print("Before get_connection()")
        conn = get_connection()
        print("After get_connection()")
        try:
            with conn.cursor() as cursor:
                print("Before execute()")
                cursor.execute("""
                    SELECT item_name, quantity 
                    FROM inventory 
                    WHERE user_id = %s AND item_type = 'card';
                """, (user_id,))
                print("After execute()")
                result = cursor.fetchall()
                print("Database query successful. Result:", result)
                return result
        except Exception as e:
            print("Exception during database fetch:", e)
            traceback.print_exc()
            return None
        finally:
            print("Returning connection to pool.")
            pool.putconn(conn)
            print("Fetching cards from database.")
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT item_name, quantity 
                        FROM inventory 
                        WHERE user_id = %s AND item_type = 'card';
                    """, (user_id,))
                    result = cursor.fetchall()
                    print("Database query successful. Result:", result)
                    return result
            except Exception as e:
                print("Exception during database fetch:", e)
                traceback.print_exc()
                return None
            finally:
                print("Returning connection to pool.")
                pool.putconn(conn)

    print("Starting card fetch in thread.")
    user_cards = await asyncio.to_thread(fetch_cards)
    print("User cards object: ", user_cards)

    if not user_cards:
        print("No cards found. Sending empty message.")
        await interaction.followup.send("❌ You don't own any cards yet!")
        return

    with open("card_database.json", "r") as f:
        pack = json.load(f)

    header_embed = discord.Embed(
        title=f"🃏 **{interaction.user.display_name}'s Card Collection** 🃏",
        description=f"Total unique cards: **{len(user_cards)}**",
        color=discord.Color.purple()
    )

    embeds = [header_embed]
    print("Created header embed.")

    for card_name, quantity in user_cards:
        print(f"Processing card: {card_name} (quantity: {quantity})")
        card_data = card_lookup.get(card_name)

        for pack_name, pack_data in pack.items():
            print(f"Checking pack: {pack_name}")
            for rarity_name, rarity_list in pack_data.items():
                print(f"Checking rarity: {rarity_name}")
                if isinstance(rarity_list, list):
                    for card in rarity_list:
                        print(f"Checking card in rarity list: {card.get('name', 'N/A')}")
                        if card["name"] == card_name:
                            card_data = card
                            print(f"Found matching card data for {card_name}")
                            break
                    if card_data:
                        break
            if card_data:
                break

        if card_data:
            print(f"Creating card embed for {card_name}")
            card_embed = discord.Embed(
                title=f"{card_name} ×{quantity}",
                description=card_data["description"],
                color=discord.Color.blue()
            )
            card_embed.set_image(url=card_data["image"])
            embeds.append(card_embed)
        else:
            print(f"No image found for {card_name}, creating fallback embed.")
            fallback_embed = discord.Embed(
                title=f"{card_name} ×{quantity}",
                description="(No image found)",
                color=discord.Color.dark_gray()
            )
            embeds.append(fallback_embed)

    print(f"Total embeds to send: {len(embeds)}")

    batch_size = 10
    for i in range(0, len(embeds), batch_size):
        print(f"Sending embed batch {i // batch_size + 1}: embeds[{i}:{i+batch_size}]")
        try:
            await interaction.followup.send(embeds=embeds[i:i+batch_size])
            print(f"Batch {i // batch_size + 1} sent successfully.")
        except Exception as e:
            print(f"Exception while sending embed batch {i // batch_size + 1}: {e}")
            traceback.print_exc()
            await interaction.followup.send(f"❌ Error sending embeds batch {i // batch_size + 1}: {e}")
        time.sleep(0.5)  # Avoid rate limits

    print("Finished sending all embed batches.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
