#RP Central, written by Zennara#8377
#https://discord.com/api/oauth2/authorize?client_id=919791828289601540&permissions=8&scope=bot

#imports
import keep_alive
import discord
import os
import asyncio
from discord import Embed
from discord import Webhook, AsyncWebhookAdapter
from replit import db
import json

#declare client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

#delete database
CLEAR = False
if CLEAR:
  count = 0
  for key in db.keys():
    del db[key]
    count += 1
    print(count)

#dump data in database.json
DUMP = True
if DUMP:
  data2 = {}
  count = 0
  for key in db.keys():
    data2[str(key)] = db[str(key)]
    count += 1
    print(str(count))

  with open("database.json", 'w') as f:
    json.dump(str(data2), f)

@client.event
async def on_ready():
  print("\nRP Central Ready\n")
  await client.change_presence(activity=discord.Game(name="a RP experience"))

prefix = "z/"

@client.event
async def on_guild_join(guild):
  if guild.id not in dict(db).keys():
    db[guild.id] = {"prefix" : "z/", "role": "", "accounts":{}}

@client.event
async def on_message(message):
  #declare database
  global db
  data = dict(db)

  messagecontent = message.content.lower()

  #create new character
  if messagecontent == prefix + "create":
    embed = discord.Embed(color=0x593695, description=message.author.name + ", please enter your character name.")
    embed.set_author(name="📝 | @" + client.user.name)
    await message.channel.send(embed=embed)

    def check(m):
      if m.author == message.author:
        if m.content not in data[message.guild.id]:
          return True
          print("go")

    msg = await client.wait_for('message', check=check)

  #remake database
  db = data



keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot token is in .env file on repl.it, which isn't viewable by data
client.run(os.environ.get("TOKEN"))