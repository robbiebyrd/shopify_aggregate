#!/usr/bin/env python
from app.importer.Base import Base
from app.models import ShippingZone as dbShippingZone
from app.importer.ShippingZoneCountries import ShippingZoneCountries
from app.importer.ShippingZoneWeightBasedShippingRates import ShippingZoneWeightBasedShippingRates
from app.importer.ShippingZonePriceBasedShippingRates import ShippingZonePriceBasedShippingRates
from app.importer.ShippingZoneCarrierShippingRateProviders import ShippingZoneCarrierShippingRateProviders
from app.utils.logger import Logger

class ShippingZone(Base):

    data = None
    ep = "shipping_zones.json?limit=250"
    json_root = 'shipping_zones'
    base = None
    shop_id = None

    def __init__(self, base, shop_id):
        self.base = base
        self.shop_id = shop_id

    def save(self):
        ids = []
        weight_based_rates_count = 0
        price_based_rates_count = 0
        carrier_rates_count = 0
        for zone in self.data:
            id = dbShippingZone.upsert(zone, self.shop_id)
            ids.append(id)

            szc = ShippingZoneCountries(id)
            szc.save(zone['countries'])

            szwbsr = ShippingZoneWeightBasedShippingRates()
            weight_based_rates_count = weight_based_rates_count + len(szwbsr.save(zone['weight_based_shipping_rates']))
            szpbsr = ShippingZonePriceBasedShippingRates()
            price_based_rates_count = price_based_rates_count + len(szpbsr.save(zone['price_based_shipping_rates']))
            szcsrp = ShippingZoneCarrierShippingRateProviders()
            carrier_rates_count = carrier_rates_count + len(szcsrp.save(zone['carrier_shipping_rate_providers']))

        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Shipping Zone Weight Based Rates" % (weight_based_rates_count))
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Shipping Zone Price Based Rates" % (price_based_rates_count))
        Logger.status_message(Logger.RUN_ID, Logger.SHOP_ID, "Synced %s Shipping Zone Carrier Shipping Rates" % (carrier_rates_count))

        return ids
