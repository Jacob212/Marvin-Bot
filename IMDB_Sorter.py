import csv
import os
import time
from operator import itemgetter


def get_time(give_time):
  elapsed_time = time.time() - give_time
  minutes, seconds = divmod(elapsed_time,60)
  hours, minutes = divmod(minutes,60)
  return str(int(hours))+":"+str(int(minutes))+":"+str(round(seconds,2)) 

def menu():
  while True:
    print("======================================================")
    print('Format: # YEAR LANGUAGE')
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
      print("======================================================\n")
      if option == "1":
        movie_file(year)
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

def movie_file(year):
  start_time = time.time()
  basics = open('./basics/data.tsv', mode='r', encoding='utf-8')
  movie = open('./MOVIE'+year+'.tsv', mode='w', encoding='utf-8')

  for rownum, line in enumerate(basics):
    words = line.split("\t")
    if year == "":
      if words[1] == "movie":
        movie.write(line)
    else:
      if words[1] == "movie" and words[5] == year:
        movie.write(line)

  basics.close()
  movie.close()
  print("Finished in "+get_time(start_time))


def tv_file(year="ALL"):
  run_time = time.time()
  start_time = time.time()
  basics = open('./basics/data.tsv', mode='r', encoding='utf-8')
  tv = open('./TV.tsv', mode='w', encoding='utf-8')

  for rownum, line in enumerate(basics):
    words = line.split("\t")
    if year == "ALL":
      if words[1] == "tvSeries":
        tv.write(line)
    else:
      if words[1] == "tvSeries" and words[5] == year:
        tv.write(line)
      
  basics.close()
  tv.close()
  print("step 1 finished in "+get_time(start_time)+" total time: "+get_time(run_time))


  start_time = time.time()
  episodes = open('./episodes/data.tsv', mode='r', encoding='utf-8')
  episodes2 = open('./TEMP.tsv', mode='w', encoding='utf-8')

  for rownum, line in enumerate(episodes):
    words = line.split("\t")
    if not(words[2] == "\\N" or words[3] == "\\N" or words[0] == "tconst"):
      episodes2.write(line)

  episodes.close()
  episodes2.close()

  print("step 2 finished in "+get_time(start_time)+" total time: "+get_time(run_time))

  start_time = time.time()
  episodes = open('./TEMP.tsv', mode='r', encoding='utf-8')
  sortfile = open('./EPISODES.tsv', mode='w', encoding='utf-8')

  csv1 = csv.reader(episodes,delimiter='\t')

  sort = sorted(csv1,key=lambda x:(x[1],int(x[2]),int(x[3])))

  for eachline in sort:
    line = "\t".join(eachline)
    sortfile.write(line)
    sortfile.write("\n")

  episodes.close()
  sortfile.close()

  print("step 2 finished in "+get_time(start_time)+" total time: "+get_time(run_time))

  start_time = time.time()
  episodes = open('./EPISODES.tsv', mode='r', encoding='utf-8')
  numbers = open('./NUMBERS.tsv', mode='w', encoding='utf-8')
  total = []

  for rownum, line in enumerate(episodes):
    words = line.split("\t")
    if total == []:
      total = [words[1]+"\t"+words[2]]
    else:
      if words[1]+"\t"+words[2] in total:
        total.append(words[1]+"\t"+words[2])
      else:
        numbers.write(total[0]+"\t"+str(len(total))+"\n")
        total = [words[1]+"\t"+words[2]]

  episodes.close()
  numbers.close()

  print("step 3 finished in "+get_time(start_time)+" total time: "+get_time(run_time))

  start_time = time.time()

  tv = open('./TV.tsv', mode='r', encoding='utf-8')
  tvnumbers = open('./TV'+year+'.tsv', mode='w', encoding='utf-8')
  if year == "":
    for rownum, line in enumerate(tv):
      line_time = time.time()
      words = line.split("\t")
      numbers = open('./NUMBERS.tsv', mode='r+', encoding='utf-8')
      lines = numbers.readlines()
      numbers.seek(0)
      for line2 in lines:
        words2 = line2.split("\t")
        if words[0] == words2[0]:
          line = line.rstrip("\n")
          tvnumbers.write(line+"\t"+words2[1]+"\t"+words2[2])
        if words2[0] != words[0]:
          numbers.write(line2)
      numbers.truncate()
      numbers.close()
      print(str(rownum)+" finished in "+get_time(line_time)+" total time: "+get_time(run_time))
    tv.close()
    tvnumbers.close()
  else:
    for rownum, line in enumerate(tv):
      line_time = time.time()
      words = line.split("\t")
      numbers = open('./NUMBERS.tsv', mode='r', encoding='utf-8')
      for fornum, line2 in enumerate(numbers):
        words2 = line2.split("\t")
        if words[0] == words2[0]:
          line = line.rstrip("\n")
          tvnumbers.write(line+"\t"+words2[1]+"\t"+words2[2])
      print(str(rownum)+" finished in "+get_time(line_time)+" total time: "+get_time(run_time))
      numbers.close()
    tv.close()
    tvnumbers.close()

  print("step 4 finished in "+get_time(start_time)+" total time: "+get_time(run_time))
  os.remove("TEMP.tsv")
  os.remove("EPISODES.tsv")
  os.remove("NUMBERS.tsv")
  os.remove("TV.tsv")

menu()