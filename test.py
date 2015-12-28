from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
#from builtins import *
from lxml import html
import requests

def getStats(ID): #gets team stats

	hasStats = isStats(ID)

	if hasStats:

		page = requests.get('http://www.hsquizbowl.org/db/tournaments/'+ str(ID)+'/stats/all_games/')

		tree = html.fromstring(page.content)

		stats = []
		ppb = []
		powers = []

		allteams =  tree.xpath('//a/text()') #gets everything in <a> tags
		teams = allteams[15:] #removes header stuff
		teams = teams[:len(teams)-3] #removes footer stuff

		stats.append(tree.xpath('//td[@align="RIGHT"]/text()')) #gets all stats

		set = raw_input("what set is this: ")

		f = open('stats','a') #.txt file with everything

		for i in range(len(teams)):
			ppb.append(stats[0][17*i+16]) #gets ppb
			powers.append(stats[0][17*i+7]) #gets powers

			string = str([teams[i], str(set), float(ppb[i]), int(powers[i])])
			
			f.write(string+"\n")
			#print(teams[i], ppb[i], powers[i])


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



