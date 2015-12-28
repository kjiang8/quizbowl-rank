from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
from lxml import html
import requests

page = requests.get('http://www.hsquizbowl.org/db/tournaments/3502/stats/combined/')

tree = html.fromstring(page.content)

teams = []
ppb = []

for i in range(11):

	teams.append(tree.xpath('//a[@href="tournaments/3502/stats/combined/teamdetail/#t'+ str(i) + '"]/text()'))
	
ppb.append(tree.xpath('//td[@align="RIGHT"]/text()'))

print(teams)
print(ppb)

#ppb gets everything with <td align=RIGHT> including all stats


