#!/usr/bin/env python
from app.importer.Base import Base
from app.importer.OrderFulfillment import OrderFulfillment
from app.importer.OrderLineItems import OrderLineItems
from app.importer.OrderRefund import OrderRefund
from app.importer.OrderShippingAddress import OrderShippingAddress
from app.importer.OrderShippingLines import OrderShippingLines
from app.models import Order as dbOrder
from app.utils.logger import Logger

class Order(Base):

    data = None
    ep = 'orders.json?limit=250&status=any'
    json_root = 'orders'
    paginated = True
    base = None
    shop_id = None
    last_updated = None

    def __init__(self, base, shop_id, last_updated):
        self.base         = base
        self.shop_id      = shop_id
        self.last_updated = last_updated
    
    def save(self):
        ids = []
        fulfillment_count = 0
        line_items_count = 0
        shipping_addresses_count = 0
        shipping_lines_count = 0
        refunds_count = 0
        for order in self.data:

            id = dbOrder.upsert(order, self.shop_id)
            ids.append(id)

            of = OrderFulfillment(id)
            fulfillment_count = fulfillment_count + len(of.save(order['fulfillments']))

            oli = OrderLineItems(id)
            line_items_count = line_items_count + len(oli.save(order['line_items']))

            refund = OrderRefund()
            refunds_count = refunds_count + len(refund.save(order['refunds']))

            if 'shipping_address' in order:
                shipping_address = OrderShippingAddress(id)
                shipping_address.save(order['shipping_address'])
                shipping_addresses_count = shipping_addresses_count + 1

            shipping_lines = OrderShippingLines(id)
            shipping_lines_count = shipping_lines_count + len(shipping_lines.save(order['shipping_lines']))

        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Order Fulfillments" % (fulfillment_count))
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Order Line Items" % (line_items_count))
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Order Shipping Addresses" % (shipping_addresses_count))
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Order Shipping Lines" % (shipping_lines_count))
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Order Refunds" % (refunds_count))
        return ids

