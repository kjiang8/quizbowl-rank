'''
BACKLOG

automatically get set name (which is in same url as where isStats looks)
remove need for housewrites file, cut content by those only with that housewrite to make things more efficient
fix all the manual copy/pasting things

INSTRUCTIONS:
1. add tournament stats to file: run getStats(ID) where ID = 4-digit tournamet ID in url
	1a. manually input set name when prompted
2. look over team names for consistency: run alphabetize()
2a. manually replace pseudonyms, etc
3. if housewrite, copy over statlines to housewrites file
3a. if IS-set, run copyNAQT() to copy naqt statlines to appb
	warning: this will copy all IS-sets, including the ones already in appb, so delete old ones or fix this
4. for each housewrite set, run adjust('NAME OF HOUSEWRITE')
5. once all ppbs are adjusted and transferred to appb file, run makeDict() to show team rankings

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
		g = open('ID','a') #.txt file with tournament IDs

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
		g.write(str(ID)+"\n")

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

def adjust(housewrite): #adjusts ppb for housewrites

	stdev, mean = onlyboth() #use ppbs of only teams that have played both IS-set and housewrite
	#stdev, mean = getNAQT()
	#print(mean, stdev)

	with open('housewrites') as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	#print(len(content))

	b = []

	for i in range(len(content)):
		if content[i][1].strip() == housewrite:
			b.append([content[i][0],content[i][1],float(content[i][2])]) #append float ppb

	c = []
	for i in range(len(b)):
		c.append(b[i][2]) #gets only ppb

	#print("avg ppb " + str(housewrite) + ":",np.mean(c))
	z = stats.zscore(c) #finds z-scores		

	f = open('appb','a') #.txt file with everything

	for i in range(len(b)):
		b[i].append(z[i]) #adds z-score to content
		b[i].append(z[i]*stdev + mean) #z-score * naqt stdev + naqt mean to calculate appb
		#print(b[i][0], b[i][2], b[i][3],b[i][4])
		f.write(b[i][0]+ ", " + b[i][1] + ', ' + str(b[i][4])+"\n")

	f.close()

def getNAQT(): #gets stdev, mean from naqt stats

	with open('stats')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	a = []

	for i in range(len(content)):
		if str(content[i][1][:4].strip()) == 'IS-':	
			a.append(float(content[i][2])) #append float ppb

	#a = sorted(a, reverse=True)
	#a = a[:100]

	stdev = np.std(a)
	mean = np.mean(a)

	#print(stdev,mean)
	return(stdev, mean)


def makeDict(): #makes json, writes to dict.txt file, ranks teams
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
			b.append([key,round(np.mean(d[key][:3]),6)]) #takes top 3 average
		else:
			b.append([key, round(np.mean(d[key]),6)]) #takes average of all

	#print(b)

	sort = sorted(b, key=lambda x: x[1], reverse=True)
	#print(sort)

	for i in range(50):
		print(i+1,sort[i][0],round(sort[i][1],2))

def copyNAQT(): #copies over IS-sets from stats to appb
	with open('stats')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	g = open('appb','a')	

	for i in range(len(content)):
		if str(content[i][1][:4].strip()) == 'IS-':	
			g.write(str(content[i][0]) + ', ' + str(content[i][1]) + ', ' + str(content[i][2]) + '\n' ) 

def alphabetize(): #prints alphabetized list of team names to look over
	with open('stats') as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)
	sorted_content = sorted(content)
	
	for i in range(len(content)):
		print(sorted_content[i][0])


def morlan(x): #does adjustments the morlan way
	with open('stats') as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)
	harvard = {}

	for i in range(len(content)):
		if content[i][1].strip() == x:
			harvard[content[i][0]] = float(content[i][2])

	for key in harvard:
		print(key, harvard[key])
	print(len(harvard))

	isset = {}
	
	with open('naqt') as g:
		naqt = g.read().splitlines()

	naqt = map(lambda x: x.split(','), naqt)

	naqt = [x for y in naqt for x in y]

	#print(naqt)

	for key in harvard:
		try:
			a = naqt.index(key)
			isset[key] = naqt[a+2]
			print(key,naqt[a+2])
		except ValueError:
			#print(key,"has not played an IS-set")
			pass

	print(isset)

	difference = []

	for key in isset:
		difference.append(float(isset[key]) - float(harvard[key]))

	print(difference)
	print(np.mean(difference))

	new = []
	new.append(difference[2])
	new.append(difference[4])
	new.append(difference[5])

	print(np.mean(new))

	i = 0
	print('team', 'is-set ppb','hft ppb','difference')
	for key in isset:
		print(key, isset[key],harvard[key],difference[i])
		i=i+1


def copyNAQT2(): #copies over IS-sets from stats to naqt
	with open('stats')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	g = open('naqt','a')	

	for i in range(len(content)):
		if str(content[i][1][:4].strip()) == 'IS-':	
			g.write(str(content[i][0]) + ', ' + str(content[i][1]) + ', ' + str(content[i][2]) + '\n' ) 


def naqtrank(): #playing around with just naqt is-set ppbs
	oldDict = {}
	with open('naqt')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	for i in range(len(content)):
		content[i][2] = float(content[i][2]) #append float ppb
		if content[i][0] in oldDict: #already have a team entry
			oldDict[content[i][0]][content[i][1].strip()] = content[i][2] #adds set name, ppb as entries in dict
		else: #making new key for team
			oldDict[content[i][0]] = {content[i][1].strip(): content[i][2]}

	#print(oldDict)
	#rankinglist(oldDict)

	sort = sorted(content, key=lambda x: x[2], reverse=True)
	
	for i in range(50):
		print(i+1,sort[i][0], sort[i][2])

def onlytop():
	d = json.load(open('naqtdict'))
	sortingDict(d)
	for key in d:
		d[key] = float(d[key][0])
		print(key,d[key])

	a = []

	for key in d:
		a.append(float(d[key])) #append float ppb


	a = sorted(a, reverse=True)
	a = a[:50]
	print(a)

	stdev = np.std(a)
	mean = np.mean(a)

	#print(stdev,mean)
	return(stdev, mean)

def onlyboth():
	d = json.load(open('naqtdict'))
	sortingDict(d)
	for key in d:
		d[key] = float(d[key][0])
		#print(key,d[key])

	with open('housewrites')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	oldDict = {}

	for i in range(len(content)):
		content[i] = content[i][:3]
		content[i][2] = float(content[i][2]) #append float ppb

		oldDict[content[i][0]] = {content[i][1].strip(): content[i][2]}

	#print(oldDict)

	newDict = {}

	for key in oldDict:
		try:
			if d[key]:
				newDict[key] = d[key]
		except KeyError:
			pass

	#print(newDict,len(newDict))

	a = []

	for key in newDict:
		a.append(float(newDict[key])) #append float ppb

	#a = sorted(a, reverse=True)
	#a = a[:50]
	#print(a)

	stdev = np.std(a)
	mean = np.mean(a)

	#print(stdev,mean)
	return(stdev, mean)




