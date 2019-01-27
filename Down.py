from discord import Game
from discord.ext import commands

import asyncio
import discord
import os

f = open("Token.txt","r")
TOKEN = f.read()
f.close()

client = commands.Bot(command_prefix="?")

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
	await client.send_message(context.message.channel,context.message.author.mention+" Sorry, The bot is down for maintenance")

#Changes the bot to the live version.
@commands.has_role("Owner")
@client.command(hidden=True,pass_context=True, aliases=["Start"])
async def start(context):
	await client.close()
	print("Changing to live version")
	os.system('python3 Marvin.py')

#Terminates the bot only if they have the role Owner.
@commands.has_role("Owner")
@client.command(hidden=True,pass_context=True, aliases=["Shutdown"])
async def shutdown(context):
	await client.say("Bye.")
	await client.close()


client.run(TOKEN)