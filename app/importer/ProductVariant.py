#!/usr/bin/env python
from app.importer.Base import Base
from app.models import ProductVariant as dbProductVariant

class ProductVariant(Base):

    data = None
    json_root = "variants"
    product_id = None

    def __init__(self, product_id):
        self.product_id = product_id

    def save(self, data):
        ids = []
        for variant in data:
            id = dbProductVariant.upsert(variant, self.product_id)
            ids.append(id)
        return ids

