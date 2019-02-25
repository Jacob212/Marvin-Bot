import time
import sqlite3
import re
import gzip
import requests
import os

conn = sqlite3.connect("Discord.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS Movies (movieID INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,titleType TEXT NOT NULL,primaryTitle  TEXT NOT NULL,originalTitle TEXT,season  INTEGER,episodes  INTEGER,releaseYear INTEGER,runtimeMinutes  INTEGER,language  TEXT,genre TEXT,tconst  TEXT NOT NULL, UNIQUE(season,tconst));")
c.execute("CREATE TABLE IF NOT EXISTS Members (userID  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,discordID INTEGER NOT NULL UNIQUE,username  TEXT NOT NULL);")
c.execute("CREATE TABLE IF NOT EXISTS Watched (ID  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,userID  INTEGER,`movieID` INTEGER,episode INTEGER,FOREIGN KEY(movieID) REFERENCES Movies(movieID) ON DELETE SET NULL,FOREIGN KEY(userID) REFERENCES Members(userID) ON DELETE SET NULL);")
conn.commit()

def get_time(give_time):
  elapsed_time = time.time() - give_time
  minutes, seconds = divmod(elapsed_time,60)
  hours, minutes = divmod(minutes,60)
  return f'{int(hours)}:{int(minutes)}:{seconds:.2f}'

def download():
  print("Redownloading source files.")
  url = "https://datasets.imdbws.com/title.basics.tsv.gz"
  req = requests.get(url, stream=True)
  total_size = int(req.headers.get("content-length", 0)); 
  with open("./Datasets/title.basics.tsv.gz", "wb") as f:
    for chunk in req.iter_content(1024): 
      if chunk:
        f.write(chunk)
  url = "https://datasets.imdbws.com/title.akas.tsv.gz"
  req = requests.get(url, stream=True)
  total_size = int(req.headers.get("content-length", 0)); 
  with open("./Datasets/title.akas.tsv.gz", "wb") as f:
    for chunk in req.iter_content(1024): 
      if chunk:
        f.write(chunk)
  url = "https://datasets.imdbws.com/title.episode.tsv.gz"
  req = requests.get(url, stream=True)
  total_size = int(req.headers.get("content-length", 0)); 
  with open("./Datasets/title.episode.tsv.gz", "wb") as f:
    for chunk in req.iter_content(1024): 
      if chunk:
        f.write(chunk)
  print("Finished downloading source files.")

def setup():
  print("Running setup. This could take a minute.")
  start_time = time.time()
  basics = gzip.open("./Datasets/title.basics.tsv.gz", mode="rt", encoding="utf-8")
  basic = basics.readlines()
  basics.close()
  movie = []
  tv = []
  for line in basic:
    line = line.rstrip("\n")
    words = line.split("\t")
    if words[1] == "movie":
      movie.append(words)
    elif words[1] == "tvSeries":
      tv.append(words)

  genres = open("./GENRES.txt", mode="w")
  totalGenres = []
  for line in basic:
    line = line.rstrip("\n")
    words = line.split("\t")
    genresList = words[8].split(",")
    for genre in genresList:
      if genre not in totalGenres and genre != "genres":
        totalGenres.append(genre)
  totalGenres.sort()
  for genre in totalGenres:
    genres.write(genre+"\n")
  genres.close()

  akas = gzip.open("./Datasets/title.akas.tsv.gz", mode="rt", encoding="utf-8")
  sumLanguages = []
  total = None
  languages = []
  countries = []
  for rownum, line in enumerate(akas):
    line = line.rstrip("\n")
    words = line.split("\t")
    if words[0] != "titleId":
      if total == None:
        total = words[0]
        languages = [words[4]]
        countries = [words[3]]
      else:
        if words[0] == total:
          languages.append(words[4])
          countries.append(words[3])
        else:
          sumLanguages.append([total,",".join(countries),",".join(languages)])
          total = words[0]
          languages = [words[4]]
          countries = [words[3]]
  sumLanguages.append([total,",".join(countries),",".join(languages)])
  akas.close()

  allTitles = []
  index = 0
  for words in movie:
    done = 0
    while index < len(sumLanguages):
      words2 = sumLanguages[index]
      index += 1
      if words[0] == words2[0]:
        allTitles.append(words+[words2[1],words2[2],"\\N","\\N"])
        done = 1
        break
      if words2[0] > words[0]:
        index -= 1
        break
    if done == 0:
      allTitles.append(words+["\\N","\\N","\\N","\\N"])

  tvLanguages = []
  index = 0
  for words in tv:
    done = 0
    while index < len(sumLanguages):
      words2 = sumLanguages[index]
      index += 1
      if words[0] == words2[0]:
        tvLanguages.append(words+[words2[1],words2[2]])
        done = 1
        break
      if words2[0] > words[0]:
        index -= 1
        break
    if done == 0:
      tvLanguages.append(words+["None","None"])

  episodes = gzip.open("./Datasets/title.episode.tsv.gz", mode="rt", encoding="utf-8")
  info = []
  for rownum, line in enumerate(episodes):
    line = line.rstrip("\n")
    words = line.split("\t")
    if words[2] != "\\N" and words[3] != "\\N" and words[0] != "tconst":
      info.append(words)
  episodes.close()
  info = sorted(info,key=lambda x:(x[1],int(x[2]),int(x[3])))

  numbers = []
  episodes = []
  tconst = None
  for words in info:
    if tconst == None:
      tconst = words[1]
      episodes = [words[2]]
    else:
      if words[1] == tconst and words[2] in episodes:
        episodes.append(words[2])
      else:
        numbers.append([tconst,episodes[0],len(episodes)])
        tconst = words[1]
        episodes = [words[2]]
  numbers.append([tconst,episodes[0],len(episodes)])

  index = 0
  for words in tvLanguages:
    done = 0
    while index < len(numbers):
      words2 = numbers[index]
      index += 1
      if words[0] == words2[0]:
        allTitles.append(words+[words2[1],words2[2]])
        done = 1
      if words2[0] > words[0]:
        index -= 1
        break
    if done == 0:
      allTitles.append(words+["Unknown","Unknown"])
  print("Finished in "+get_time(start_time))

  print("Importing titles into database")
  imported = 0
  updated = 0
  start_time = time.time()
  tenSeconds = time.time()
  for words in allTitles:
    try:
      c.execute("INSERT INTO Movies VALUES(?,?,?,?,?,?,?,?,?,?,?)", (None,words[1],words[2],words[3],words[11],words[12],words[5],words[7],words[10],words[8],words[0]))
      imported += 1
    except:
      c.execute("UPDATE Movies SET titleType=?,primaryTitle=?,originalTitle=?,season=?,episodes=?,releaseYear=?,runtimeMinutes=?,language=?,genre=? WHERE tconst = ? AND season = ?;",(words[1],words[2],words[3],words[11],words[12],words[5],words[7],words[10],words[8],words[0],words[11]))
      updated += 1
    if (time.time()-tenSeconds) > 10:
      print(f'Imported: {imported} |Updated: {updated} |Total time: {get_time(start_time)}')
      tenSeconds = time.time()
      conn.commit()
  conn.commit()
  print(f'Imported: {imported} |Updated: {updated} |Total time: {get_time(start_time)}')

if os.path.isfile("./Datasets/title.basics.tsv.gz"):
  st=os.stat("./Datasets/title.basics.tsv.gz")
  Age=(time.time()-st.st_mtime)
  if Age > 604800:#Will redownload only if the files are a week old.
    download()
else:
  download()
setup()
c.close()
conn.close()