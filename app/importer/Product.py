#!/usr/bin/env python
from app.importer.Base import Base
from app.models import Product as dbProduct
from app.importer.ProductVariant import ProductVariant
from app.utils.logger import Logger


class Product(Base):

    data = None
    ep = "products.json?limit=250"
    json_root = "products"
    paginated = True
    base = None
    shop_id = None

    def __init__(self, base, shop_id):
        self.base = base
        self.shop_id = shop_id

    def save(self):
        ids = []

        variant_count = 0

        for product in self.data:
            id = dbProduct.upsert(product, self.shop_id)
            ids.append(id)
            pv = ProductVariant(id)
            variant_count = variant_count + len(pv.save(product['variants']))
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Product Variants" % (variant_count))
        return ids

