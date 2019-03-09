from discord import Game
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
  return context.message.author.id == "130470072190894082"

#Sets the played game status and prints that bot is logged in when ready.
@client.event
async def on_ready():
  print('------')
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')
  await client.change_presence(game=Game(name="Down for maintenance"))

@client.event
async def on_command_error(error,context):
  print(error)
  await client.send_message(context.message.channel,context.message.author.mention+" Sorry, The bot is down for maintenance")

#logs when the bot has been invited to a server
@client.event
async def on_server_join(server):
  embed = discord.Embed(title=str(client.user)+" has joined: "+str(server),description="ID: "+str(server.id)+" Owner: "+str(server.owner),color=16727013)
  embed.set_thumbnail(url=str(server.icon_url))
  await client.send_message(discord.Object(id="538719054479884300"),embed=embed)

#logs when the bot has been kicked from a server
@client.event
async def on_server_remove(server):
  embed = discord.Embed(title=str(client.user)+" has been removed from: "+str(server),description="ID: "+str(server.id)+" Owner: "+str(server.owner),color=16727013)
  embed.set_thumbnail(url=str(server.icon_url))
  await client.send_message(discord.Object(id="538719054479884300"),embed=embed)

#Changes the bot to the live version.
@commands.check(is_me)
@client.command(hidden=True,pass_context=True, aliases=["Start"])
async def start(context):
  await client.delete_message(context.message)
  await client.close()
  print("Changing to live version")
  os.system("python Marvin.py")

#Pulls latest version from github.
@commands.check(is_me)
@client.command(hidden=True,pass_context=True, aliases=["Update"])
async def update(context):
  await client.delete_message(context.message)
  returned_value = subprocess.check_output("git pull", shell=True)
  embed = discord.Embed(title="Github Updates",description=f'{returned_value.decode("utf-8")}',color=discord.Colour.green())
  await client.send_message(discord.Object(id="538719054479884300"),embed=embed)

#Terminates the bot only if they have the role Owner.
@commands.check(is_me)
@client.command(hidden=True,pass_context=True,aliases=["Shutdown"])
async def shutdown(context):
  await client.delete_message(context.message)
  await client.close()


client.run(TOKEN)