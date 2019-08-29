#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderShippingAddress as dbOSA

class OrderShippingAddress(Base):

    data = None
    order_id = None

    def __init__(self, order_id):
        self.order_id = order_id

    def save(self, data):
        dbOSA.upsert(data, self.order_id)
        return True
        
