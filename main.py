#RP Central, written by Zennara#8377

#imports
import keep_alive
import discord
import os
import asyncio
from discord import Embed
from discord import Webhook, AsyncWebhookAdapter
from replit import db

#declare client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
  print("\nRP Central Ready\n")
  await client.change_presence(activity=discord.Game(name="a RP experience"))

prefix = "z/"

@client.event
async def on_guild_join(guild):
  if db[guild.id] not in db.keys():
    db[guild.id] = {"prefix" : "z/", "role": "", "accounts":{}}

@client.event
async def on_message(message):
  messagecontent = message.content.lower()

  if messagecontent == prefix + "create":


keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot token is in .env file on repl.it, which isn't viewable by data
client.run(os.environ.get("TOKEN"))