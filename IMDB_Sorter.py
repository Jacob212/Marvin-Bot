import csv
import os
import time
import sqlite3
import re
from operator import itemgetter

conn = sqlite3.connect('Discord.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS `Movies` (`movieID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,`titleType` TEXT NOT NULL,`primaryTitle`  TEXT NOT NULL,`originalTitle` TEXT NOT NULL,`season`  INTEGER,`episodes`  INTEGER,`releaseYear` INTEGER NOT NULL,`runtimeMinutes`  INTEGER,`language`  TEXT,`genre` TEXT,`tconst`  TEXT NOT NULL);''')
c.execute('''CREATE TABLE IF NOT EXISTS `Members` (`userID`  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,`discordID` INTEGER NOT NULL UNIQUE,`username`  TEXT NOT NULL);''')
c.execute('''CREATE TABLE IF NOT EXISTS `Watched` (`ID`  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,`userID`  INTEGER,`movieID` INTEGER,`episode` INTEGER,FOREIGN KEY(`movieID`) REFERENCES `Movies`(`movieID`) ON DELETE SET NULL,FOREIGN KEY(`userID`) REFERENCES `Members`(`userID`) ON DELETE SET NULL);''')
conn.commit()

def get_time(give_time):
  elapsed_time = time.time() - give_time
  minutes, seconds = divmod(elapsed_time,60)
  hours, minutes = divmod(minutes,60)
  return f'{int(hours)}:{int(minutes)}:{seconds:.2f}'

def menu():
  while True:
    print("======================================================")
    print("1: Movie file")
    print("2: TV file")
    print("3: List all genres")
    print("4: List all languages")
    print("5: List all regions")
    print("6: Import all Movie files")
    print("7: Import all TV files")
    print("8: Exit")
    option = input("Enter one of the options above: ")
    if option == "1" or option == "2":
      year = input("Enter the year you want: ")
      language = input("Enter the language you want: ")
      region = input("Enter the region you want: ")
      print("======================================================\n")
      if option == "1":
        movie_file(year,language,region)
      else:
        tv_file(year)
    elif option == "3":
      print("======================================================\n")
      genres()
    elif option == "4":
      print("======================================================\n")
      languages()
    elif option == "5":
      print("======================================================\n")
      regions()
    elif option == "6":
      print("======================================================\n")
      importMovies()
    elif option == "7":
      print("======================================================\n")
      importTV()
    elif option == "8":
      break
    else:
      print("plz pick again")

def genres():
  start_time = time.time()
  basics = open('./basics/data.tsv', mode='r', encoding='utf-8')
  genres = open('./GENRES.tsv', mode='w', encoding='utf-8')
  totalGenres = {}
  for rownum, line in enumerate(basics):
    line = line.rstrip("\n")
    words = line.split("\t")
    genresList = words[8].split(",")
    for genre in genresList:
      if genre == "genres":
        pass
      elif genre in totalGenres:
        totalGenres[genre] += 1
      else:
        totalGenres[genre] = 1
  for k, v in sorted(totalGenres.items(), key = itemgetter(1),reverse=True):
    genres.write(k+"\t"+str(v)+"\n")
    print(k+": "+str(v))
  genres.close()
  basics.close()
  print("\nFinished in "+get_time(start_time)+"\n")

def languages():
  start_time = time.time()
  akas = open('./akas/data.tsv', mode='r', encoding='utf-8')
  languages = open('./LANGUAGES.tsv', mode='w', encoding='utf-8')
  totalLanguages = {}
  for rownum, line in enumerate(akas):
    line = line.rstrip("\n")
    words = line.split("\t")
    languagesList = words[4].split(",")
    for language in languagesList:
      if language == "language":
        pass
      elif language in totalLanguages:
        totalLanguages[language] += 1
      else:
        totalLanguages[language] = 1
  for k, v in sorted(totalLanguages.items(), key = itemgetter(1),reverse=True):
    languages.write(k+"\t"+str(v)+"\n")
    print(k+": "+str(v))
  akas.close()
  languages.close()
  print("\nFinished in "+get_time(start_time)+"\n")

def regions():
  start_time = time.time()
  akas = open('./akas/data.tsv', mode='r', encoding='utf-8')
  regions = open('./REGIONS.tsv', mode='w', encoding='utf-8')
  totalRegions = {}
  for rownum, line in enumerate(akas):
    line = line.rstrip("\n")
    words = line.split("\t")
    regionsList = words[3].split(",")
    for region in regionsList:
      if region == "region":
        pass
      elif region in totalRegions:
        totalRegions[region] += 1
      else:
        totalRegions[region] = 1
  for k, v in sorted(totalRegions.items(), key = itemgetter(1),reverse=True):
    regions.write(k+"\t"+str(v)+"\n")
    print(k+": "+str(v))
  akas.close()
  regions.close()
  print("\nFinished in "+get_time(start_time)+"\n")

def sortByRegionAndLanguage(language,region):
  start_time = time.time()
  akas = open('./akas/data.tsv', mode='r', encoding='utf-8')
  sortedList = []
  for rownum, line in enumerate(akas):
    line = line.rstrip("\n")
    words = line.split("\t")
    if words[3] == region and words[4] == language:
      sortedList.append(line)
    elif words[4] == language and region == "":
      sortedList.append(line)
    elif words[3] == region and language == "":
      sortedList.append(line)
  akas.close()
  print(len(sortedList))
  print("Sorting by language and/or region finished in "+get_time(start_time))
  return sortedList

def movie_file(year,language,region):
  start_time = time.time()
  basics = open('./basics/data.tsv', mode='r', encoding='utf-8')
  movies = []
  for rownum, line in enumerate(basics):
    words = line.split("\t")
    if words[1] == "movie":
      movies.append(line)
  basics.close()
  partTwoTime = time.time()
  movie = open('./MOVIE'+year+language+region+'.tsv', mode='w', encoding='utf-8')
  regionAndLanguageList = sortByRegionAndLanguage(language,region)
  count = 0
  for line in movies:
    count += 1
    line = line.rstrip("\n")
    words = line.split("\t")
    if (time.time()-partTwoTime) > 10:
      print("Number of movies checked: "+str(count)+" Total time: "+get_time(start_time))
      partTwoTime = time.time()
    formatLine = "MovieID\t"+words[1]+"\t"+words[2]+"\t"+words[3]+"\t"+"none"+"\t"+"none"+"\t"+words[5]+"\t"+words[7]+"\t"+words[8]+"\t"+words[0]+"\n"
    if language != "" or region != "":
      for line2 in regionAndLanguageList:
        words2 = line2.split("\t")
        if words[5] == year and words[0] == words2[0]:
          movie.write(formatLine)
          regionAndLanguageList.remove(line2)
          break
    elif words[5] == year:
      movie.write(formatLine)
    elif year == "":
      movie.write(formatLine)
  print(count)
  movie.close()
  print("Finished in "+get_time(start_time))

def tv_file(year="ALL"):
  run_time = time.time()
  start_time = time.time()
  basics = open('./basics/data.tsv', mode='r', encoding='utf-8')
  tv = []
  for rownum, line in enumerate(basics):
    line = line.rstrip("\n")
    words = line.split("\t")
    if year == "":
      if words[1] == "tvSeries":
        tv.append(line)
    else:
      if words[1] == "tvSeries" and words[5] == year:
        tv.append(line)
  basics.close()
  print("step 1 finished in "+get_time(start_time)+" total time: "+get_time(run_time))

  
  start_time = time.time()
  episodes = open('./episodes/data.tsv', mode='r', encoding='utf-8')
  episodes2 = []
  for rownum, line in enumerate(episodes):
    line = line.rstrip("\n")
    words = line.split("\t")
    if not(words[2] == "\\N" or words[3] == "\\N" or words[0] == "tconst"):
      episodes2.append(words)
  episodes.close()
  print("step 2 finished in "+get_time(start_time)+" total time: "+get_time(run_time))
  start_time = time.time()
  sortfile = []
  sort = sorted(episodes2,key=lambda x:(x[1],int(x[2]),int(x[3])))
  for eachline in sort:
    line = "\t".join(eachline)
    sortfile.append(line)
  print("step 3 finished in "+get_time(start_time)+" total time: "+get_time(run_time))
  start_time = time.time()
  numbers = []
  total = []
  for line in sortfile:
    words = line.split("\t")
    if total == []:
      total = [words[1]+"\t"+words[2]]
    else:
      if words[1]+"\t"+words[2] in total:
        total.append(words[1]+"\t"+words[2])
      else:
        numbers.append(total[0]+"\t"+str(len(total)))
        total = [words[1]+"\t"+words[2]]
  print("step 4 finished in "+get_time(start_time)+" total time: "+get_time(run_time))
  start_time = time.time()
  partTwoTime = time.time()
  tvnumbers = open('./TV'+year+'.tsv', mode='w', encoding='utf-8')
  count = 0
  for line in tv:
    count += 1
    line_time = time.time()
    words = line.split("\t")
    for line2 in numbers:
      words2 = line2.split("\t")
      if words[0] == words2[0]:
        tvnumbers.write(line+"\t"+words2[1]+"\t"+words2[2]+"\n")
        numbers.remove(line2)
    if (time.time()-partTwoTime) > 10:
      print("Number of tv shows checked: "+str(count)+" Total time: "+get_time(start_time))
      partTwoTime = time.time()
  tvnumbers.close()
  print("step 5 finished in "+get_time(start_time)+" total time: "+get_time(run_time))

def importMovies():
  movies = open('./MOVIE.tsv', mode='r', encoding='utf-8')
  for rownum, line in enumerate(movies):
    words = line.split("\t")
    final = []
    for word in words:
      print(word)
      if word == "\\N":
        final.append(None)
      else:
        final.append(word)
    primaryTitle = " ".join(re.findall('\w+',final[2]))
    originalTitle = " ".join(re.findall('\w+',final[3]))
    genres = None
    if final[8] != None:
      genres = "\t".join(re.findall('[\w-]+',final[8]))
    c.execute('''SELECT Movies.primaryTitle FROM Movies WHERE primaryTitle = "'''+primaryTitle+'''" ORDER BY Movies.primaryTitle, Movies.Season;''')
    conn.commit()
    result = c.fetchall()
    if result == []:
      c.execute('''INSERT INTO movies VALUES(?,?,?,?,?,?,?,?,?,?)''', (None,final[1],primaryTitle,originalTitle,None,None,final[6],final[7],genres,final[9]))
      conn.commit()
  movies.close()

def importTV():
  tv = open('./TV.tsv', mode='r', encoding='utf-8')
  for rownum, line in enumerate(tv):
    words = line.split("\t")
    title = " ".join(re.findall('\w+',words[2]))
    genres = "\t".join(re.findall('[\w-]+',words[8]))
    if genres == "N":
      genres = None
    c.execute('''SELECT Movies.Title FROM Movies WHERE Title = "'''+title+'''" ORDER BY Movies.Title, Movies.Season;''')
    conn.commit()
    result = c.fetchall()
    if result == []:
      c.execute('''INSERT INTO movies VALUES(?,?,?,?,?,?)''', (None,title,None,None,None,genres))
      conn.commit()
  tv.close()






menu()
c.close()
conn.close()