import re
import discord
from discord.ext import commands
from sql import *

class arrowPages():
  def __init__(self,client,context,args):
    self.client = client
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
        display_episode = "Episodes"
        self.movies = getMoviesLikeLimit(self.title,self.titleType,self.genre,self.year,(page-1)*10)
        embed = discord.Embed(title="Listing titles in database",color=self.context.message.author.color.value)
      elif str(self.context.command) == "watched":
        display_episode = "Episode"
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
            message += f'{count}: {movie[1]}\n'
          elif movie[0] == "tvSeries":
            if str(self.context.command) == "watched":
              episodeDisplay = movie[9]
            else:
              episodeDisplay = movie[3]
            message += f'{count}: {movie[1]} Season: {movie[2]} {display_episode}: {episodeDisplay}\n'
          count += 1
        embed.add_field(name=f'Page: {page}',value=message,inline=False)
      else:
        embed.add_field(name=f'Page: {page}',value="There is nothing to display",inline=False)
      try:
        await self.msg.edit(embed=embed)
      except:
        self.msg = await self.context.send(embed=embed)
      await self.msg.add_reaction("◀")
      await self.msg.add_reaction("▶")
      reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: (r.emoji == "▶" or r.emoji == "◀") and u.id == self.context.message.author.id and r.message.id == self.msg.id)
      if reaction.emoji == "▶" and len(self.movies) == 10:
        page += 1
      elif reaction.emoji == "◀" and page != 1:
        page -= 1
      await self.msg.remove_reaction("▶",self.context.message.author)
      await self.msg.remove_reaction("◀",self.context.message.author)

  async def expand(self,index):
    if index <= len(self.movies):
      if self.movies[index][0] == "movie":
        description = "Movie"
      else:
        description = "TV show"
      embed = discord.Embed(title=self.movies[index][1],description=description,url=f'https://www.imdb.com/title/{self.movies[index][4]}/?ref_=fn_al_tt_1',color=self.context.message.author.color.value)
      embed.add_field(name="Original Title",value=self.movies[index][8])
      embed.add_field(name="Release Year",value=self.movies[index][5])
      embed.add_field(name="Run Time",value=self.movies[index][6])
      if self.movies[index][0] == "tvSeries":
        embed.add_field(name="Season",value=self.movies[index][2])
        embed.add_field(name="Episodes",value=self.movies[index][3])
      embed.add_field(name="Genres",value=self.movies[index][7])
    else:
      embed = discord.Embed(title="That is not an option",description="Please go back",color=discord.Colour.dark_red())
    await self.msg.edit(embed=embed)
    await self.msg.remove_reaction("▶",self.client.user)
    while True:
      reaction, user = await self.client.wait_for("reaction_add", check=lambda r, u: r.message==self.msg and r.emoji == "◀" and u.id == self.context.message.author.id and r.message.id == self.msg.id)
      if reaction.emoji == "◀":
        break
      await self.msg.remove_reaction("◀",self.context.message.author)

class generalCommands(commands.Cog):
  def __init__(self,client):
    self.client = client

  #Tells the user where the info about the movies and tv shows are from.
  @commands.command(description="Infomation for where the data is from.",brief="Infomation for where the data is from. :)",aliases=["Info"])
  async def info(self,context):
    await context.message.delete()
    embed = discord.Embed(title="Information courtesy of",description="IMDB\nhttp://www.imdb.com\nUsed with permission",color=context.message.author.color.value)
    await context.send(embed=embed,delete_after=10)   

  #Adds user to database
  @commands.command(description="Adds you to bot database. (?add)",brief="Adds you to bot database.", aliases=["Add"])
  async def add(self,context):
    await context.message.delete()
    try:
      new_member(str(context.message.author.id),str(context.message.author))
      await context.send("Added to system, " + context.message.author.mention,delete_after=10)
    except:
      await context.send("You are already in the system, " + context.message.author.mention,delete_after=10)

  #User can request for new titles to be added
  @commands.command(description="Request for a movie/tv to be added. If the message is more than 256 characters long it will not be logged. (?request MESSAGE)",brief="Request for a movie/tv to be added.", aliases=["Request"])
  async def request(self,context, *args):
    await context.message.delete()
    embed = discord.Embed(title=" ".join(args),description=f'Request logged by {context.message.author.mention}',color=context.message.author.color.value)
    await self.client.get_channel(538720732499410968).send(embed=embed)
    await context.send("Your request has been logged",delete_after=10)

  #Lists all movie entrys to database.
  @commands.command(description="You can sort by year, genre, type(movie or tv) and title. If the title has a year in it, it will sort by that year and might get the title wrong.",brief="Used to sort through everthing in the database", aliases=["List"])
  async def list(self,context, *args):
    await context.message.delete()
    globals()[context.message.author] = arrowPages(self.client,context,args)
    await globals()[context.message.author].display()

  #Gets watched list from database
  @commands.command(description="Used to check what someone has watched. (?watched or ?watched mention)",brief="Used to check what someone has watched.", aliases=["Watched"])
  async def watched(self,context, *args):
    await context.message.delete()
    globals()[context.message.author] = arrowPages(self.client,context,args)
    await globals()[context.message.author].display()

  #Used with list command to get more info on a given movie or tv show.
  @commands.command(description="",brief="",aliases=["Select"])
  async def select(self,context, arg=None):
    await context.message.delete()
    if arg is None:
      await context.send("You have to enter an option to use this command")
    elif arg.isdigit() and context.message.author in globals():
      await globals()[context.message.author].expand(int(arg))
    else:
      await context.send("That is not a valid option")

  #Adds or updates the users watch list in database.
  @commands.command(description="Use when you want to save what movie or episode you have watched. (?watch TITLE season# episode#)",brief="Use when you want to save what movie or episode you have watched.", aliases=["Watch"])
  async def watch(self,context,*args):
    await context.message.delete()
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
    await context.send("Your watched list has been updated "+context.message.author.mention,delete_after=10)

def setup(client):
    client.add_cog(generalCommands(client))