#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderFulfillment as dbOrderFulfillment

class OrderFulfillment(Base):
    data = None
    json_root = 'fulfillments'
    order_id = None

    def __init__(self, order_id):
        self.order_id = order_id

    def save(self, data):
        ids = []
        for fulfillment in data:
            id = dbOrderFulfillment.upsert(fulfillment)
            ids.append(id)

        return ids
