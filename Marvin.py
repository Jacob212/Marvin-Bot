from discord import Game
from discord.ext import commands
from discord.utils import get
from itertools import cycle
import asyncio
import sqlite3
import re
import discord
import os

conn = sqlite3.connect('Discord.db')
c = conn.cursor()

f = open("Token.txt","r")#Reads bot taken from text file.
TOKEN = f.read()
f.close()

def new_member(discordID,name):
	c.execute('''INSERT INTO members VALUES(?,?,?)''', (None,discordID,name))
	conn.commit()

def new_Movie(title,season=None,episodes=None):
	c.execute('''INSERT INTO movies VALUES(?,?,?,?,?,?)''', (None,title,season,episodes,None,None))
	conn.commit()

def new_watched(userID,movieID,episode=None):
	c.execute('''INSERT INTO watched VALUES(?,?,?,?)''', (None,userID,movieID,episode))
	conn.commit()

def getIDS(discordID,title,season=None):
	if season == None:
		c.execute('''SELECT Members.UserID, Movies.MovieID FROM Movies,Members WHERE (((Members.[DiscordID])='''+discordID+''') AND ((Movies.[title])='''+title+''') AND ((Movies.[season]) IS NULL));''')
	else:
		c.execute('''SELECT Members.UserID, Movies.MovieID FROM Movies,Members WHERE (((Members.[DiscordID])='''+discordID+''') AND ((Movies.[title])='''+title+''') AND ((Movies.[season])='''+season+'''));''')
	conn.commit()
	b = c.fetchall()
	userID = b[0][0]
	movieID = b[0][1]
	return userID,movieID

def getWatchedID(discordID):
	c.execute('''SELECT Movies.Title, Movies.Season, Watched.Episode FROM Movies INNER JOIN (Members INNER JOIN Watched ON Members.[UserID] = Watched.[UserID]) ON Movies.[MovieID] = Watched.[MovieID] WHERE (((Members.DiscordID)='''+discordID+''')) ORDER BY Movies.Title, Movies.Season;''')
	conn.commit()
	return c.fetchall()

def getWatchedMovie(title,season=None):
	c.execute('''SELECT Members.Username, Watched.Episode FROM Movies INNER JOIN (Members INNER JOIN Watched ON Members.[UserID] = Watched.[UserID]) ON Movies.[MovieID] = Watched.[MovieID] WHERE ((Movies.Title)='''+title+''') AND ((Movies.Season)='''+season+''');''')
	conn.commit()
	return c.fetchall()

def updateWatched(discordID,title,episode=None):
	c.execute('''UPDATE Watched SET Episode = '''+episode+''' WHERE (UserID = (SELECT UserID FROM Members WHERE DiscordID = '''+discordID+''')) AND (MovieID = (SELECT MovieID FROM Movies WHERE Title = '''+title+'''));''')
	conn.commit()

def checkWatched(discordID,title,season=None):#Checks to see if someone has already watched an episode already(False if the have not and True if they have)
	if season == None:
		c.execute('''SELECT Members.DiscordID, Movies.Title, Movies.Season FROM Movies INNER JOIN (Members INNER JOIN Watched ON Members.[UserID] = Watched.[UserID]) ON Movies.[MovieID] = Watched.[MovieID] WHERE (((Members.DiscordID)='''+discordID+''') AND ((Movies.Title)='''+title+''') AND ((Movies.Season) IS NULL));''')
	else:
		c.execute('''SELECT Members.DiscordID, Movies.Title, Movies.Season FROM Movies INNER JOIN (Members INNER JOIN Watched ON Members.[UserID] = Watched.[UserID]) ON Movies.[MovieID] = Watched.[MovieID] WHERE (((Members.DiscordID)='''+discordID+''') AND ((Movies.Title)='''+title+''') AND ((Movies.Season)='''+season+'''));''')
	conn.commit()
	if c.fetchall() == []:
		return False
	else:
		return True

def getMovies():
	c.execute('''SELECT Movies.Title, Movies.Season, Movies.Episodes FROM Movies ORDER BY Movies.Title, Movies.Season;''')
	conn.commit()
	return c.fetchall()

def getLastFive():
	c.execute('''SELECT Title,Season FROM Movies ORDER BY MovieID DESC LIMIT 0,5''')
	conn.commit()
	return c.fetchall()




def is_me(context):
	return context.message.author.id == "130470072190894082"

def getID(discord):
	return re.findall('\d+',discord)[0]

def didReact(users,author):
	for i in range(len(users)):
		if users[i] == author:
			return True
	return False

async def arrowPages(context,movies,msg2=None):
	pages = []
	count = 0
	page = 0
	while count != len(movies):
			page += 1
			message = "Page: "+str(page)+"\n"
			for x in range(0,10):
				episode = movies[count][2]
				season = movies[count][1]
				title = movies[count][0]
				count += 1
				if season == None:
					message = message+"	"+title+"\n"
				else:
					message = message+"	"+title+ " Season: " +str(season)+ " Episode: " +str(episode)+"\n"
				if count == len(movies):
					break
			pages.append(message)
	page = 0
	msg = await client.say(pages[page])
	await client.add_reaction(msg, "◀")
	await client.add_reaction(msg, "▶")
	client.loop.create_task(delete(context,msg,msg2))
	while True:
		res = await client.wait_for_reaction(["▶", "◀"], message=msg,user=context.message.author)
		if res.reaction.emoji == "▶" and page <= (len(pages)-2):
			page += 1
			await client.edit_message(msg,pages[page])
		elif res.reaction.emoji == "◀" and page != 0:
			page -= 1
			await client.edit_message(msg,pages[page])
		await client.remove_reaction(msg, "▶", context.message.author)
		await client.remove_reaction(msg, "◀", context.message.author)

async def change_status():
	await client.wait_until_ready()
	games = getLastFive()
	status = []
	for x in range(0,5):
		if games[x][1] == None:
			status.append(games[x][0])
		else:
			status.append(games[x][0]+" Season "+str(games[x][1]))
	msgs = cycle(status)
	while not client.is_closed:
		await client.change_presence(game=discord.Game(name=next(msgs)))
		await asyncio.sleep(10)

#Sames as delete_after attribute but works for varying times. e.g. timer resets after someone reacts
async def delete(context,msg,header=None):
	count = 0
	while count != 10:
		count += 1
		leftUsers = await client.get_reaction_users(discord.utils.get(client.messages, id=msg.id).reactions[0])
		rightUsers = await client.get_reaction_users(discord.utils.get(client.messages, id=msg.id).reactions[1])
		await asyncio.sleep(1)
		if didReact(leftUsers,context.message.author) == True or didReact(rightUsers,context.message.author) == True:
			count = 0
	await client.delete_message(msg)
	if header != None:
		await client.delete_message(header)

client = commands.Bot(command_prefix="?")

#Sets the played game status and prints that bot is logged in when ready.
@client.event
async def on_ready():
	print('------')
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	#await client.change_presence(game=Game(name="?help"))

#logs when the bot has been invited to a server
@client.event
async def on_server_join(server):
	embed = discord.Embed(title=str(client.user)+" has joined: "+str(server),description="ID: "+str(server.id)+" Owner: "+str(server.owner),color= 16727013)
	embed.set_thumbnail(url=str(server.icon_url))
	await client.send_message(discord.Object(id='538719054479884300'),embed=embed)

#logs when the bot has been kicked from a server
@client.event
async def on_server_remove(server):
	embed = discord.Embed(title=str(client.user)+" has been removed from: "+str(server),description="ID: "+str(server.id)+" Owner: "+str(server.owner),color= 16727013)
	embed.set_thumbnail(url=str(server.icon_url))
	await client.send_message(discord.Object(id="538719054479884300"),embed=embed)

#Catches command errors. (check error)
@client.event
async def on_command_error(error,context):#The check functions for command shutdown failed.
	embed = discord.Embed(title=str(context.message.author)+"			"+str(context.message.content),description=str(error))
	await client.send_message(discord.Object(id="538719054479884300"),embed=embed)
	if error.args[0] == "The check functions for command shutdown failed.":
		msg = await client.send_message(context.message.channel,"You cant access this command."+context.message.author.mention)
	elif error.args[0] == "The check functions for command new failed.":
		msg = await client.send_message(context.message.channel,"You can not add new titles. You must request them to be added. (?request MESSAGE)"+context.message.author.mention)
	else:
		msg = await client.send_message(context.message.channel,"You either dont have access to the command or you have entered something wrong."+context.message.author.mention)
	await asyncio.sleep(10)
	await client.delete_message(msg)

#Adds user to database
@client.command(description="Adds you to bot database. (?add)",brief="Adds you to bot database.",pass_context=True, aliases=["Add"])
async def add(context):
	try:
		new_member(str(context.message.author.id),str(context.message.author))
		await client.say("Added to system, " + context.message.author.mention,delete_after=10)
	except:
		await client.say("You are already added to the system, " + context.message.author.mention,delete_after=10)
	await client.delete_message(context.message)

#User can request for new titles to be added
@client.command(description="Request for a movie/tv to be added. (?request MESSAGE)",brief="Request for a movie/tv to be added.",pass_context=True, aliases=["Request"])
async def request(context, *args):
	message = " ".join(args)
	await client.send_message(discord.Object(id='538720732499410968'),context.message.author.mention+" "+message)
	await client.say("Your request has been logged",delete_after=10)

#Adds new title to database. only works for shows not movies.
@commands.check(is_me)
@client.command(hidden=True,pass_context=True, aliases=["New"])
async def new(context,*args):
	await client.delete_message(context.message)
	try:
		try:
			episodes = args[-1]
			season = args[-2]
			int(episodes)
			title = " ".join(args[0:-2])
			msg = await client.say("Is the following information right? \nTitle = "+title+"\nSeason = "+season+"\nEpisodes = "+episodes+ "\n" + context.message.author.mention)
		except:
			title = " ".join(args)
			msg = await client.say("Is the following information right? \nTitle = "+title+ "\n" + context.message.author.mention)
			episodes = None
			season = None
		await client.add_reaction(msg, '✅')
		await client.add_reaction(msg, '❎')
		while True:
			res = await client.wait_for_reaction(['✅', '❎'], message=msg,user=context.message.author)
			if res.reaction.emoji == "✅":
				new_Movie(title,season,episodes)
				await client.edit_message(msg,"The title has been added to the system "+ context.message.author.mention)
			elif res.reaction.emoji == "❎":
				await client.edit_message(msg,"Plz try again "+ context.message.author.mention)
			else:
				await client.edit_message(msg,"That is not a valid response "+ context.message.author.mention)
			await client.clear_reactions(msg)
			await asyncio.sleep(10)
			await client.delete_message(msg)
			break
	except Exception as e:
		print(e)
		await client.say("The title has already been added or the wrong data was entered, (?new TITLE season# ep#) " + context.message.author.mention,delete_after=10)

#Adds or updates the users watch list in database.
@client.command(description="Use when you want to save what movie or episode you have watched. (?watch TITLE season# episode#)",brief="Use when you want to save what movie or episode you have watched.",pass_context=True, aliases=["Watch"])
async def watch(context,*args):
	await client.delete_message(context.message)
	try:
		episode = args[-1]
		season = args[-2]
		int(season)#checks to see if there is a season and episode number saved. If there isnt then it should be a movie
		int(episode)
		title = " ".join(args[0:-2])
	except:
		title = " ".join(args)
		episode = None
		season = None
	title = "'"+title+"'"
	userID,movieID = getIDS(str(context.message.author.id),title,season)
	if checkWatched(str(context.message.author.id),title,season) == True:
		updateWatched(str(context.message.author.id),title,episode)
	else:
		new_watched(userID,movieID,episode)
	await client.say("Your watched list has been updated "+context.message.author.mention,delete_after=10)

#Gets watched list from database
@client.command(description="Used to check what someone has watched. (?watched or ?watched mention)",brief="Used to check what someone has watched.",pass_context=True, aliases=["Watched"])
async def watched(context, *arg):
	await client.delete_message(context.message)
	try:
		movies = getWatchedID(getID(arg))
		msg2 = await client.say(arg+" has watched:\n")
	except Exception as e:
		print(e)
		movies = getWatchedID(context.message.author.id)
		msg2 = await client.say("You have watched:\n")
	await arrowPages(context,movies,msg2)

#Lists all movie entrys to database.
@client.command(description="Lists all movies/tv in databse. (?list)",brief="Lists all movies/tv in databse.",pass_context=True, aliases=["List"])
async def list(context):
	await client.delete_message(context.message)
	movies = getMovies()
	await arrowPages(context,movies)

#Changes the bot to the maintenance version.
@commands.check(is_me)
@client.command(hidden=True,pass_context=True, aliases=["Switch"])
async def switch(context):
	await client.delete_message(context.message)
	await client.close()
	print("Changing to maintenance version")
	os.system('python Down.py')

#Terminates the bot only if they have the role Owner.
@commands.check(is_me)
@client.command(hidden=True,pass_context=True, aliases=["Shutdown"])
async def shutdown(context):
	await client.delete_message(context.message)
	await client.close()

#Gets the id of emoji.
@commands.check(is_me)
@client.command(hidden=True,pass_context=True)
async def get(context, *args):
	await client.delete_message(context.message)
	print(args)

client.loop.create_task(change_status())
client.run(TOKEN)
c.close()
conn.close()
