#!/usr/bin/env python
# -*- coding: utf-8 -*-
# module: secrets.py
"""
Keep secret configuration data out of source control with 
a secrets.json file, and this module
"""
import json

with open("secrets.json") as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        raise Exception("Could not fetch {} from secrets.json.".format(setting))
