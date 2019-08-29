#!/usr/bin/env python
from app.importer.Base import Base
from app.models import ShippingZonePriceBasedShippingRates as dbSZPBSR

class ShippingZonePriceBasedShippingRates(Base):

    data = None
    json_root = 'price_based_shipping_rates'

    def __init__(self):
        pass

    def save(self, data):
        ids = []
        for priceBased in data:
            id = dbSZPBSR.upsert(priceBased)
            ids.append(id)
        return ids
