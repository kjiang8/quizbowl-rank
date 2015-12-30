'''
BACKLOG

automatically get set name (which is in same url as where isStats looks)
pseudynoms - mohan
remove need for housewrites file, cut content by those only with that housewrite to make things more efficient

'''

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
#from builtins import *
from lxml import html
import requests
from scipy import stats
import numpy as np
import json

def getStats(ID): #gets team stats

	allstats = []
	ppb = []
	powers = []
	games = []
	teams = []
	headers = []
	page = 0
	tree = 0
	allteams = 0

	hasStats = isStats(ID)

	if hasStats:

		page = requests.get('http://www.hsquizbowl.org/db/tournaments/'+ str(ID)+'/stats/all_games/')
		tree = html.fromstring(page.content)

		error = tree.xpath('//p/text()')

		if error[0] == 'Report "all_games" does not exist.':
			print('trying combined')
			page = requests.get('http://www.hsquizbowl.org/db/tournaments/'+ str(ID)+'/stats/combined/')
			tree = html.fromstring(page.content)
			error2 = tree.xpath('//p/text()')

			if error2[0] == 'Report "combined" does not exist.':
				print('not combined or all_games')
				report = raw_input("stat report name: ")
				page = requests.get('http://www.hsquizbowl.org/db/tournaments/'+ str(ID)+'/stats/' + str(report)+ '/')
				tree = html.fromstring(page.content)


		allteams =  tree.xpath('//a/text()') #gets everything in <a> tags
		#print(allteams)

		headerIndex = allteams.index("Stat Key") #figures how how many header rows to remove
		#print(headerIndex)

		teams = allteams[headerIndex + 1:] #removes header stuff
		teams = teams[:len(teams)-3] #removes footer stuff

		headers.append(tree.xpath('//b/text()')) #gets table header row

		allstats.append(tree.xpath('//td[@align="RIGHT"]/text()')) #gets all stats


		ppbIndex = headers[0].index("P/B") #gets ppb index
		#print("ppb: ", ppbIndex)

		powersIndex = headers[0].index("15")
		#print("15: ", powersIndex)

		winIndex = headers[0].index("W")
		#print("W: ", winIndex)

		lostIndex = headers[0].index("L")
		#print("L: ",lostIndex)

		tieIndex = headers[0].index("T")
		#print("T: ",tieIndex)

		setName = raw_input("what set is this: ")
		#setName = "IS-148" #laziness is real

		f = open('stats','a') #.txt file with everything

		for i in range(len(teams)):

			try:
				ppb.append(allstats[0][(ppbIndex-1)*i+(ppbIndex-2)]) #gets ppb
				powers.append(allstats[0][(ppbIndex-1)*i+(powersIndex-2)]) #gets powers
				games.append(int(allstats[0][(ppbIndex-1)*i+(winIndex-2)]) + int(allstats[0][(ppbIndex-1)*i+(lostIndex-2)]) + int(allstats[0][(ppbIndex-1)*i+(tieIndex-2)])) #wins + losses + ties = total games played
			except IndexError:
				print('something messed up')

			print(teams[i], ppb[i], powers[i], games[i])
			string = str(teams[i]) + ", " + str(setName) + ", " + str(ppb[i]) + ", " + str(powers[i]) + ', ' + str(games[i])
			
			f.write(string+"\n")

		f.close()

		print("added stats")

	else:
		print("no stats")


def isStats(ID): #checks to see if tournament has stats uplaoded
	
	hasStats = False

	home = requests.get('http://www.hsquizbowl.org/db/tournaments/'+str(ID)+'/')
	tree2 = html.fromstring(home.content)

	reports = tree2.xpath('//ul[@class="Stats NoHeader"]/text()')

	if len(reports) > 0: #there are reports
		hasStats = True

	print("has stats?: ", hasStats)
	return hasStats


def rank(content): #ranks things

	sort = sorted(content, key= lambda x: x[2], reverse=True)

	for i in range(25):
		print(i+1,sort[i][0],sort[i][1],round(sort[i][2],2))

def adjust(housewrite): #adjusts ppb for housewrites

	stdev, mean = getNAQT()
	#print(mean, stdev)

	with open('housewrites') as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	#print(len(content))

	b = []

	for i in range(len(content)):
		if content[i][1].strip() == housewrite:
			b.append(float(content[i][2])) #append float ppb

	z = stats.zscore(b) #finds z-scores

	f = open('appb','a') #.txt file with everything

	for i in range(len(content)):
		try:
			if content[i][1].strip() == housewrite:
				content[i].append(z[i]) #adds z-score to content
				content[i].append(z[i]*stdev + mean) #z-score * naqt stdev + naqt mean to calculate appb
				f.write(content[i][0]+ ", " + content[i][1] + ', ' + str(content[i][6])+"\n")
		except IndexError:
			pass

	#rank(content)

	f.close()

def getNAQT(): #gets stdev, mean from naqt stats

	with open('stats')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	a = []

	for i in range(len(content)):
		if str(content[i][1][:4].strip()) == 'IS-':	
			a.append(float(content[i][2])) #append float ppb

	stdev = np.std(a)
	mean = np.mean(a)

	return(stdev, mean)

def getAPPB(): #ranks appb, but teams are repeated
	with open('appb')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	for i in range(len(content)):
		content[i][2] = float(content[i][2]) #append float ppb

	#print(content)

	rank(content)


def makeDict():
	oldDict = {}
	try:
		oldDict = json.load(open('dict.txt'))
		#print(oldDict)
	except ValueError:
		oldDict = {}
		print('no json')

	with open('appb')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	for i in range(len(content)):
		content[i][2] = float(content[i][2]) #append float ppb
		if content[i][0] in oldDict: #already have a team entry
			oldDict[content[i][0]][content[i][1].strip()] = content[i][2] #adds set name, ppb as entries in dict
		else: #making new key for team
			oldDict[content[i][0]] = {content[i][1].strip(): content[i][2]}

	json.dump(oldDict, open('dict.txt','w'))
	#print(oldDict)
	rankinglist(oldDict)



def sortingDict(d): #sorts all aPPB for each team high to low
	#d = dictionary
	for key in d:
		d[key] = sorted(d[key].values(), reverse=True)
	return d

def rankinglist(d): #takes top 3 appb of each team, averages, prints sorted list
	
	b = []

	sortingDict(d)
	#print(d)

	for key in d:
		if len(d[key]) > 3:
			b.append([key,round(np.mean(d[key][:3]),3)]) #takes top 3 average
		else:
			b.append([key, round(np.mean(d[key]),3)]) #takes average of all

	#print(b)

	sort = sorted(b, key=lambda x: x[1], reverse=True)
	#print(sort)

	for i in range(25):
		print(i+1,sort[i][0],round(sort[i][1],2))

