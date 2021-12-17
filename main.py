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
import requests

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
    db[str(guild.id)] = {"prefix" : "z/", "role": "", "accounts":{}}

@client.event
async def on_message(message):
  #declare database
  global db

  DUMP = True
  if DUMP:
    data2 = {}
    count = 0
    for key in db.keys():
      data2[str(key)] = db[str(key)]
      count += 1

    with open("database.json", 'w') as f:
      json.dump(str(data2), f)

  #write new dict
  WRITE = False
  if WRITE:
    db[str(message.guild.id)] = {"prefix" : "z/", "role": "", "accounts":{}}

  messagecontent = message.content.lower()

  #create new character
  if messagecontent == prefix + "create":
    embed = discord.Embed(color=0xFFFFFF, description="Please enter your character name.")
    embed.set_author(name="📝 | @" + message.author.name)
    sentMessage = await message.channel.send(embed=embed)
    
    #check for msg
    def check(m):
      if m.author == message.author:
        #test and create account for user
        if str(m.author.id) not in db[(str(m.guild.id))]["accounts"].keys():
          print("test")
          db[(str(m.guild.id))]["accounts"][str(m.author.id)] = {}
        if m.content not in db[str(message.guild.id)]["accounts"][str(m.author.id)]:
          print("go")
          return True
    #check if url is valid
    def checkURL(m):
      if m.author == message.author:
        if m.content.lower() == "na":
          return True
        try:
          #test if content is valid picture url
          image_formats = ("image/png", "image/jpeg", "image/jpg")
          r = requests.head(m.content)
          if r.headers["content-type"] in image_formats:
            return True
        except:
          pass
          
    #wait for response message for name
    msg = await client.wait_for('message', check=check)

    #edit embed
    embed = discord.Embed(color=0xFFFFFF, description="Please enter an image URL for your character, or type NA for no image.")
    embed.set_author(name="📝 | @" + message.author.name)
    await sentMessage.edit(embed=embed)
    #image url
    url = await client.wait_for('message', check=checkURL)

    #confirmation message
    embed = discord.Embed(color=0x00FF00, description="Your character, **" + msg.content + "**, was created.")
    embed.set_author(name="@" + message.author.name)
    embed.set_thumbnail(url="" if url.content == "na" else url.content)
    await sentMessage.edit(embed=embed)
    
    #create character
    db[str(message.guild.id)]["accounts"][str(message.author.id)][msg.content] = url.content

  #send message as bot
  if messagecontent.startswith(prefix):
    glist = list(db[str(message.guild.id)]["accounts"][str(message.author.id)].keys())
    gmap = map(lambda x: x.lower(), glist)
    if messagecontent[len(prefix):].startswith(tuple(gmap)):
      count = 0
      for x in glist:
        if messagecontent[len(prefix):].startswith(x.lower()):
          break
        count += 1
      character = glist[count]
  
      embed = discord.Embed(color=0x2C2F33, description=messagecontent[len(prefix)+len(glist[count]):])
      embed.set_author(name=character)
      embed.set_thumbnail(url=db[str(message.guild.id)]["accounts"][str(message.author.id)][glist[count]] if db[str(message.guild.id)]["accounts"][str(message.author.id)][glist[count]] != "na" else "")
      await message.channel.send(embed=embed)

keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot token is in .env file on repl.it, which isn't viewable by data
client.run(os.environ.get("TOKEN"))