#!/usr/bin/env python
from app.models import UserShop
from app.importer.Order import Order
from app.importer.OrderRisk import OrderRisk
from app.importer.OrderTransaction import OrderTransaction
from app.importer.Customer import Customer
from app.importer.Product import Product
from app.importer.ShippingZone import ShippingZone
from app.importer.Shop import Shop
from app.importer.Base import ShopifyAPIException
from app.utils.logger import Logger
from app.utils.flow import error_out
import simplejson as json
import sys
import time
import datetime

RUN_ID = ""
SHOP_ID = ""

def create_url(shop):
    url = shop.url
    url = url.replace('https://', '')
    return "https://%s:%s@%sadmin/" % (shop.secret, shop.password, url)

def generate_run_id(shop_id):
    run_date = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return "%s-%s" % (shop_id, run_date)

if __name__ == "__main__":
    arg_count = len(sys.argv)
    if arg_count < 2 or arg_count > 3:
        sys.exit('Usage: importer <shop_id> <run_id>')
    shop_id = int(sys.argv[1])
    if arg_count == 2:
        run_id = generate_run_id(shop_id)
    else:
        run_id = str(sys.argv[2])
    RUN_ID = run_id
    SHOP_ID = shop_id

    Logger.start(run_id, shop_id)
    Logger.RUN_ID = run_id
    Logger.SHOP_ID = shop_id

    shop = UserShop.get(shop_id)

    full_url = create_url(shop)
    try:
        oShop = Shop(full_url)
        oShop.retrieve().save()
    except Exception as e:
        error_out(dict(message=e.__str__()))
    UserShop.set_shopify_id(shop.id, shop_id)

    order = Order(full_url, shop_id, shop.last_updated)
    order_ids = order.retrieve().save()

    Logger.status_message(run_id, shop.id, "Synced %s Orders" % (len(order_ids)))

    risks = OrderRisk(full_url, order_ids)
    risk_ids = risks.sync()
    Logger.status_message(run_id, shop.id, "Synced %s Order Risks" % (len(risk_ids)))
    
    transactions = OrderTransaction(full_url, order_ids)
    transaction_ids = transactions.sync()
    Logger.status_message(run_id, shop.id, "Synced %s Order Transactions" % (len(transaction_ids)))

    customer = Customer(full_url, shop_id, shop.last_updated)
    customer_ids = customer.retrieve().save()
    Logger.status_message(run_id, shop.id, "Synced %s Customers" % (len(customer_ids)))

    product = Product(full_url, shop_id)
    product_ids = product.retrieve().save()
    Logger.status_message(run_id, shop.id, "Synced %s Products" % (len(product_ids)))

    sz = ShippingZone(full_url, shop_id)
    sz_ids = sz.retrieve().save()
    Logger.status_message(run_id, shop.id, "Synced %s Shipping Zones" % (len(sz_ids)))

    Logger.complete(run_id, shop_id)

    UserShop.mark_updated(shop_id)
