#!/usr/bin/python3
import datetime
sd = datetime.date(2019, 5, 1)
ed = datetime.date(2020, 2, 11)
f = open('tasks.sh', 'w')
for d in [sd + datetime.timedelta(x) for x in range((ed - sd).days + 1)]:
#    f.write('/root/scraper/dump_erd.py {}\n'.format(d.strftime('%Y%m%d')))
    f.write('/Users/apple/Documents/trading/stock/it_prod/ccass/alpha.q -dt {}\n'.format(d.strftime('%Y%m%d')))
