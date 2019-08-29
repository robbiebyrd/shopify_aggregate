#!/usr/bin/env python
from app.importer.Base import Base
from app.models import Customer as dbCustomer
from app.importer.CustomerAddress import CustomerAddress
from app.utils.logger import Logger

class Customer(Base):
    data = None
    ep = "customers.json?limit=250"
    json_root = "customers"
    paginated = True
    base = None
    shop_id = None
    last_updated = None

    def __init__(self, base, shop_id, last_updated):
        self.base = base
        self.shop_id = shop_id
        self.last_updated = last_updated

    def save(self):
        ids = []
        addresses_count = 0
        for customer in self.data:
            id = dbCustomer.upsert(customer, self.shop_id)
            ids.append(id)
            ca = CustomerAddress(id)
            addresses_count = addresses_count + len(ca.save(customer['addresses']))


        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Customer Addresses" % (addresses_count))
        return ids


