#!/usr/bin/env python
import sys
from app.models import UserShop
import subprocess
from app.utils.logger import Logger
import simplejson as json
import datetime

if __name__ == "__main__":
    run_date = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")

    shops = UserShop.get_all()
    for shop in shops:
        run_id = "%s-%s" % (str(shop.id), run_date)
        path = sys.path[0]
        proc = subprocess.run([''.join([path, '/venv/bin/python3']), ''.join([path, '/importer.py']), str(shop.id), run_id], \
            stdout=subprocess.PIPE, env={'PATH': path})
        print(proc)
        if proc.returncode != 0:
            resp = proc.stdout.decode('utf-8')
            print(resp)
            try:
                respObj = json.loads(resp)
                Logger.error_message(run_id, str(shop.id), respObj['message'])
            except:
                Logger.error_message(run_id, str(shop.id), resp)

    
