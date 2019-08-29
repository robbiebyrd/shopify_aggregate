#!/usr/bin/env python
from app.importer.Base import Base
from app.models import ShippingZoneCountries as dbShippingZoneCountries
from app.importer.ShippingZoneCountriesProvinces import ShippingZoneCountriesProvinces

class ShippingZoneCountries(Base):

    data = None
    json_root = 'countries'
    shipping_zone_id = None

    def __init__(self, shipping_zone_id):
        self.shipping_zone_id = shipping_zone_id

    def save(self, data):
        ids = []
        for country in data:
            id = dbShippingZoneCountries.upsert(country, self.shipping_zone_id)
            ids.append(id)
            szcp = ShippingZoneCountriesProvinces()
            szcp.save(country['provinces'])
        return ids
