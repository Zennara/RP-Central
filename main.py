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
import aiohttp

#api limit checker
r = requests.head(url="https://discord.com/api/v1")
try:
    print(f"Rate limit {int(r.headers['Retry-After']) / 60} minutes left")
except:
    print("No rate limit")

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

#dump data in database.json
DUMP = True
if DUMP:
  data2 = {}
  count = 0
  for key in db.keys():
    data2[str(key)] = db[str(key)]
    count += 1

  with open("database.json", 'w') as f:
    json.dump(str(data2), f)

@client.event
async def on_ready():
  print("\nRP Central Ready\n")
  await client.change_presence(activity=discord.Game(name="a RP experience"))

@client.event
async def on_guild_join(guild):
  if guild.id not in dict(db).keys():
    db[str(guild.id)] = {"prefix" : "z/", "role": "", "accounts":{}}

async def error(message, code):
  embed = discord.Embed(color=0xff0000, description=code)
  await message.channel.send(embed=embed)

@client.event
async def on_message(message):
  #declare database
  global db

  #get prefix
  prefix = db[str(message.guild.id)]["prefix"]

  DUMP = True
  if DUMP:
    data2 = {}
    count = 0
    for key in db.keys():
      data2[str(key)] = db[str(key)]
      count += 1

    with open("database.json", 'w') as f:
      json.dump(str(data2), f)

  messagecontent = message.content.lower()

  print("\n\nCONTENT: " +message.content)
  print("\nMODDEDCONT: " +messagecontent)
  

  
  #write new dict
  if messagecontent == "z/clear":
    db[str(message.guild.id)] = {"prefix" : "z/", "role": "", "accounts":{}}

  #delete character
  if messagecontent.startswith(prefix + "del"):
    print(message.content[len(prefix)+4:])
    if message.content[len(prefix)+4:] in db[str(message.guild.id)]["accounts"][str(message.author.id)]:
      del db[str(message.guild.id)]["accounts"][str(message.author.id)][message.content[len(prefix)+4:]]
      embed = discord.Embed(color=0x00FF00, description = message.author.name+"'s character, **"+message.content[len(prefix)+4:]+"**, was deleted.")
      embed.set_author(name="Character Deletion")
      await message.channel.send(embed=embed)
    else:
      await error(message, "Character does not exist.")
  #change prefix
  if messagecontent.startswith(prefix + "prefix"):
    db[str(message.guild.id)]["prefix"] = messagecontent.split()[1:][0]
    embed = discord.Embed(color=0x00FF00, description ="Prefix is now `" + messagecontent.split()[1:][0] + "`")
    embed.set_author(name="Prefix Change")
    await message.channel.send(embed=embed)


  #help command
  if messagecontent == prefix + "help":
    text= "My prefix is `" + prefix + "`. You can change this at any time with `" + prefix + "prefix`.\n\n`"+prefix+"help` - *Displays this message!*\n`"+prefix+"create` - *Create a new character.*\n`"+prefix+"characters` - *Display your characters.*\n`"+prefix+"<character> [#channel] [message]` - *Send a message as your character.*\n`"+prefix+"del <character>` - *Deletes a character.*"
    embed = discord.Embed(color=0x00FF00, description = text)
    embed.set_author(name="RP Central Help")
    embed.set_footer(text= "________________________\n<> Required | [] Optional\nMade By Zennara#8377")
    await message.channel.send(embed=embed)


  #list your characters
  if messagecontent == prefix + "characters":
    #check if user is in database
    if str(message.author.id) in db[(str(message.guild.id))]["accounts"].keys():
      #check if user has character
      if db[str(message.guild.id)]["accounts"][str(message.author.id)].value!= {}:
        embed = discord.Embed(color=0x00FF00)
        embed.set_author(name=message.author.name + "'s Characters")
        await message.channel.send(embed=embed)
        #loop through characters
        for x in db[(str(message.guild.id))]["accounts"][str(message.author.id)]:
          embed = discord.Embed(color=0xFFFFFF)
          embed.set_author(name=x)
          embed.set_thumbnail(url=db[str(message.guild.id)]["accounts"][str(message.author.id)][x] if db[str(message.guild.id)]["accounts"][str(message.author.id)][x] != "na" else "")
        await message.channel.send(embed=embed)
      else:
        await error(message, message.author.name + " does not have any characters.")
    else:
      await error(message, message.author.name + " does not have any characters.")


  #create new character
  #default var vals
  global attach
  global done
  attach = False
  done = False
  if messagecontent == prefix + "create":
    embed = discord.Embed(color=0xFFFFFF, description="Please enter your character name.\nEnter `cancel` to stop.")
    embed.set_author(name="📝 | @" + message.author.name)
    sentMessage = await message.channel.send(embed=embed)
    #check for msg
    def check(m):
      global done
      #check if done
      if m.content.lower() == "cancel":
        done = True
        return True
      if m.author == message.author:
        #test and create account for user
        if str(m.author.id) not in db[(str(m.guild.id))]["accounts"].keys():
          db[(str(m.guild.id))]["accounts"][str(m.author.id)] = {}
        if m.content not in db[str(message.guild.id)]["accounts"][str(m.author.id)]:
          return True
        else:
          asyncio.create_task(error(m, "Character already exists.")) 
    #check if url is valid
    def checkURL(m):
      global attach
      global done
      if m.content.lower() == "cancel":
        done = True
        return True
      if m.author == message.author:
        if m.content.lower() == "na":
          return True
        if m.content.lower().startswith("http") and m.content.lower().endswith((".png",".jpg",".jpeg")):
          #test if content is valid picture url
          image_formats = ("image/png", "image/jpeg", "image/jpg")
          try:
            r = requests.head(m.content, timeout=3)
          except:
            asyncio.create_task(error(m, "Connection Timeout. Check your URL."))
            return False
          if r.headers["content-type"] in image_formats:
            return True
        else:
          #ensure list contains element
          if m.attachments:
            #get url
            if m.attachments[0].url.lower().startswith("http") and m.attachments[0].url.lower().endswith((".png",".jpeg",".jpg")):
              attach = True
              return True
            else:
              asyncio.create_task(error(m, "Invalid Attachment Type."))   
          else:
            asyncio.create_task(error(m, "Invalid image URL\n`.png`*,* `.jpeg`*, and* `.jpg` *are supported.*"))
    #wait for response message for name
    msg = await client.wait_for('message', check=check)
    #check done
    if done:
      embed = discord.Embed(color=0x00FF00, description="Character creation cancelled.")
      await sentMessage.edit(embed=embed)
      return
    #edit embed
    embed = discord.Embed(color=0xFFFFFF, description="Please enter an image URL for your character, or type `NA` for no image.\nEnter `cancel` to stop.")
    embed.set_author(name="📝 | @" + message.author.name)
    await sentMessage.edit(embed=embed)
    #image url
    url = await client.wait_for('message', check=checkURL)
    #check done
    if done:
      embed = discord.Embed(color=0x00FF00, description="Character creation cancelled.")
      await sentMessage.edit(embed=embed)
      return
    #confirmation message
    embed = discord.Embed(color=0x00FF00, description="Your character, **" + msg.content + "**, was created.")
    embed.set_author(name="@" + message.author.name)
    #get thumbnail url for characters
    if url.content == "na":
      thumb = ""
    elif attach:
      thumb = url.attachments[0].url
    else:
      thumb = url.content
    embed.set_thumbnail(url=thumb)
    await sentMessage.edit(embed=embed)
    #create character
    db[str(message.guild.id)]["accounts"][str(message.author.id)][msg.content] = thumb
  

  #send message as bot
  #default channel
  chnl = message.channel
  chnlCheck = False
  #set error default
  errorCh=False
  #check for prefix
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
      #check if message is channel mention
      if messagecontent[len(prefix)+len(glist[count])+1:].startswith("<#"):
        #check if message is long enough
        if len(messagecontent) >= len(prefix)+len(glist[count])+22:
          #check if there is valid channel
          try:
            chnl = message.guild.get_channel(int(messagecontent[len(prefix)+len(glist[count])+3:len(prefix)+len(glist[count])+21]))
            chnlCheck = True
          except:
            await error(message, "Invalid channel. Please mention the channel.")
            errorCh=True
        else:
          await error(message, "Invalid channel. Please mention the channel.")
          errorCh=True
      #get correct text (remove channel)
      if chnlCheck:
        gtext = message.content[len(prefix)+len(glist[count])+22:]
      else:
        gtext = message.content[len(prefix)+len(glist[count]):]
      #send message
      if not errorCh:
        #get all files
        files = []
        for ach in message.attachments:
          files.append(await ach.to_file())
        #get webhook
        hooks = await chnl.webhooks()
        if hooks:
          webhook = hooks[0]
        else:
          webhook= await chnl.create_webhook(name="RPCentral Required",avatar=None,reason="For the RP Central send msg command.")
        await webhook.send(username=character, avatar_url=db[str(message.guild.id)]["accounts"][str(message.author.id)][glist[count]] if db[str(message.guild.id)]["accounts"][str(message.author.id)][glist[count]] != "na" else "", content=gtext, files=files)
        #delete old message
        await message.delete()     


keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot TOKEN is in secret var on repl.it, which isn't viewable by others
client.run(os.environ.get("TOKEN"))