#!/usr/bin/env python
from app.importer.Base import Base
from app.models import CustomerAddress as dbCustomerAddress

class CustomerAddress(Base):

    data = None
    json_root = 'addresses'
    customer_id = None

    def __init__(self, customer_id):
        self.customer_id = customer_id

    def save(self, data):
        ids = []
        for address in data:
            id = dbCustomerAddress.upsert(address, self.customer_id)
            ids.append(id)
        return ids


