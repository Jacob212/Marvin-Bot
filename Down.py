from discord.ext import commands

import asyncio
import discord
import os
import subprocess

f = open("Token.txt","r")
TOKEN = f.read()
f.close()

client = commands.Bot(command_prefix="?")

def is_me(context):
  return context.message.author.id == 130470072190894082

#Sets the played game status and prints that bot is logged in when ready.
@client.event
async def on_ready():
  print('------')
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')
  await client.change_presence(activity=discord.Game(name="Down for maintenance"))

@client.event
async def on_command_error(context,error):
  print(error)
  await context.message.channel.send(context.message.author.mention+" Sorry, The bot is down for maintenance")

#Changes the bot to the live version.
@commands.check(is_me)
@client.command(hidden=True, aliases=["Start"])
async def start(context):
  await context.message.delete()
  await client.close()
  print("Changing to live version")
  os.system("python Marvin.py")

#Pulls latest version from github.
@commands.check(is_me)
@client.command(hidden=True, aliases=["Update"])
async def update(context):
  await context.message.delete()
  returned_value = subprocess.check_output("git pull", shell=True)
  embed = discord.Embed(title="Github Updates",description=f'{returned_value.decode("utf-8")}',color=discord.Colour.green())
  await discord.Object(id=538719054479884300).send(embed=embed)

#Terminates the bot only if they have the role Owner.
@commands.check(is_me)
@client.command(hidden=True,aliases=["Shutdown"])
async def shutdown(context):
  await context.message.delete()
  await client.close()


client.run(TOKEN)