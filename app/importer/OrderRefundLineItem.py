#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderRefundLineItem as dbOrderRefundLineItem

class OrderRefundLineItem(Base):

    data = None
    json_root = 'refund_line_items'
    refund_id = None

    def __init__(self, refund_id):
        self.refund_id = refund_id

    def save(self, data):
        ids = []
        for refund_li in data:
            id = dbOrderRefundLineItem.upsert(refund_li, self.refund_id)
            ids.append(id)

        return ids

