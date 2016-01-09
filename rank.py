'''
BACKLOG

automatically get set name (which is in same url as where isStats looks)
clean up code
automatically add entries---write new parser / data input thing 

INSTRUCTIONS:

1a. to manually add tournament stats from individual tournaments:
		i. 	run getStats(ID) where ID = 4-digit tournamet ID in url
		ii. if report is not called "all_games" or "combined", manually input report name when promtped
		iii. manually input set name when prompted

1b. to add tournament stats in bulk:
		i. 	have a .csv file with ID,setName,reportName (if needed)
		ii. run autoget()

2. 	look over team names for consistency: run alphabetize()
		2a. manually replace pseudonyms, etc

3. 	for each housewrite set, run adjust('NAME OF HOUSEWRITE')

4. 	once all ppbs are adjusted and transferred to appb file, run makeDict() to show team rankings
5a. if no new teams are added, run rankinglist()

'''

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
#from builtins import *
from lxml import html
import requests
from scipy import stats
import numpy as np
import json
import matplotlib.pyplot as plt

def getStats(ID,setName,reportName): #gets team stats

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
				report = reportName
				page = requests.get('http://www.hsquizbowl.org/db/tournaments/'+ str(ID)+'/stats/' + str(report)+ '/')
				tree = html.fromstring(page.content)


		allteams =  tree.xpath('//a/text()') #gets everything in <a> tags
		#print(allteams)

		try: 
			headerIndex = allteams.index("Stat Key") #figures how how many header rows to remove
			#print(headerIndex)
		except ValueError: #doesn't have stat key
			headerIndex = allteams.index('Round Report')

		teams = allteams[headerIndex + 1:] #removes header stuff
		teams = teams[:len(teams)-3] #removes footer stuff

		headers.append(tree.xpath('//b/text()')) #gets table header row

		allstats.append(tree.xpath('//td[@align="RIGHT"]/text()')) #gets all stats
		print(allstats)

		ppbIndex = headers[0].index("P/B") #gets ppb index
		print("ppb: ", ppbIndex)

		haspowers = True #flag for powers
		hasbounce = True #flag for bouncebacks

		try:
			powersIndex = headers[0].index("15")
			print("15: ", powersIndex)

			winIndex = headers[0].index("W")
			print("W: ", winIndex)

			lostIndex = headers[0].index("L")
			print("L: ",lostIndex)

			#tieIndex = headers[0].index("T")
			#print("T: ",tieIndex)

		except ValueError: #can't find '15' so set has no powers
			haspowers = False
			print("no powers")

		try:
			bounceIndex = headers[0].index("P/BB")
			print("P/BB: ",bounceIndex)

		except ValueError: #does not have bouncebacks
			hasbounce = False
			print("no bouncebacks")		

		#setName = raw_input("what set is this: ")
		#setName = "IS-148" #laziness is real

		f = open('stats.txt','a') #.txt file with everything
		g = open('ID','a') #.txt file with tournament IDs

		isset = False #flag to see if IS-set

		if str(setName[:3].strip()) == "IS-":
			isset = True
			h = open('appb','a') #open appb to copy over naqt stats

		#print("len(teams):",len(teams))

		for i in range(len(teams)):

			if haspowers:
				#print("has powers")

				if hasbounce:
					#print("has bouncebacks")
					#print("POWERS + BOUNCEBACKS")
					#print("PPB:",(bounceIndex-1)*i+(ppbIndex-2),allstats[0][(bounceIndex-1)*i+(ppbIndex-2)])
					#print("POWERS:",(bounceIndex-1)*i+(powersIndex-2),allstats[0][(bounceIndex-1)*i+(powersIndex-2)])
					#print("WIN:",(bounceIndex-1)*i+(winIndex-2),allstats[0][(bounceIndex-1)*i+(winIndex-2)])
					#print("LOSS:",(bounceIndex-1)*i+(lostIndex-2),allstats[0][(ppbIndex-1)*i+(lostIndex-2)])

					try: 
						ppb.append(allstats[0][(bounceIndex-1)*i+(ppbIndex-2)]) #gets ppb
						powers.append(allstats[0][(bounceIndex-1)*i+(powersIndex-2)]) #gets powers
						games.append(int(allstats[0][(bounceIndex-1)*i+(winIndex-2)]) + int(allstats[0][(bounceIndex-1)*i+(lostIndex-2)])) #wins + losses + ties = total games played
					except ValueError:
						print('something still messed up')

				else:
					#print('powers, no bouncebacks')
					try:
						'''
						print("IN THE RIGHT SPOT")
						print(i)
						ppbIndex = 15
						powerIndex = 6
						print(ppbIndex,powerIndex)
						print("PPB:",(ppbIndex)*i+(ppbIndex-1),allstats[0][(ppbIndex)*i+(ppbIndex-1)])
						print("POWERS:",(ppbIndex)*i+powersIndex-4,allstats[0][(ppbIndex)*i+powersIndex-4])
						print("WIN:",(ppbIndex)*i+(winIndex-2),allstats[0][(ppbIndex)*i+(winIndex-2)])
						print("LOSS:",(ppbIndex)*i+(lostIndex-2),allstats[0][(ppbIndex)*i+(lostIndex-2)])
						
						'''
						ppb.append(allstats[0][(ppbIndex-1)*i+(ppbIndex-2)]) #gets ppb
						powers.append(allstats[0][(ppbIndex-1)*i+(powersIndex-2)]) #gets powers
						games.append(int(allstats[0][(ppbIndex-1)*i+(winIndex-2)]) + int(allstats[0][(ppbIndex-1)*i+(lostIndex-2)])) #wins + losses + ties = total games played
						'''

						#temp code
						ppb.append(allstats[0][(ppbIndex)*i+(ppbIndex-1)]) #gets ppb
						powers.append(allstats[0][(ppbIndex)*i+powersIndex-4]) #gets powers
						games.append(int(allstats[0][(ppbIndex-0)*i+(winIndex-2)]) + int(allstats[0][(ppbIndex-0)*i+(lostIndex-2)])) #wins + losses + ties = total games played
						'''
					except IndexError:
						print('something messed up')

				print(teams[i], ppb[i], powers[i], games[i])
				string = str(teams[i]) + ", " + str(setName) + ", " + str(ppb[i]) + ", " + str(powers[i]) + ', ' + str(games[i])
				
				f.write(string+"\n") #write stats to file

				if isset:
					h.write(str(teams[i]) + ", " + str(setName) + ", " + str(ppb[i])+"\n") #writes to appb file
			
			else: #only writes team name, set, ppb
				#print('no powers')
				if hasbounce:
					#print('has bouncebacks')
					try: 
						ppb.append(allstats[0][(bounceIndex-1)*i+(ppbIndex-2)]) #gets ppb
					except ValueError:
						print('something still messed up')


				else:
					#print('no bouncebacks')
					try:
						ppb.append(allstats[0][(ppbIndex-1)*i+(ppbIndex-2)]) #gets ppb
					except IndexError:
						print('something messed up')

				print(teams[i], ppb[i])
				string = str(teams[i]) + ", " + str(setName) + ", " + str(ppb[i])
				
				f.write(string+"\n") #write stats to file

				if isset:
					h.write(str(teams[i]) + ", " + str(setName) + ", " + str(ppb[i])+"\n") #writes to appb file


		g.write(str(ID)+"\n") #writes ID to file

		f.close()
		g.close()

		if isset:
			h.close()

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

	stdev, mean = both() #use ppbs of only teams that have played both IS-set and housewrite
	#stdev, mean = getNAQT()
	print(mean, stdev)

	with open('stats.txt') as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	#print(len(content))

	b = []


	for i in range(len(content)):
		if content[i][1].strip() == housewrite:
			b.append([content[i][0],content[i][1],float(content[i][2])]) #append float ppb
			#print(content[i][0],content[i][1],float(content[i][2]))

	c = []
	for i in range(len(b)):
		c.append(float(b[i][2])) #gets only ppb

	#print("avg ppb " + str(housewrite) + ":",np.mean(c))
	z = stats.zscore(c) #finds z-scores		

	f = open('appb.txt','a') #.txt file with everything

	for i in range(len(b)):
		b[i].append(z[i]) #adds z-score to content
		b[i].append(z[i]*stdev + mean) #z-score * naqt stdev + naqt mean to calculate appb
		if b[i][4] > 20:
			print(b[i][0], b[i][2], b[i][3],b[i][4])
		
		f.write(b[i][0]+ ", " + b[i][1] + ', ' + str(b[i][4])+"\n")

	f.close()

def makeDict(): #makes json, writes to dict.txt file, ranks teams
	oldDict = {}
	try:
		oldDict = json.load(open('dict.txt'))
		#print(oldDict)
	except ValueError:
		oldDict = {}
		print('no json')

	with open('appb.txt')as f:
		content = f.read().splitlines()

	content = list(map(lambda x: x.split(','), content))

	for i in range(len(content)):
		content[i][2] = float(content[i][2]) #append float ppb
		if content[i][0] in oldDict: #already have a team entry
			oldDict[content[i][0]][content[i][1].strip()] = content[i][2] #adds set name, ppb as entries in dict
		else: #making new key for team
			oldDict[content[i][0]] = {content[i][1].strip(): content[i][2]}

	json.dump(oldDict, open('dict.txt','w'), sort_keys=True, indent=4)
	#print(oldDict)
	rankinglist(oldDict)

def sortingDict(d): #sorts all aPPB for each team high to low
	#d = dictionary
	for key in d:
		d[key] = sorted(d[key].values(), reverse=True)
	return d

def rankinglist(d=None,x=25): #takes top 3 appb of each team, averages, prints sorted list of top x teams, defaults to 25
	
	if d==None:
		d = json.load(open('dict.txt'))

	b = []
	sortingDict(d) #within each team, appbs are high to low
	#print(d)

	for key in d:
		if len(d[key]) > 3:
			b.append([key,round(np.mean(d[key][:3]),6)]) #takes top 3 average
		else:
			b.append([key, round(np.mean(d[key]),6)]) #takes average of all

	#print(b)

	sort = sorted(b, key=lambda x: x[1], reverse=True)
	#print(sort)

	for i in range(x):
		print(i+1,sort[i][0],round(sort[i][1],2))

def alphabetize(): #prints alphabetized list of team names to look over
	with open('stats.txt') as f:
		content = f.read().splitlines()

	content = list(map(lambda x: x.split(','), content))
	sorted_content = sorted(content)

	g = open('names.txt','a')
	
	for i in range(len(content)):
		print(sorted_content[i][0])
		g.write(sorted_content[i][0]+"\n")

def both():
	
	with open('stats.txt')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	naqtdict = {}
	hw = []

	for i in range(len(content)):
		content[i][2] = float(content[i][2])
		if str(content[i][1][:4].strip()) == 'IS-':	#IS-set
			try:	
				if naqtdict[content[i][0]] < content[i][2]: #if new ppb is greater than old ppb
					naqtdict[content[i][0]] = content[i][2] #replace
			
			except KeyError: #team not already in naqt dict
				naqtdict[content[i][0]] = content[i][2]
		else:
			try:
				hw.index(content[i][0])
			except ValueError:
				hw.append(content[i][0])

	#print(naqtdict,hw)
	#print(len(naqtdict),len(hw))

	ppb = []

	for i in range(len(hw)):
		try:
			ppb.append(naqtdict[hw[i]]) #is team listed in naqtdict
		except KeyError:
			pass

	stdev = np.std(ppb)
	mean = np.mean(ppb)

	#print(stdev,mean)
	return(stdev, mean)






##--------------old stuff / playing around with things-----------##

def getNAQT(): #gets stdev, mean from all naqt stats

	with open('stats.txt')as f:
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

def copyNAQT(): #copies over IS-sets from stats to appb
	with open('stats.txt')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	g = open('appb','a')	

	#print(len(content))
	#print(content[len(content)-1][1])
	for i in range(len(content)-1):
		#print(content[i][1][:4])
		if content[i][1][:4].strip() == 'IS-':	
			g.write(str(content[i][0]) + ', ' + str(content[i][1]) + ', ' + str(content[i][2]) + '\n' ) 
			#print("YES")

def copyNAQT2(): #copies over IS-sets from stats to naqt
	with open('stats')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	g = open('naqt','a')	

	for i in range(len(content)):
		if str(content[i][1][:4].strip()) == 'IS-':	
			g.write(str(content[i][0]) + ', ' + str(content[i][1]) + ', ' + str(content[i][2]) + '\n' ) 

def onlytop(): #only looks at best IS-set performance
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

def morlan(x): #does adjustments the morlan way
	with open('stats.txt') as f:
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
	print('team,', 'is-set ppb,','hft ppb,','difference')
	for key in isset:
		print(key, isset[key],harvard[key],difference[i])
		i=i+1


def graph():

	'''
	with open('naqt')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	for i in range(len(content)):
		a.append(float(content[i][2])) #append float ppb
	'''

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

	a = []

	for key in newDict:
		a.append(newDict[key])

	#print(a)

	with open('housewrites')as g:
		hw = g.read().splitlines()

	hw = map(lambda x: x.split(','), hw)

	allhw = [[],[],[],[],[]]

	names = ('bask','cali','umd','hft','limit')

	for i in range(len(hw)):
		
		if str(hw[i][1].strip()) == 'BASK':
			allhw[0].append(float(hw[i][2]))
		elif str(hw[i][1].strip()) == 'CALI':
			allhw[1].append(float(hw[i][2]))
		elif str(hw[i][1].strip()) == 'UMD Fall':
			allhw[2].append(float(hw[i][2]))
		elif str(hw[i][1].strip()) == 'Harvard':
			allhw[3].append(float(hw[i][2]))
		elif str(hw[i][1].strip()) == 'LIMIT':
			allhw[4].append(float(hw[i][2]))

	#print(allhw)

	#print(bask, cali, umd, hft, limit)
	for i in range(len(allhw)):
		plt.subplot(2,3,i+1)
		n, bins, patches = plt.hist(allhw[i], len(allhw[i]), normed=1,facecolor='b',alpha=0.75)
		
		x_axis = np.arange(0,30,1)
		plt.plot(x_axis,stats.norm.pdf(x_axis,np.mean(allhw[i]),np.std(allhw[i])))

		plt.title(names[i])
		plt.axis([0,30,0,0.4])

	plt.subplot(2,3,6)
	n, bins, patches = plt.hist(a, len(a), normed=1, facecolor='b', alpha=0.75)
	plt.title('IS-set ppb')
	#plt.ylabel('some arbitrary thing')
	#plt.title('Distribution of IS-set ppbs')
	
	x_axis = np.arange(0,30,0.01)
	plt.plot(x_axis,stats.norm.pdf(x_axis,np.mean(a),np.std(a)))
	plt.axis([0,30,0,0.3])

	#plt.plot(a,b,'ro')
	plt.show()	


def autoget(): #loops through txt file with ID,set,report_name
	with open('tourneys')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	for i in range(len(content)):
		#print(content[i][0],content[i][1].strip(),"special:",content[i][2],"!")
		#print(content[i][2]=="")
		getStats(content[i][0],content[i][1].strip(),content[i][2])
		print("SUCCESS",i,content[i][0])


def gethwnames():

	with open('stats.txt')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	#g = open('hwnames','a')

	hwnames = []

	for i in range(len(content)):
		
		if str(content[i][1][:4].strip()) != 'IS-':	#not IS-set
			try:
				hwnames.index(content[i][1])
			except ValueError:
				hwnames.append(content[i][1])

	return(hwnames)
	#hwnames = [u' BASK', u' CALI', u' Maryland_Fall', u' HFT', u' LIMIT', u' ACF_Fall', u' VTACO', u' Northmont', u' BISB', u' SSNCT', u' SMART', u' GSAC', u' Missouri_Open']

	#adjust(hwnames[i])



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

	a = []
	for key in newDict:
		a.append(float(newDict[key])) #append float ppb

	#a = sorted(a, reverse=True)
	#a = a[:50]
	#print(a)

	stdev = np.std(a)
	mean = np.mean(a)
	return(stdev, mean)


