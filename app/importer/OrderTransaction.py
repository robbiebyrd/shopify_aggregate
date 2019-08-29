#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderTransaction as dbOrderTransaction
import requests
import simplejson as json

class OrderTransaction(Base):
    
    ids = None
    url = None
    ep = 'orders/%s/transactions.json?limit=250'
    json_root = 'transactions'


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
        for transaction in data:
            id = dbOrderTransaction.upsert(transaction)
            ids.append(id)

        return ids

