#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderRisk as dbOrderRisk
import requests
import simplejson as json

class OrderRisk(Base):
    
    ids = None
    url = None
    ep = 'orders/%s/risks.json?limit=250'
    json_root = 'risks'


    def __init__(self, url, ids):
        self.url = url
        self.ids = ids

    def sync(self):
        for id in self.ids:
            res = requests.get("".join([self.url, self.ep % id]))
            obj = json.loads(res.text)
            if self.json_root in obj:
                data = obj[self.json_root]
                return self.save(data)

        return []

    def save(self, data):
        ids = []
        for risk in data:
            id = dbOrderRisk.upsert(risk)
            ids.append(id)

        return ids

