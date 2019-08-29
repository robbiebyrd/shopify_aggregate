#!/usr/bin/env python
from app.importer.Base import Base
from app.models import Shop as dbShop

class Shop(Base):

    data      = None
    ep        = "shop.json"
    json_root = "shop"
    base      = None
    
    def __init__(self, base):
        self.base = base

    def get_id(self):
        return self.data['id']

    def save(self):
        dbShopObj = dbShop()
        return dbShopObj.upsert(self.data)
