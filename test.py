from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
#from builtins import *
from lxml import html
import requests

page = requests.get('http://www.hsquizbowl.org/db/tournaments/3502/stats/combined/')

tree = html.fromstring(page.content)

stats = []
ppb = []

allteams =  tree.xpath('//a/text()') #gets everything in <a> tags
teams = allteams[15:] #gets only team names
teams = teams[:len(teams)-3] #removes footer stuff

stats.append(tree.xpath('//td[@align="RIGHT"]/text()')) #gets all stats


for i in range(len(teams)):
	ppb.append(stats[0][17*i+16]) #gets ppb

	print(teams[i], ppb[i])




