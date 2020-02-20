#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import sys

import numpy as np
import pandas as pd
import scipy.stats as stats

sys.path.append('../measure')

from database import DNSDatabase


def per_website_total_bytes(db):
    # Get each HTTP request/response that was made
    content_sizes = db.get_content_sizes()
    columns = ['uuid', 'domain', 'recursive', 'dns_type',
               'requestHeadersSize', 'requestBodySize',
               'responseHeadersSize', 'responseBodySize']
    df = pd.DataFrame(data=content_sizes, columns=columns)

    # Group the requests by HARs, and sum the bytes sent/received for each HAR
    per_har_bytes = df.groupby(['uuid', 'domain', 'recursive', 'dns_type']).sum()
    total_bytes = per_har_bytes.loc[:, ['requestHeadersSize', 'requestBodySize', 
                                        'responseHeadersSize', 'responseBodySize']].sum(axis=1)

    # Compute summary stats for bytes sent/received for each website
    per_website_median = total_bytes.groupby(['domain']).median()
    per_website_stats = total_bytes.groupby(['domain']).describe()
    per_website_stats['median'] = per_website_median
    per_website_stats.to_json('per_website_stats.json')
    print(per_website_stats)


def all_websites_total_bytes(db):
    # Get each HTTP request/response that was made
    content_sizes = db.get_content_sizes()
    columns = ['uuid', 'domain', 'recursive', 'dns_type',
               'requestHeadersSize', 'requestBodySize',
               'responseHeadersSize', 'responseBodySize']
    df = pd.DataFrame(data=content_sizes, columns=columns)

    # Group the requests by HARs, and sum the bytes sent/received for each HAR
    per_har_bytes = df.groupby(['uuid', 'domain', 'recursive', 'dns_type']).sum()
    total_bytes = per_har_bytes.loc[:, ['requestHeadersSize', 'requestBodySize', 
                                        'responseHeadersSize', 'responseBodySize']].sum(axis=1)

    # Compute summary stats for bytes sent/received across all websites
    total_median = total_bytes.median()
    total_stats = total_bytes.describe()
    total_stats['median'] = total_median
    total_stats.to_json('total_stats.json')
    print(total_stats)


if __name__ == '__main__':
    # Connect to the db
    config_file = '../../data/postgres.ini'
    db = DNSDatabase.init_from_config_file(config_file)
    per_website_total_bytes(db)
    all_websites_total_bytes(db)
