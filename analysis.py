#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 09:37:44 2020

@author: anobles
"""


import pandas as pd



if __name__ == "__main__":
    # open csv
    df = pd.open_csv('INPUT_PATHWAY')

    # count the number of times a unique url was tweeted in original tweets
    df.groupby('url_returned').count()

    # count the number of times each url was shared
    count_url_shared = df['url_returned'].value_counts()
    count_url_shared = count_url_shared.to_frame()
    count_url_shared.reset_index(inplace=True)
    count_url_shared.rename(columns={"index": "url", "url_returned": "count"}, inplace=True)
    count_url_shared.to_csv('OUTPUT_PATHWAY', index=False)

    # count the number of times each tld was shared
    count_tld_shared = df['top_level_domain'].value_counts()
    count_tld_shared = count_tld_shared.to_frame()
    count_tld_shared.reset_index(inplace=True)
    count_tld_shared.rename(columns={"index": "tld", "top_level_domain": "count"}, inplace=True)
    count_tld_shared.to_csv('OUTPUT_PATHWAY', index=False)

    # count the number of times each tld -- domain was shared
    count_tld_domain_shared = df.groupby(['top_level_domain', 'domain']).size()
    count_tld_domain_shared = count_tld_domain_shared.to_frame()
    count_tld_domain_shared.reset_index(inplace=True)
    count_tld_domain_shared.rename(columns={0: "count"}, inplace=True)
    count_tld_domain_shared.to_csv('OUTPUT_PATHWAY', index=False)
