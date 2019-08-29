#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderRefundTransaction as dbOrderRefundTransaction

class OrderRefundTransaction(Base):

    data = None
    json_root = 'order_refund_transaction'
    refund_id = None

    def __init__(self, refund_id):
        self.refund_id = refund_id

    def save(self, data):
        ids = []
        for transaction in data:
            id = dbOrderRefundTransaction.upsert(transaction, self.refund_id)
            ids.append(id)
        return ids

