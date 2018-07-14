# -*- coding: utf-8 -*-

import base64
import json


def dec_data(dic_value):
    data = base64.b64decode(dic_value).decode('utf-8')
    dic = json.loads(data)
    return dic

