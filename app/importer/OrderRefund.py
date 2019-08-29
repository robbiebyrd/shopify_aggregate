#!/usr/bin/env python
from app.importer.Base import Base
from app.models import OrderRefund as dbOrderRefund
from app.importer.OrderRefundLineItem import OrderRefundLineItem
from app.importer.OrderRefundTransaction import OrderRefundTransaction
from app.utils.logger import Logger

class OrderRefund(Base):

    data = None
    json_root = 'refunds'

    def save(self, data):
        ids = []
        refund_lis_count = 0
        refund_trans_count = 0
        for refund in data:
            id = dbOrderRefund.upsert(refund)
            ids.append(id)

            refund_li = OrderRefundLineItem(id)
            refund_lis_count = refund_lis_count + len(refund_li.save(refund['refund_line_items']))

            refund_trans = OrderRefundTransaction(id)
            refund_trans_count = refund_trans_count + len(refund_trans.save(refund['transactions']))
            
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Order Refund Line Items" % (refund_lis_count))
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Order Refund Transactions" % (refund_lis_count))

        return ids
