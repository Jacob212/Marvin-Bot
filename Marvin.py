from discord import Game
from discord.ext import commands
from discord.utils import get
from itertools import cycle
import asyncio
import sqlite3
import re
import discord
import os
import math

conn = sqlite3.connect("Discord.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS Movies (movieID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,titleType TEXT NOT NULL,primaryTitle  TEXT NOT NULL,originalTitle TEXT,season  INTEGER,episodes  INTEGER,releaseYear INTEGER,runtimeMinutes  INTEGER,language  TEXT,genre TEXT,tconst  TEXT NOT NULL, UNIQUE(season,tconst));")
c.execute("CREATE TABLE IF NOT EXISTS Members (userID  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,discordID INTEGER NOT NULL UNIQUE,username  TEXT NOT NULL);")
c.execute("CREATE TABLE IF NOT EXISTS Watched (ID  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,userID  INTEGER,`movieID` INTEGER,episode INTEGER,FOREIGN KEY(movieID) REFERENCES Movies(movieID) ON DELETE SET NULL,FOREIGN KEY(userID) REFERENCES Members(userID) ON DELETE SET NULL);")
conn.commit()

f = open("Token.txt","r")#Reads bot token from text file.
TOKEN = f.read()
f.close()

f = open("GENRES.txt","r")
genres = f.readlines()
f.close()
allGenres = []
for genre in genres:
  genre = genre.rstrip("\n")
  allGenres.append(genre.lower())

def new_member(discordID,name):
  c.execute("INSERT INTO Members VALUES(?,?,?)", (None,discordID,name))
  conn.commit()

def new_watched(discordID,primaryTitle,season,episode):
  c.execute("INSERT INTO Watched VALUES(?,(SELECT userID FROM Members WHERE discordID = ?),(SELECT movieID FROM Movies WHERE primaryTitle = ? and season = ?),?)", (None,discordID,primaryTitle,season,episode))
  conn.commit()

def getWatchedID(discordID,primaryTitle,titleType,genre,year,offset):
  c.execute("SELECT Movies.titleType, Movies.primaryTitle, Movies.season, Watched.episode, Movies.tconst FROM Movies INNER JOIN (Members INNER JOIN Watched ON Members.[userID] = Watched.[userID]) ON Movies.[movieID] = Watched.[movieID] WHERE (Members.discordID) = ? AND (Movies.primaryTitle) LIKE ? AND (Movies.titleType) LIKE ? AND (Movies.genre) LIKE ? AND (Movies.releaseYear) LIKE ? ORDER BY Movies.primaryTitle, Movies.season LIMIT ?,10;",(discordID,primaryTitle,titleType,genre,year,offset))
  return c.fetchall()

def updateWatched(discordID,primaryTitle,season,episode):
  c.execute("UPDATE Watched SET episode = ? WHERE (UserID = (SELECT UserID FROM Members WHERE DiscordID = ?)) AND (MovieID = (SELECT MovieID FROM Movies WHERE primaryTitle = ? AND season = ?));",(episode,discordID,primaryTitle,season))
  conn.commit()

def checkWatched(discordID,primaryTitle,season):#Checks to see if someone has already watched an episode already(False if the have not and True if they have)
  c.execute("SELECT Members.discordID, Movies.primaryTitle, Movies.season FROM Movies INNER JOIN (Members INNER JOIN Watched ON Members.[UserID] = Watched.[UserID]) ON Movies.[MovieID] = Watched.[MovieID] WHERE (((Members.discordID) = ?) AND ((Movies.primaryTitle)=?) AND ((Movies.season)=?));",(discordID,primaryTitle,season))
  if c.fetchall() == []:
    return False
  else:
    return True

def getMovies():
  c.execute("SELECT Movies.primaryTitle, Movies.season, Movies.episodes FROM Movies ORDER BY Movies.primaryTitle, Movies.season;")
  return c.fetchall()

def getMoviesLike(genre,titleType):
  c.execute("SELECT Movies.titleType, Movies.primaryTitle, Movies.season, Movies.episodes FROM Movies WHERE (Movies.titleType) LIKE ? AND (Movies.genre) LIKE ? ORDER BY Movies.primaryTitle, Movies.season;",(titleType,genre))
  return c.fetchall()

def getMoviesLikeLimit(primaryTitle,titleType,genre,year,offset):
  c.execute("SELECT Movies.titleType, Movies.primaryTitle, Movies.season, Movies.episodes, Movies.tconst, Movies.releaseYear, Movies.runtimeMinutes, Movies.genre, Movies.originalTitle FROM Movies WHERE (Movies.primaryTitle) LIKE ? AND (Movies.titleType) LIKE ? AND (Movies.genre) LIKE ? AND (Movies.releaseYear) LIKE ? ORDER BY Movies.primaryTitle, Movies.season LIMIT ?,10;",(primaryTitle,titleType,genre,year,offset))
  return c.fetchall()

def getLastFive():
  c.execute("SELECT primaryTitle,season FROM Movies ORDER BY movieID DESC LIMIT 0,5")
  return c.fetchall()

def getLength():
  c.execute("SELECT count(*) FROM Movies")
  return c.fetchone()[0]

#checks to see if user is me
def is_me(context):
  return context.message.author.id == "130470072190894082"

class arrowPages():
  def __init__(self,context,args):
    self.context = context
    self.id = None
    self.mention = None
    self.titleType = "%"
    self.title = "%"
    self.genre = "%"
    self.year = "%"
    genres = []
    title = []
    for arg in args:
      if arg.lower() == "tv":
        self.titleType = "tvSeries"
      elif arg.lower() == "movie":
        self.titleType = "movie"
      elif re.match("(<@!?)[0-9]*(>)",arg):
        self.id = re.findall("\d+",arg)[0]
        self.mention = arg
      elif arg in allGenres:
        genres.append(arg)
      elif arg.isdigit() and len(arg) == 4:
        self.year = f'%{arg}%'
      else:
        title.append(arg)
    genres.sort()
    self.title = f'%{" ".join(title)}%'
    self.genre = f'%{"%".join(genres)}%'

  async def display(self,header=None):
    page = 1
    while True:
      if str(self.context.command) == "list":
        self.movies = getMoviesLikeLimit(self.title,self.titleType,self.genre,self.year,(page-1)*10)
        embed = discord.Embed(title="Listing titles in database",color=self.context.message.author.color.value)
      elif str(self.context.command) == "watched":
        if self.id is None:
          self.movies = getWatchedID(self.context.message.author.id,self.title,self.titleType,self.genre,self.year,(page-1)*10)
          embed = discord.Embed(title="Listing titles watched by "+self.context.message.author.display_name,color=self.context.message.author.color.value)
        else:
          member = discord.utils.get(self.context.message.server.members, id=self.id)
          self.movies = getWatchedID(self.id,self.title,self.titleType,self.genre,self.year,(page-1)*10)
          embed = discord.Embed(title="Listing titles watched by "+member.display_name,color=self.context.message.author.color.value)
      message = ""
      count = 0
      if self.movies != []:
        for movie in self.movies:
          if movie[0] == "movie":
            message += str(count)+": "+movie[1]+"\n"
          elif movie[0] == "tvSeries":
            message += str(count)+": "+movie[1]+" Season: "+str(movie[2])+" Episode: "+str(movie[3])+"\n"
          count += 1
        embed.add_field(name="Page: "+str(page),value=message,inline=False)
      else:
        embed.add_field(name="Page: "+str(page),value="There is nothing to display",inline=False)
      try:
        await client.edit_message(self.msg,embed=embed)
      except:
        self.msg = await client.say(embed=embed) 
      await client.add_reaction(self.msg, "◀")
      await client.add_reaction(self.msg, "▶")
      res = await client.wait_for_reaction(["▶", "◀"], message=self.msg,user=self.context.message.author)
      if res.reaction.emoji == "▶" and len(self.movies) == 10:
        page += 1
      elif res.reaction.emoji == "◀" and page != 1:
        page -= 1
      await client.remove_reaction(self.msg, "▶", self.context.message.author)
      await client.remove_reaction(self.msg, "◀", self.context.message.author)

  async def expand(self,index):
    if index <= len(self.movies):
      embed = discord.Embed(title=self.movies[index][1],description=".....",url=f'https://www.imdb.com/title/{self.movies[index][4]}/?ref_=fn_al_tt_1',color=self.context.message.author.color.value)
      embed.add_field(name="Original Title",value=self.movies[index][8])
      embed.add_field(name="Release Year",value=self.movies[index][5])
      embed.add_field(name="Run Time",value=self.movies[index][6])
      embed.add_field(name="Season",value=self.movies[index][2])
      embed.add_field(name="Episodes",value=self.movies[index][3])
      embed.add_field(name="Genres",value=self.movies[index][7])
    else:
      embed = discord.Embed(title="That is not an option",description="Please go back",color=discord.Colour.dark_red())
    await client.edit_message(self.msg,embed=embed)
    await client.remove_reaction(self.msg, "▶", client.user)
    while True:
      res = await client.wait_for_reaction("◀", message=self.msg,user=self.context.message.author)
      if res.reaction.emoji == "◀":
        break
      await client.remove_reaction(self.msg, "◀", self.context.message.author)

#Updates the bots playing status with the last 5 titles that were added to the database
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

client = commands.Bot(command_prefix="?")

#Sets the played game status and prints that bot is logged in when ready.
@client.event
async def on_ready():
  print('------')
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')
  await client.change_presence(game=Game(name="?help"))

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

#Catches command errors. (check error)
@client.event
async def on_command_error(error,context):#The check functions for command shutdown failed.
  print(error)
  if isinstance(error, commands.NoPrivateMessage):
    msg = await client.send_message(context.message.channel, "**private messages.** " + context.message.author.mention)
  if isinstance(error, commands.MissingRequiredArgument):
    msg = await client.send_message(context.message.channel, "**Missing an argument.** " + context.message.author.mention)
  elif isinstance(error, commands.DisabledCommand):
    msg = await client.send_message(context.message.channel, "**Command is disabled.** " + context.message.author.mention)
  elif isinstance(error, commands.CheckFailure):
    msg = await client.send_message(context.message.channel, "**No permission.** " + context.message.author.mention)
  elif isinstance(error, commands.CommandNotFound):
    msg = await client.send_message(context.message.channel, "**Wrong command.** " + context.message.author.mention)
  elif error == "HTTPException: BAD REQUEST (status code: 400)":
    msg = await client.send_message(context.message.channel, "**Too many characters.** " + context.message.author.mention)
  else:
    embed = discord.Embed(title=str(error),description=f'{context.message.author.mention}\n{context.message.content}')
    await client.send_message(discord.Object(id="538719054479884300"),embed=embed)
    msg = await client.send_message(context.message.channel,"You either dont have access to the command or you have entered something wrong."+context.message.author.mention)
  await asyncio.sleep(10)
  await client.delete_message(msg)

#Tells the user where the info about the movies and tv shows are from.
@client.command(description="Infomation for where the data is from.",brief="Infomation for where the data is from. :)",pass_context=True,aliases=["Info"])
async def info(context):
  await client.delete_message(context.message)
  embed = discord.Embed(title="Information courtesy of",description="IMDB\nhttp://www.imdb.com\nUsed with permission",color=context.message.author.color.value)
  await client.say(embed=embed,delete_after=10)   

#Adds user to database
@client.command(description="Adds you to bot database. (?add)",brief="Adds you to bot database.",pass_context=True, aliases=["Add"])
async def add(context):
  await client.delete_message(context.message)
  try:
    new_member(str(context.message.author.id),str(context.message.author))
    await client.say("Added to system, " + context.message.author.mention,delete_after=10)
  except:
    await client.say("You are already in the system, " + context.message.author.mention,delete_after=10)

#User can request for new titles to be added
@client.command(description="Request for a movie/tv to be added. If the message is more than 256 characters long it will not be logged. (?request MESSAGE)",brief="Request for a movie/tv to be added.",pass_context=True, aliases=["Request"])
async def request(context, *args):
  await client.delete_message(context.message)
  embed = discord.Embed(title=" ".join(args),description=f'Request logged by {context.message.author.mention}',color=context.message.author.color.value)
  await client.send_message(discord.Object(id='538720732499410968'),embed=embed)
  await client.say("Your request has been logged",delete_after=10)

#Lists all movie entrys to database.
@client.command(description="You can sort by year, genre, type(movie or tv) and title. If the title has a year in it, it will sort by that year and might get the title wrong.",brief="Used to sort through everthing in the database",pass_context=True, aliases=["List"])
async def list(context, *args):
  await client.delete_message(context.message)
  globals()[context.message.author] = arrowPages(context,args)
  await globals()[context.message.author].display()

#Gets watched list from database
@client.command(description="Used to check what someone has watched. (?watched or ?watched mention)",brief="Used to check what someone has watched.",pass_context=True, aliases=["Watched"])
async def watched(context, *args):
  await client.delete_message(context.message)
  globals()[context.message.author] = arrowPages(context,args)
  await globals()[context.message.author].display()

#Used with list command to get more info on a given movie or tv show.
@client.command(description="",brief="",pass_context=True,aliases=["Select"])
async def select(context, arg=None):
  await client.delete_message(context.message)
  if arg is None:
    await client.say("You have to enter an option to use this command")
  elif arg.isdigit() and context.message.author in globals():
    await globals()[context.message.author].expand(int(arg))
  else:
    await client.say("That is not a valid option")

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
    episode = "\\N"
    season = "\\N"
  if checkWatched(str(context.message.author.id),title,season) == True:
    updateWatched(str(context.message.author.id),title,season,episode)
  else:
    new_watched(str(context.message.author.id),title,season,episode)
  await client.say("Your watched list has been updated "+context.message.author.mention,delete_after=10)


#Changes the bot to the maintenance version.
@commands.check(is_me)
@client.command(hidden=True,pass_context=True, aliases=["Switch"])
async def down(context):
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

#client.loop.create_task(change_status())
client.run(TOKEN)
c.close()
conn.close()
