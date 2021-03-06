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
import random

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
  if random.randint(1,4) == 1:
    embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
  await message.channel.send(embed=embed)

#check for reaction
  #reaction def
async def removeR(reaction, user):
  await reaction.remove(user)
def checkReact(reaction, user):
  return not user.bot
def betterCheckReact(reaction, user, message):
  if str(reaction.emoji) in ("◀️","🏷️","🖼️"):
    if reaction.message == message:
      asyncio.create_task(removeR(reaction, user))
      return True

#check for msg
def check(m):
  return not m.author.bot
#used because check cant pass variables
def betterCheck(m, message):
  #get prefix
  prefix = db[str(m.guild.id)]["prefix"]
  #check if done or cancel
  if m.content.lower() == "cancel" or m.content.lower().startswith(prefix):
    return True
  #test and create account for user
  if str(m.author.id) not in db[(str(m.guild.id))]["accounts"].keys():
    db[(str(m.guild.id))]["accounts"][str(m.author.id)] = {}
  if m.content not in db[str(m.guild.id)]["accounts"][str(m.author.id)]:
    if len(m.content) < 81 and len(m.content) > 1:
      return True
    else:
      asyncio.create_task(error(m, "Character name must be between **1** and **80**."))
  else:
    asyncio.create_task(error(m, "Character already exists.")) 

#check if url is valid
def checkURL(m):
  return not m.author.bot
#used because check cant pass variables
def betterCheckURL(m, message, attachments):
  #get prefix
  prefix = db[str(m.guild.id)]["prefix"]
  if m.content.lower() == "cancel" or m.content.lower().startswith(prefix) or m.content.lower() == "na":
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
    if attachments:
      #get url
      if attachments[0].url.lower().startswith("http") and attachments[0].url.lower().endswith((".png",".jpeg",".jpg")):
        return True
      else:
        asyncio.create_task(error(m, "Invalid Attachment Type."))   
    else:
      asyncio.create_task(error(m, "Invalid image URL\n`.png`*,* `.jpeg`*, and* `.jpg` *are supported.*"))

#check if player has role
def checkRole(message):
  if db[str(message.guild.id)]["role"] == "":
    return True
  else:
    if message.guild.get_role(int(db[str(message.guild.id)]["role"])) in message.author.roles:
      return True

#check if member has proper permissions
def checkPerms(message):
  if message.author.guild_permissions.manage_webhooks:
    return True
  else:
    asyncio.create_task(error(message, "You do not have the valid permission: `Manage Webhooks`."))

@client.event
async def on_message(message):
  #declare database
  global db

  monetize = random.randint(1,4) == 1

  #check for bots
  if message.author.bot:
    return

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

  #print("\n\nCONTENT: " +message.content)
  #print("\nMODDEDCONT: " +messagecontent)

  #role
  if messagecontent.startswith(prefix+"role"):
    if checkPerms(message):
      msgcontent = messagecontent.replace('<','').replace('>','').replace('@','').replace('&','')
      #check to only display
      if messagecontent == prefix+"role":
        if db[str(message.guild.id)]["role"] == "":
          text = "Anyone can create characters and perform RP commands."
        else:
          text = "The role required to create characters and perform RP commands is "+message.guild.get_role(int(db[str(message.guild.id)]["role"])).mention
        embed = discord.Embed(color=0x00FF00, description = text)
        await message.channel.send(embed=embed)
        return
      try:
        if message.guild.get_role(int(msgcontent[len(prefix)+5:])):
          db[str(message.guild.id)]["role"] = msgcontent[len(prefix)+5:]
          text = "Role required for commands and characters is now "+message.guild.get_role(int(msgcontent[len(prefix)+5:])).mention+"."
        elif msgcontent[len(prefix)+5:] == "0":
          db[str(message.guild.id)]["role"] = ""
          text = "Anyone can now create characters and perform RP commands."
        else:
          await error(message, "Invalid role mention or ID.")
          return
        embed = discord.Embed(color=0x00FF00, description = text)
        if monetize:
          embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
        await message.channel.send(embed=embed)
      except:
        await error(message, "Invalid role mention or ID.")


  #edit character
  if messagecontent.startswith(prefix + "edit"):
    if checkRole(message):
      if message.content[len(prefix)+5:] in db[str(message.guild.id)]["accounts"][str(message.author.id)]:
        #get character from list
        glist =  list(db[str(message.guild.id)]["accounts"][str(message.author.id)].keys())
        count = 0
        for x in glist:
          if message.content[len(prefix)+5:].startswith(x):
            break
          count += 1
        character =glist[count]
        embed2 = discord.Embed(color=0xFFFFFF, description="React for that edit or ◀️ to finish.\n\n:label: | **Character Name**\n:frame_photo: | **Profile Picture**")
        embed2.set_author(name="|  " + character, icon_url= db[str(message.guild.id)]["accounts"][str(message.author.id)][str(character)])
        if monetize:
          embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
        sentMessage = await message.channel.send(embed=embed2)
        #add reactions
        await sentMessage.add_reaction('◀️')
        await sentMessage.add_reaction('🏷️')
        await sentMessage.add_reaction('🖼️')
        while True:
          #define starting embed
          embed2 = discord.Embed(color=0xFFFFFF, description="React for that edit or ◀️ to finish.\n\n:label: | **Character Name**\n:frame_photo: | **Profile Picture**")
          embed2.set_author(name="|  " + character, icon_url= db[str(message.guild.id)]["accounts"][str(message.author.id)][str(character)])
          if monetize:
            embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
          await sentMessage.edit(embed=embed2)
          try:
            while True:
              reaction, user = await client.wait_for('reaction_add', check=checkReact, timeout=30.0)
              if user.id == message.author.id:
                if betterCheckReact(reaction, user, sentMessage):
                  break
          except asyncio.TimeoutError:
            embed = discord.Embed(color=0xff0000, description="TImed out. Interactive messages time out after `30` seconds.")
            if monetize:
              embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
            await sentMessage.edit(embed=embed)
            await sentMessage.clear_reactions()
            return
          else:
            #seperate emojis
            if str(reaction.emoji) == "🏷️":
              embed = discord.Embed(color=0xFFFFFF, description="Please enter your new character name.\nEnter `cancel` to go back.")
              embed.set_author(name="|  " + character, icon_url= db[str(message.guild.id)]["accounts"][str(message.author.id)][str(character)])
              if monetize:
                embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
              await sentMessage.edit(embed=embed)
              try:
                while True:
                  done = False
                  msg = await client.wait_for('message', check=check, timeout=30.0)
                  #check for author and guild
                  if msg.author == message.author and msg.guild == message.guild:
                    if msg.content.lower() == "cancel" or msg.content.lower().startswith(prefix):
                      done = True
                      break
                    if betterCheck(msg, message):
                      break
                if done:
                  continue
              except asyncio.TimeoutError:
                embed = discord.Embed(color=0xff0000, description="TImed out. Interactive messages time out after `30` seconds.")
                if monetize:
                  embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
                await sentMessage.edit(embed=embed)
                await sentMessage.clear_reactions()
                return
              else:
                #remake key
                db[str(message.guild.id)]["accounts"][str(message.author.id)][msg.content] = db[str(message.guild.id)]["accounts"][str(message.author.id)][character]
                del db[str(message.guild.id)]["accounts"][str(message.author.id)][character]
                character = msg.content
                #confirmation message
                embed = discord.Embed(color=0x00FF00, description="Your characters name was changed to **" + msg.content + "**.")
                embed.set_author(name="@" + message.author.name)
                if monetize:
                  embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
                await message.channel.send(embed=embed)
            elif str(reaction.emoji) == "🖼️":
              embed = discord.Embed(color=0xFFFFFF, description="Please enter a new image URL for your character, or type `NA` for no image.\nEnter `cancel` to go back.")
              embed.set_author(name="|  " + character, icon_url= db[str(message.guild.id)]["accounts"][str(message.author.id)][str(character)])
              await sentMessage.edit(embed=embed)
              try:
                while True:
                  done = False
                  url = await client.wait_for('message', check=checkURL, timeout=30.0)
                  #check author and guild
                  if url.author == message.author and url.guild == message.guild:
                    if url.content.lower() == "cancel" or url.content.lower().startswith(prefix) or url.content.lower() == "na":
                      done = True
                      break
                    if betterCheckURL(url, message, url.attachments):
                      break
                if done and not url.content.lower() == "na":
                  continue
              except asyncio.TimeoutError:
                embed = discord.Embed(color=0xff0000, description="TImed out. Interactive messages time out after `30` seconds.")
                if monetize:
                  embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
                await sentMessage.edit(embed=embed)
                await sentMessage.clear_reactions()
                return
              else:
                #get thumbnail url for characters
                if url.content.lower() == "na":
                  thumb = ""
                else:
                  if url.attachments:
                  #get url
                    if url.attachments[0].url.lower().startswith("http") and url.attachments[0].url.lower().endswith((".png",".jpeg",".jpg")):
                      thumb = url.attachments[0].url
                    else:
                      thumb = url.content
                  else:
                    thumb = url.content
                #remake key
                db[str(message.guild.id)]["accounts"][str(message.author.id)][character] = thumb
                #confirmation message
                embed = discord.Embed(color=0x00FF00, description="Your character, **"+character+"'s** image was set to:")
                embed.set_author(name="@" + message.author.name)
                embed.set_thumbnail(url=thumb)
                if monetize:
                  embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
                await message.channel.send(embed=embed)
            elif str(reaction.emoji) == "◀️":
              await sentMessage.clear_reactions()
              embed = discord.Embed(color=0x00FF00, description = "Editing Complete")
              if monetize:
                embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
              await sentMessage.edit(embed=embed)
              return
            continue
        else:
          await error(message, "Account does not exist.")
    else:
      await error(message, "You do not have the proper role.")
  
  
  #write new dict
  if messagecontent == "z/clear":
    if checkPerms(message):
      db[str(message.guild.id)] = {"prefix" : "z/", "role": "", "accounts":{}}

  #delete character
  if messagecontent.startswith(prefix + "del"):
    if checkRole(message):
      if message.content[len(prefix)+4:] in db[str(message.guild.id)]["accounts"][str(message.author.id)]:
        del db[str(message.guild.id)]["accounts"][str(message.author.id)][message.content[len(prefix)+4:]]
        embed = discord.Embed(color=0x00FF00, description = message.author.name+"'s character, **"+message.content[len(prefix)+4:]+"**, was deleted.")
        embed.set_author(name="Character Deletion")
        if monetize:
          embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
        await message.channel.send(embed=embed)
      else:
        await error(message, "Character does not exist.")
    else:
      await error(message, "You do not have the proper role.")

        
  #change prefix
  if messagecontent.startswith(prefix + "prefix"):
    if checkPerms(message):
      if not any(x in messagecontent for x in ["_","~","*","`","<",">","@","&"]):
        if len(messagecontent) <= len(prefix) + 10:
          db[str(message.guild.id)]["prefix"] = message.content.lower().split()[1:][0]
          embed = discord.Embed(color=0x00FF00, description ="Prefix is now `" + message.content.split()[1:][0] + "`")
          embed.set_author(name="Prefix Change")
          if monetize:
            embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
          await message.channel.send(embed=embed)
        else:
          await error(message, "Prefix must be between `1` and `3` characters.")
      else:
        await error(message, "Prefix can not contain `` ` `` , `_` , `~` , `*` , `<` , `>` , `@` , `&`")


  #help command
  if messagecontent == prefix + "help":
    text= "My prefix is `" + prefix + "`. You can change this at any time with `" + prefix + "prefix`.\n\n`"+prefix+"help` - *Displays this message!*\n`"+prefix+"create` - *Create a new character.*\n`"+prefix+"characters` - *Display your characters.*\n`"+prefix+"<character> [#channel] [message]` - *Send a message as your character.*\n`"+prefix+"del <character>` - *Deletes a character.*\n`"+prefix+"edit <character>` - *Edit your character*\n`"+prefix+"role [newRole]` - *Changes the role required for commands. Enter 0 for everyone.*"
    embed = discord.Embed(color=0x00FF00, description = text)
    embed.set_author(name="RP Central Help")
    embed.set_footer(text= "________________________\n<> Required | [] Optional\nMade By Zennara#8377")
    embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
    await message.channel.send(embed=embed)


  #list your characters
  if messagecontent == prefix + "characters":
    if checkRole(message):
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
            if monetize:
              embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
            await message.channel.send(embed=embed)
        else:
          await error(message, message.author.name + " does not have any characters.")
      else:
        await error(message, message.author.name + " does not have any characters.")
    else:
      await error(message, "You do not have the proper role.")


  #create new character
  #default var vals
  if messagecontent == prefix + "create":
    if checkRole(message):
      embed = discord.Embed(color=0xFFFFFF, description="Please enter your character name.\nEnter `cancel` to stop.")
      embed.set_author(name="📝 | @" + message.author.name)
      if monetize:
        embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
      sentMessage = await message.channel.send(embed=embed)
      #wait for response message for name
      try:
        while True:
          msg = await client.wait_for('message', check=check, timeout=30.0)
          #check for guild and author
          if msg.author == message.author and msg.guild == message.guild:
            if msg.content.lower() == "cancel" or msg.content.lower().startswith(prefix):
              embed = discord.Embed(color=0x00FF00, description="Character creation cancelled.")
              if monetize:
                embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
              await sentMessage.edit(embed=embed)
              return
            if betterCheck(msg, message):
              break
      except asyncio.TimeoutError:
        embed = discord.Embed(color=0xff0000, description="TImed out. Interactive messages time out after `30` seconds.")
        if monetize:
          embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
        await sentMessage.edit(embed=embed)
      else:
        #edit embed
        embed = discord.Embed(color=0xFFFFFF, description="Please enter an image URL for your character, or type `NA` for no image.\nEnter `cancel` to stop.")
        embed.set_author(name="📝 | @" + message.author.name)
        if monetize:
          embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
        await sentMessage.edit(embed=embed)
        #image url
        try:
          while True:
            url = await client.wait_for('message', check=checkURL, timeout=30.0)
            #check for guild and author
            if url.author == message.author and url.guild == message.guild:
              #check for no image
              if url.content.lower() == "na":
                break
              #check if done
              if url.content.lower() == "cancel" or url.content.lower().startswith(prefix):
                embed = discord.Embed(color=0x00FF00, description="Character creation cancelled.")
                if monetize:
                  embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
                await sentMessage.edit(embed=embed)
                return
              if betterCheckURL(url, message, url.attachments):
                break
        except asyncio.TimeoutError:
          embed = discord.Embed(color=0xff0000, description="TImed out. Interactive messages time out after `30` seconds.")
          if monetize:
            embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
          await sentMessage.edit(embed=embed)
          return
        else:
          #confirmation message
          embed = discord.Embed(color=0x00FF00, description="Your character, **" + msg.content + "**, was created.")
          embed.set_author(name="@" + message.author.name)
          #get thumbnail url for characters
          if url.content.lower() == "na":
            thumb = ""
          else:
            if url.attachments:
            #get url
              if url.attachments[0].url.lower().startswith("http") and url.attachments[0].url.lower().endswith((".png",".jpeg",".jpg")):
                thumb = url.attachments[0].url
              else:
                thumb = url.content
            else:
              thumb = url.content
          embed.set_thumbnail(url=thumb)
          if monetize:
            embed.add_field(name="᲼",value="\n:smile: Enjoy free hosting? Consider [donating](https://www.paypal.me/keaganlandfried)")
          await sentMessage.edit(embed=embed)
          #create character
          db[str(message.guild.id)]["accounts"][str(message.author.id)][msg.content] = thumb
    else:
      await error(message, "You do not have the proper role.")
  

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
      if checkRole(message):
        #get character from list
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
          hookFind = False
          if hooks:
            x=0
            for hook in hooks:
              if hook.token != None:
                webhook = hooks[x]
                hookFind = True
                break
              x += 1
          if not hookFind:
            webhook= await chnl.create_webhook(name="RPCentral Required",avatar=None,reason="For the RP Central send msg command.")
          await webhook.send(username=character, avatar_url=db[str(message.guild.id)]["accounts"][str(message.author.id)][glist[count]] if db[str(message.guild.id)]["accounts"][str(message.author.id)][glist[count]] != "na" else "", content=gtext, files=files)
          #delete old message
          await message.delete()
      else:
        await error(message, "You do not have the proper role.")


keep_alive.keep_alive() 
#keep the bot running after the window closes, use UptimeRobot to ping the website at least every <60min. to prevent the website from going to sleep, turning off the bot

#run bot
#Bot TOKEN is in secret var on repl.it, which isn't viewable by others
client.run(os.environ.get("TOKEN"))