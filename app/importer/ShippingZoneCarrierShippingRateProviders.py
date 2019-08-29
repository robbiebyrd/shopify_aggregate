#!/usr/bin/env python
from app.importer.Base import Base
from app.models import ShippingZoneCarrierShippingRateProviders as dbSZCSRP

class ShippingZoneCarrierShippingRateProviders(Base):

    data = None
    json_root = 'carrier_shipping_rate_providers'

    def __init__(self):
        pass

    def save(self, data):
        ids = []
        for carrier in data:
            id = dbSZCSRP.upsert(carrier)
            ids.append(id)
        return ids
