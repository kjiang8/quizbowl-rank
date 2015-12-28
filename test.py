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

		page = requests.get('http://www.hsquizbowl.org/db/tournaments/'+ str(ID)+'/stats/all_games/')

		tree = html.fromstring(page.content)

		allteams =  tree.xpath('//a/text()') #gets everything in <a> tags
		teams = allteams[15:] #removes header stuff
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

	#content = map(lambda x:x.split(),content)

	#print(len(content))
	#print(content[0])
	#print(content[0][2])
	#print(content)

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

