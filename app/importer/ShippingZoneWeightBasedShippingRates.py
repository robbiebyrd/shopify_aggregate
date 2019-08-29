#!/usr/bin/env python
from app.importer.Base import Base
from app.models import ShippingZoneWeightBasedShippingRates as dbSZWBSR

class ShippingZoneWeightBasedShippingRates(Base):

    data = None
    json_root = 'weight_based_shipping_rates'

    def __init__(self):
        pass

    def save(self, data):
        ids = []
        for weightBased in data:
            id = dbSZWBSR.upsert(weightBased)
            ids.append(id)
        return ids
