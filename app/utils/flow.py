#!/usr/bin/env python
import sys
import simplejson as json

def error_out(message_obj):
    message_obj['error'] = True
    print(json.dumps(message_obj))
    sys.exit(1)
