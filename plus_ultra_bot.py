import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
import json
import time
from webserver import keep_alive

keep_alive()

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

DATA_FILE = "userdata.json"

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as file:
        user_data = json.load(file)
else:
    user_data = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

def get_level(xp):
    return xp // 100 + 1

cooldowns = {}

games = {}

shop_items = {
    "1": {"name": "Plus Ultra Badge", "price": 200, "description": "Show off your Plus Ultra Spirit!"},
    "2": {"name": "League of Villians Pin", "price": 500, "description": "A collectible LOV pin"},
    "3": {"name": "All Might's Hair", "price": 1000, "description": "EAT THIS!!"},
    "4": {"name": "All Might Funko Pop", "price": 300, "description": "A Funko Pop of the Symbol of Peace"},
    "5": {"name": "Deku's Notebook", "price": 700, "description": "Izuku idoriya's Hero Notebook"},
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
    
    characters = ["Deku", "Bakugo", "Uravity", "Ingenium", "Red Riot"]
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
        "full_cowling": {"damage": 25, "accuracy": 15},
        "gunhead_martial_arts": {"damage": 12, "accuracy": 95},
        "float": {"damage": 18, "accuracy": 50},
        "meteor_shower": {"damage": 25, "accuracy": 15},
        "recipro_burst": {"damage": 12, "accuracy": 95},
        "recipro_extend": {"damage": 18, "accuracy": 50},
        "recipro_turbo": {"damage": 25, "accuracy": 15},
        "red_counter": {"damage": 12, "accuracy": 95},
        "red_gauntlet": {"damage": 18, "accuracy": 50},
        "unbreakable": {"damage": 25, "accuracy": 15}
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
                        "`air_force`, `detroit_smash`, `full_cowling`\n\n"
                        "**Uravity's Moves:**\n"
                        "`gunhead_martial_arts`, `float`, `meteor_shower`\n\n"
                        "**Ingenium's Moves:**\n"
                        "`recipro_burst`, `recipro_extend`, `recipro_turbo`\n\n"
                        "**Red Riot's Moves:**\n"
                        "`red_counter`, `red_gauntlet`, `unbreakable`",
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
        embed = discord.Embed(
            title="🏆 Battle Over!",
            description=(
                f"{result}\n\n"
                f"**{game['players'][target_id]['name']}** has been **defeated!**\n"
                f"🎉 ** {interaction.user.mention} wins the fight!** 🎉"
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
    if user_id in user_data:
        await interaction.response.send_message("You already have an OC! Use /profile to view it.")
        return

    user_data[user_id] = {
        "xp": 0,
        "level": 1,
        "coins": 0,
        "oc": {
            "name": name,
            "quirk": quirk},
        "inventory": [],
    }
    save_data()
    await interaction.response.send_message(f"OC created! Name: **{name}**, Quirk: **{quirk}**")

@bot.tree.command(name="profile", description="Show your hero profile")
async def profile(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in user_data:
        await interaction.response.send_message("You don't have an OC yet! Use /create_oc to create one.")
        return

    data = user_data[user_id]
    xp = data["xp"]
    coins = data["coins"]
    level = get_level(xp)
    oc = data["oc"]

    embed = discord.Embed(title=f"{interaction.user.display_name}'s Hero Profile", color=discord.Color.blue())
    embed.add_field(name="OC Name", value=oc["name"], inline=False)
    embed.add_field(name="Quirk", value=oc["quirk"], inline=False)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="XP", value=xp, inline=True)
    embed.add_field(name="Coins", value=coins, inline=True)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="train", description="Train your hero to gain XP")
async def train(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in user_data:
        await interaction.response.send_message("You don't have an OC yet! Use /create_oc to create one.")
        return
    
    now = time.time()

    if user_id in cooldowns and now - cooldowns[user_id] < 1800:
        await interaction.response.send_message(f"@{interaction.user} is on cooldown for 30 minutes")
        return 

    cooldowns[user_id] = now

    gained_xp = random.randint(10, 30)
    user_data[user_id]["xp"] += gained_xp
    new_level = get_level(user_data[user_id]["xp"])

    if new_level > user_data[user_id]["level"]:
        user_data[user_id]["level"] = new_level
        save_data()
        await interaction.response.send_message(f"You trained hard and gained {gained_xp} XP! You leveled up to level {new_level}! Come back in 30 minutes to train again!")
    else:
        save_data()
        await interaction.response.send_message(f"You trained hard and gained {gained_xp} XP! Keep going! Come back in 30 minutes to train again!")

@bot.tree.command(name="leaderboard", description="Show the top 10 users by XP!")
async def leaderboard(interaction: discord.Interaction):
    if not user_data:
        await interaction.response.send_message("No data yet! Start chatting to gain XP.")
        return

    top_users = sorted(user_data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]

    embed = discord.Embed(title="🏆 **PLUS ULTRA LEADERBOARD** 🏆", color=discord.Color.gold())
    for i, (user_id, data) in enumerate(top_users, start=1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(
            name=f"#{i} {user.name}",
            value=f"Level: **{data['level']}** | XP: **{data['xp']}** | Coins: **{data['coins']}**",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

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
    user_id = str(interaction.user.id)

    if item_id not in shop_items:
        await interaction.response.send_message("❌ Invalid item ID!", ephemeral=True)
        return

    item = shop_items[item_id]
    if user_data[user_id]["coins"] < item["price"]:
        await interaction.response.send_message("❌ You don't have enough coins!", ephemeral=True)
        return

    user_data[user_id]["coins"] -= item["price"]
    user_data[user_id]["inventory"].append(item["name"])
    save_data()

    await interaction.response.send_message(f"✅ {interaction.user.mention} bought **{item['name']}** for {item['price']} coins!")

@bot.tree.command(name="inventory", description="Open your inventory")
async def inventory(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id not in user_data or not user_data[user_id].get("inventory"):
        await interaction.response.send_message("Your inventory is empty!")
        return

    inventory_list = user_data[user_id]["inventory"]

    embed = discord.Embed(
        title=f"{interaction.user.display_name}'s Inventory",
        color=discord.Color.dark_teal()
    )

    for index, item in enumerate(inventory_list, start=1):
        embed.add_field(name=f"{index}. {item}", value="✅ Owned", inline=False)

    embed.set_footer(text=f"Total items: {len(inventory_list)}")
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)

    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "coins": 0, "level": 0, "oc": {}}

    xp_gain = random.randint(5, 15)
    coins_gain = random.randint(1, 3)
    user_data[user_id]["xp"] += xp_gain
    user_data[user_id]["coins"] += coins_gain

    new_level = get_level(user_data[user_id]["xp"])
    if new_level > user_data[user_id]["level"]:
        user_data[user_id]["level"] = new_level
        await message.channel.send(f"🎉 {message.author.mention} leveled up to **Level {new_level}**! PLUS ULTRA!")

    save_data()

bot.run(token, log_handler=handler, log_level=logging.DEBUG)