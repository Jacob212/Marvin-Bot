import csv
import os
import time
import sqlite3
import re
from operator import itemgetter

conn = sqlite3.connect('Discord.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS `Movies` (`movieID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,`titleType` TEXT NOT NULL,`primaryTitle`  TEXT NOT NULL,`originalTitle` TEXT,`season`  INTEGER,`episodes`  INTEGER,`releaseYear` INTEGER,`runtimeMinutes`  INTEGER,`language`  TEXT,`genre` TEXT,`tconst`  TEXT NOT NULL);''')
c.execute('''CREATE TABLE IF NOT EXISTS `Members` (`userID`  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,`discordID` INTEGER NOT NULL UNIQUE,`username`  TEXT NOT NULL);''')
c.execute('''CREATE TABLE IF NOT EXISTS `Watched` (`ID`  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,`userID`  INTEGER,`movieID` INTEGER,`episode` INTEGER,FOREIGN KEY(`movieID`) REFERENCES `Movies`(`movieID`) ON DELETE SET NULL,FOREIGN KEY(`userID`) REFERENCES `Members`(`userID`) ON DELETE SET NULL);''')
conn.commit()

def get_time(give_time):
  elapsed_time = time.time() - give_time
  minutes, seconds = divmod(elapsed_time,60)
  hours, minutes = divmod(minutes,60)
  return str(int(hours))+":"+str(int(minutes))+":"+str(round(seconds,2)) 

def setup():
  if os.path.isfile('./IMDBSorted/allMovies.tsv') and os.path.isfile('./IMDBSorted/allTV.tsv'):
    menu()
  else:
    print("Sorting movies and tv series")
    start_time = time.time()
    basics = open("./basics/data.tsv", mode="r", encoding="utf-8")
    movie = []
    tv = []
    for rownum, line in enumerate(basics):
      line = line.rstrip("\n")
      words = line.split("\t")
      if words[1] == "movie":
        movie.append(line)
      elif words[1] == "tvSeries":
        tv.append(line)
    basics.close()
    print("Finished in "+get_time(start_time))

    print("summing languages")
    start_time = time.time()
    akas = open("./akas/data.tsv", mode="r", encoding="utf-8")
    sumLanguages = []
    total = []
    languages = []
    countries = []
    for rownum, line in enumerate(akas):
      line = line.rstrip("\n")
      words = line.split("\t")
      if words[0] != "titleId":
        if total == []:
          total = [words[0]]
          languages = [words[4]]
          countries = [words[3]]
        else:
          if words[0] == total[0]:
            languages.append(words[4])
            countries.append(words[3])
          else:
            sumLanguages.append(total[0]+"\t"+",".join(countries)+"\t"+",".join(languages))
            total = [words[0]]
            languages = [words[4]]
            countries = [words[3]]
    sumLanguages.append(total[0]+"\t"+",".join(countries)+"\t"+",".join(languages))
    akas.close()
    print("Finished in "+get_time(start_time))

    print("adding languages to movies")
    start_time = time.time()
    short = open("./IMDBSorted/allMovies.tsv", mode="w", encoding="utf-8")
    index = 0
    for line in movie:
      line = line.rstrip("\n")
      words = line.split("\t")
      done = 0
      while index < len(sumLanguages):
        line2 = sumLanguages[index].rstrip("\n")
        index += 1
        words2 = line2.split("\t")
        if words[0] == words2[0]:
          short.write(line+"\t"+words2[1]+"\t"+words2[2]+"\tNone\tNone\n")
          done = 1
          break
        if words2[0] > words[0]:
          index -= 1
          break
      if done == 0:
        short.write(line+"\tNone\tNone\tNone\tNone\n")
    short.close()
    print("Finished in "+get_time(start_time))

    print("adding languages to tv")
    start_time = time.time()
    tvLanguages = []
    index = 0
    for line in tv:
      line = line.rstrip("\n")
      words = line.split("\t")
      done = 0
      while index < len(sumLanguages):
        line2 = sumLanguages[index].rstrip("\n")
        index += 1
        words2 = line2.split("\t")
        if words[0] == words2[0]:
          tvLanguages.append(line+"\t"+words2[1]+"\t"+words2[2]+"\n")
          done = 1
          break
        if words2[0] > words[0]:
          index -= 1
          break
      if done == 0:
        tvLanguages.append(line+"\tNone\tNone\n")
    print("Finished in "+get_time(start_time))

    print("Splitting lines with season and episode numbers up from the ones without.")
    start_time = time.time()
    episodes = open("./episodes/data.tsv", mode="r", encoding="utf-8")
    info = []
    noInfo = []
    for rownum, line in enumerate(episodes):
      line = line.rstrip("\n")
      words = line.split("\t")
      if not(words[2] == "\\N" or words[3] == "\\N" or words[0] == "tconst"):
        info.append(words)
      elif not(words[0] == "tconst"):
        noInfo.append(words)
    episodes.close()
    info = sorted(info,key=lambda x:(x[1],int(x[2]),int(x[3])))
    print("Finished in "+get_time(start_time))

    print("Adding up total episodes in each season.")
    start_time = time.time()
    numbers = []
    total = []
    for line in info:
      if total == []:
        total = [line[1]+"\t"+line[2]]
      else:
        if line[1]+"\t"+line[2] in total:
          total.append(line[1]+"\t"+line[2])
        else:
          numbers.append(total[0]+"\t"+str(len(total)))
          total = [line[1]+"\t"+line[2]]
    numbers.append(total[0]+"\t"+str(len(total)))
    print("Finished in "+get_time(start_time))

    print("Adding season and episode numbers to all the other info.")
    start_time = time.time()
    short = open("./IMDBSorted/allTV.tsv", mode="w", encoding="utf-8")
    index = 0
    for line in tvLanguages:
      line = line.rstrip("\n")
      words = line.split("\t")
      done = 0
      while index < len(numbers):
        words2 = numbers[index].split("\t")
        index += 1
        if words[0] == words2[0]:
          short.write(line+"\t"+words2[1]+"\t"+words2[2]+"\n")
          done = 1
        if words2[0] > words[0]:
          index -= 1
          break
      if done == 0:
        short.write(line+"\tNone\tNone\n")
    short.close()
    print("Finished in "+get_time(start_time))
    menu()

def menu():
  while True:
    print("="*50)
    print("1: Search movies")
    print("2: Search tv")
    print("3: List all years")
    print("4: List all genres")
    print("5: List all languages")
    print("6: List all countries")
    print("7: Import menu")
    print("8: Exit")
    option = input("Enter one of the options above: ")
    if option == "1" or option == "2":
      print("="*50)
      year = input("Enter a year(Leave blank if none): ")
      genre = input("Enter a genre(Leave blank if none): ")
      language = input("Enter a language(Leave blank if none): ").lower()
      country = input("Enter a country(Leave blank if none): ").lower()
      if option == "1":
        searchFile(year,language,country,genre,"allMovies")
      elif option == "2":
        searchFile(year,language,country,genre,"allTV")
    elif option == "3":
      years()
    elif option == "4":
      genres()
    elif option == "5":
      languages()
    elif option == "6":
      countries()
    elif option == "7":
      importMenu()
    elif option == "8":
      break
    else:
      print("Invalid option. please try again")

def importMenu():
  while True:
    listOfFiles = os.listdir('./IMDBSorted/Sorted')
    files = []
    count = 0
    print("="*50)
    print("Enter the number for the file you want to select")
    for file in listOfFiles:
      if re.search(".tsv",file):
        files.append(file)
        print(str(count)+": "+file)
        count += 1
    print(str(count)+": Back")
    option = input("Enter one of the options above: ")
    if option == str(count):
      break
    else:
      try:
        importFile(listOfFiles[int(option)])
      except Exception as e:
        print(e)
        print("Invalid option. please try again")

def importFile(file):
  print("Importing titles into database")
  imported = 0
  notImported = 0
  start_time = time.time()
  tenSeconds = time.time()
  importFile = open("./IMDBSorted/Sorted/"+file, mode="r", encoding="utf-8")
  for rownum, line in enumerate(importFile):
    line = line.rstrip("\n")
    words = line.split("\t")
    tconst = words[0]
    titleType = words[1]
    primaryTitle = words[2]
    originalTitle = words[3]
    releaseYear = words[5]
    if words[7] == "\\N":
      runtimeMinutes = None
    else:
      runtimeMinutes = words[7]
    if words[8] == "\\N":
      genres = None
    else:
      genres = words[8]
    countries = words[9]
    languages = words[10]
    if words[12] == "None":
      episodes = None
    else:
      episodes = words[12]
    if words[12] == "None":
      season = None
      c.execute('''SELECT Movies.primaryTitle FROM Movies WHERE primaryTitle = "'''+primaryTitle+'''" AND season is null ORDER BY Movies.primaryTitle, Movies.season;''')
      conn.commit()
    else:
      season = words[11]
      c.execute('''SELECT Movies.primaryTitle FROM Movies WHERE primaryTitle = "'''+primaryTitle+'''" AND season = "'''+str(season)+'''" ORDER BY Movies.primaryTitle, Movies.season;''')
      conn.commit()
    result = c.fetchall()
    if result == []:
      c.execute('''INSERT INTO Movies VALUES(?,?,?,?,?,?,?,?,?,?,?)''', (None,titleType,primaryTitle,originalTitle,season,episodes,releaseYear,runtimeMinutes,languages,genres,tconst))
      conn.commit()
      imported += 1
    else:
      notImported += 1
    if (time.time()-tenSeconds) > 10:
      print("Imported: "+str(imported)+"| Already in database: "+str(notImported)+"| Total time: "+get_time(start_time))
      tenSeconds = time.time()
  importFile.close()
  print("Imported: "+str(imported)+"| Already in database: "+str(notImported)+"| Total time: "+get_time(start_time)+"\nFinshed")

def searchFile(year,language,country,genre,file):
  print("Searching file for given options")
  start_time = time.time()
  inFile = open("./IMDBSorted/"+file+".tsv", mode="r", encoding="utf-8")
  outFile = open("./IMDBSorted/Sorted/"+file+year+language+country+genre+".tsv", mode="w", encoding="utf-8")
  for rownum, line in enumerate(inFile):
    words = line.split("\t")
    if re.search(year,words[5]) and re.search(country,words[9].lower()) and re.search(language,words[10]) and re.search(genre,words[8].lower()):
      outFile.write(line)
  outFile.close()
  inFile.close()
  print("Finished in "+get_time(start_time))

def years():
  start_time = time.time()
  basics = open('./basics/data.tsv', mode='r', encoding='utf-8')
  years = open('./IMDBSorted/YEARS.tsv', mode='w', encoding='utf-8')
  totalYears = []
  yearsNone = None
  for rownum, line in enumerate(basics):
    line = line.rstrip("\n")
    words = line.split("\t")
    if not(words[5] in totalYears) and words[5] != "startYear" and words[5] != "\\N":
      totalYears.append(words[5])
    elif words[5] == "\\N":
      yearsNone = words[5]
  for year in sorted(totalYears, key=lambda x:int(x),reverse=True):
    years.write(year+"\n")
    print(year)
  years.write(yearsNone+"\n")
  print(yearsNone)
  years.close()
  basics.close()
  print("\nFinished in "+get_time(start_time)+"\n")

def genres():
  start_time = time.time()
  basics = open('./basics/data.tsv', mode='r', encoding='utf-8')
  genres = open('./IMDBSorted/GENRES.tsv', mode='w', encoding='utf-8')
  totalGenres = {}
  for rownum, line in enumerate(basics):
    line = line.rstrip("\n")
    words = line.split("\t")
    genresList = words[8].split(",")
    for genre in genresList:
      if genre in totalGenres and genre != "genres":
        totalGenres[genre] += 1
      elif genre != "genres":
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
  languages = open('./IMDBSorted/LANGUAGES.tsv', mode='w', encoding='utf-8')
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

def countries():
  start_time = time.time()
  akas = open('./akas/data.tsv', mode='r', encoding='utf-8')
  countries = open('./IMDBSorted/REGIONS.tsv', mode='w', encoding='utf-8')
  totalCountries = {}
  for rownum, line in enumerate(akas):
    line = line.rstrip("\n")
    words = line.split("\t")
    countriesList = words[3].split(",")
    for country in countriesList:
      if country == "region":
        pass
      elif country in totalCountries:
        totalCountries[country] += 1
      else:
        totalCountries[country] = 1
  for k, v in sorted(totalCountries.items(), key = itemgetter(1),reverse=True):
    countries.write(k+"\t"+str(v)+"\n")
    print(k+": "+str(v))
  akas.close()
  countries.close()
  print("\nFinished in "+get_time(start_time)+"\n")

setup()
c.close()
conn.close()