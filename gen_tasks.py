#!/usr/bin/python3
import datetime
sd = datetime.date(2017, 1, 1)
ed = datetime.date(2019, 12, 30)
f = open('tasks.sh', 'w')
for d in [sd + datetime.timedelta(x) for x in range((ed - sd).days + 1)]:
    f.write('/Users/apple/Documents/trading/alpha/scraper/dump_erd.py {}\n'.format(d.strftime('%Y%m%d')))
