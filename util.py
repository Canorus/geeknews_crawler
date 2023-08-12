import requests
import json
import os
from logg import *
import unicodedata

base = os.path.join(os.path.dirname(os.path.abspath(__file__)),'')

def send_toot_alt(m):
    with open(os.path.join(base, 'auth.json')) as f:
        j = json.load(f)
    for k in j.keys():
        instance_ = k
        logger.debug('send meesage to ' + instance_)
        username = list(j[instance_])[0]
        acc = j[instance_][username]
        head = {'Authorization': 'Bearer ' + acc}
        data = dict()
        data['status'] = m
        data['visibility'] = 'unlisted'
        r = requests.post(instance_ + '/api/v1/statuses', headers=head, data=data)
        #return r
