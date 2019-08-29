#!/usr/bin/env python
from app.importer.Base import Base
from app.models import ShippingZoneCountriesProvinces as dbShippingZoneCountriesProvinces

class ShippingZoneCountriesProvinces(Base):

    data = None
    json_root = 'provinces'

    def __init__(self):
        pass

    def save(self, data):
        ids = []
        for province in data:
            id = dbShippingZoneCountriesProvinces.upsert(province)
            ids.append(id)
        return ids

