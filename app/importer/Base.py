#!/usr/bin/env python
import requests
import simplejson as json

class Base:
    paginated = False
    last_updated = None
    def __init__(self):
        pass

    def retrieve(self):
        if self.paginated:
            return self.retrieve_paginated()
        res = requests.get("".join([self.base, self.ep]))
        obj = json.loads(res.text)

        if 'errors' in obj:
            raise ShopifyAPIException("Shopify API Error: %s" % obj['errors'])
        if self.json_root in obj:
            self.data = obj[self.json_root]
        else:
            self.data = []
        return self

    def retrieve_paginated(self):
        count = 1
        objs = []
        while True:
            url = "".join([self.base, self.ep, "&page=", str(count)])
            if self.last_updated:
                timestamp = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S-00:00")
                url = "%s&updated_at_min=%s" % (url, timestamp)
                #print("Last updated: %s" % timestamp);
            res = requests.get(url)

            resp = res.text
            obj = json.loads(resp)
            if not self.json_root in obj or len(obj[self.json_root]) == 0:
                break

            objs = objs + obj[self.json_root]
            count = count + 1
        self.data = objs
        return self

class ShopifyAPIException(Exception):
    pass
