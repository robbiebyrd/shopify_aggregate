#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderLineItems as dbOrderLineItems

class OrderLineItems(Base):

    data = None
    order_id = None
    json_root = 'line_items'

    def __init__(self, order_id):
        self.order_id = order_id

    def save(self, data):
        ids = []
        for line_item in data:
            id = dbOrderLineItems.upsert(line_item, self.order_id)
            ids.append(id)

        return ids

