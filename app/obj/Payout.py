#!/usr/bin/env python
from timelib import strtodatetime
from app.models import Order

class Payout:
    shop_id                        = None
    store_data                     = None
    sales_activity_by_order_status = None
    sales_by_best_sellers          = None
    commission_rate                = None
    totals                         = None

    def __init__(self, shop_id):
        self.shop_id         = shop_id
        self.start           = strtodatetime("2016-05-01 00:00:00".encode('utf-8'))
        self.end             = strtodatetime("2016-05-31 23:59:59".encode('utf-8'))
        self.commission_rate = 0.15;

    def get_store_data(self):
        data = Order.get_store_data(self.shop_id, self.start, self.end)
        self.store_data = data
        return data

    def get_sales_activity_by_order_status(self):
        data = Order.get_sales_activity_by_order_status(self.shop_id, self.start, self.end)
        self.sales_activity_by_order_status = data
        return data

    def get_totals(self):
        data = dict()
        data['amount_shipped'] = 0
        data['number_shipped'] = 0
        for stati in self.sales_activity_by_order_status:
            data['amount_shipped'] = data['amount_shipped'] + stati['amount_shipped']
            data['number_shipped'] = data['number_shipped'] + stati['number_shipped']

        data['net_merchandise_sales'] = dict(
            amount_shipped = data['amount_shipped'],
            number_shipped = data['number_shipped']
        )

        data['commission'] = dict(
                rate=self.commission_rate*100,
                commission=data['amount_shipped']*self.commission_rate
                )

        data['due'] = dict(
            due=data['amount_shipped']-data['commission']['commission']
            )

        self.totals = data

        return data

    def get_sales_by_best_sellers(self):
        data = Order.get_sales_by_best_sellers(self.shop_id, self.start, self.end)
        new_data = []
        total_percent = 0.0
        for datum in data:
            percent = datum['total_amount'] / self.totals['net_merchandise_sales']['amount_shipped']
            total_percent = total_percent + percent
            new_data.append(dict(
                total_amount=datum['total_amount'],
                total_quantity=datum['total_quantity'],
                name=datum['name'],
                sku=datum['sku'],
                percent=percent * 100,
                total_percent=total_percent * 100
                ))

        self.sales_by_best_sellers = new_data
        return new_data

