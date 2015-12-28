'''
BACKLOG

identify by column header (ppb, powers, etc) not hardcoding it in [lines 67-68], since some tables are 16 wide and some are 17

automatically remove correct number of header things [line 50], since some are 14 and some 15
	- i think a simple "if int" should show where the headers end and stats start

try "all_games" and "complete" in url, else user input whatever the stats are

automatically get set name (which is in same url as where isStats looks)

pseudynoms - mohan

remove repeats so rank() spits out ranking of teams, not tournaments

suggestions on how to do actual rankings:
	- z-scores / equating ppb and powers - mohan?
	- only take top 3 appb for each team?
	- calculate powers / game, not just straight powers by getting data from win/loss columns in table
    - use machine learning to find out which statistic is the best predictor for final placement at tourneys?????????

'''


from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
#from builtins import *
from lxml import html
import requests

def getStats(ID): #gets team stats

	stats = []
	ppb = []
	powers = []
	teams = []
	page = 0
	tree = 0
	allteams = 0

	hasStats = isStats(ID)

	if hasStats:

		page = requests.get('http://www.hsquizbowl.org/db/tournaments/'+ str(ID)+'/stats/open_combined/')
		tree = html.fromstring(page.content)

		allteams =  tree.xpath('//a/text()') #gets everything in <a> tags
		teams = allteams[14:] #removes header stuff
		teams = teams[:len(teams)-3] #removes footer stuff

		print(teams)

		stats.append(tree.xpath('//td[@align="RIGHT"]/text()')) #gets all stats

		setName = raw_input("what set is this: ")
		#setName = "IS-148" #laziness is real

		f = open('stats','a') #.txt file with everything

		#16 or 17th each, every 8th is powers

		for i in range(len(teams)):
	
			try:
				ppb.append(stats[0][17*i+16]) #gets ppb
				powers.append(stats[0][17*i+7]) #gets powers
			except IndexError:
				pass

			#print(teams[i], ppb[i], powers[i])
			string = str(teams[i]) + ", " + str(setName) + ", " + str(ppb[i]) + ", " + str(powers[i])
			
			f.write(string+"\n")
			
		#print (ppb)
		#print (powers)

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

def rank():

	with open('stats')as f:
		content = f.read().splitlines()

	content = map(lambda x: x.split(','), content)

	for i in range(len(content)):
		content[i][2] = float(content[i][2]) #convert string to float

	#print(content)
	#print(content[0])
	#print(content[0][2])

	sort = sorted(content, key=getKey, reverse=True)


	for i in range(25):
		print(i+1,sort[i][0],sort[i][1],sort[i][2])


def getKey(item):
	return item[2] #sort by ppb

