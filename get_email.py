#!/usr/bin/env python
# -*- coding: utf_8 -*-

"""
Test batch method for getting email
"""

from data.models import Corpus


def get_email(id):
    c = Corpus()
    el = c.fetch_all_emails(column='id', query=id, exact_match=True)
    e = next(el)
    return e