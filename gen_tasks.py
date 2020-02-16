#!/usr/bin/python3
import datetime
sd = datetime.date(2019, 9, 30)
ed = datetime.date(2020, 2, 15)
f = open('tasks2.sh', 'w')
for d in [sd + datetime.timedelta(x) for x in range((ed - sd).days + 1)]:
    f.write('/root/scraper/dump_erd.py {}\n'.format(d.strftime('%Y%m%d')))
