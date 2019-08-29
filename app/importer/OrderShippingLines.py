#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderShippingLines as dbOSL

class OrderShippingLines(Base):
    data = None
    order_id = None

    def __init__(self, order_id):
        self.order_id = order_id

    def save(self, data):
        ids = []
        for shipping_lines in data:
            id = dbOSL.upsert(shipping_lines, self.order_id)
            ids.append(id)
        return ids
