import os
import json
import asyncio
import aiohttp
import discord
from datetime import datetime, timedelta
from os import listdir
from dotenv import load_dotenv
from discord.ext import commands

# Chargement des variables d'environnement
load_dotenv()

class Echo(commands.Bot):
    def __init__(self):
        self.description = """Echo - An Economy Bot"""
        
        # Correction : Utilisation d'un préfixe simple ou d'une liste
        super().__init__(
            command_prefix=".", 
            intents=discord.Intents.all(),
            description=self.description,
            case_insensitive=True,
        )

    async def setup_hook(self):
        """S'exécute avant que le bot ne se connecte au serveur."""
        # Création de la session HTTP
        self.session = aiohttp.ClientSession()
        
        # Chargement automatique des cogs
        for filename in listdir("./cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"[ Log ] Extension chargée : {filename}")
                except Exception as e:
                    print(f"[ Error ] Impossible de charger {filename} : {e}")
        
        # Chargement de jishaku si installé
        try:
            await self.load_extension("jishaku")
        except Exception:
            pass

    async def on_ready(self):
        cT = datetime.now() + timedelta(hours=5, minutes=30)
        print("-" * 30)
        print(f"[ Log ] {self.user} est prêt !")
        print(f"[ Log ] Heure : {cT.strftime('%H:%M:%S / %d-%m-%Y')}")
        print(f"[ Log ] Latence : {self.latency*1000:.1f} ms")
        print("-" * 30)

# Chargement du marché
try:
    with open("./market.json") as f:
        d2 = json.load(f)
except FileNotFoundError:
    d2 = {}
    print("[ Warning ] market.json non trouvé.")

def market_info():
    return d2

bot = Echo()

@bot.event
async def on_message(message):
    # Important : ignore les bots et traite les commandes
    if message.author.bot:
        return
    await bot.process_commands(message)

# Commandes de gestion des extensions (Owner uniquement)
@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Extension {extension} chargée.")

@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"Extension {extension} déchargée.")

@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Extension {extension} redémarrée.")

async def main():
    token = os.getenv("TOKEN")
    if not token:
        print("Error: Discord token not found in environment variable TOKEN")
        return

    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Arrêt propre en cas de CTRL+C
        print("[ Log ] Arrêt du bot...")
