#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import matplotlib as mpl

from collections import namedtuple
from configparser import ConfigParser

sys.path.append('../measure')

from database import DNSDatabase
from pageload import pageload_diffs, pageload_vs_resources
from dns_timing import dns_timings, dns_timings_cf, dns_timings_diffs
from resources import ext_domains
from amortization import amortization
from common import load_domains


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('database_config_file')
    parser.add_argument('domains_file')
    parser.add_argument('--matplotlibrc', help='custom matplotlibrc')
    parser.add_argument("--cf_pageloads", action='store_true', default=False)
    parser.add_argument("--cf_pageloads_4g_3g", action='store_true', default=False)
    parser.add_argument("--pageload_diffs", action='store_true', default=False)
    parser.add_argument('--pageload_diffs_cf', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_google', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_quad9', action='store_true', default=False)
    parser.add_argument('--pageload_diffs_doh', action='store_true', default=False)
    parser.add_argument("--pageload_resources", action='store_true', default=False)
    parser.add_argument("--timing", action='store_true', default=False)
    parser.add_argument("--timing_cf", action='store_true', default=False)
    parser.add_argument("--domain", action='store_true', default=False)
    parser.add_argument("--amortization", action='store_true', default=False)
    parser.add_argument("--name", default=None)
    parser.add_argument("--experiments", default=None, nargs="+")
    args = parser.parse_args()

    # If a custom matplotlibrc is provided, load it
    if args.matplotlibrc:
        mpl.rc_file(args.matplotlibrc)

    # Connect to the db
    db = DNSDatabase.init_from_config_file(args.database_config_file)

    # Load a list of domains to query HARs for
    domains = load_domains(args.domains_file)

    if args.name:
        pageload_diff_filename = "pageload_diff_{}".format(args.name)
        cf_pageloads_filename = "cf_pageloads_{}".format(args.name)
        cf_pageloads_4g_3g_filename = "cf_pageloads_4g_3g{}".format(args.name)
        timings_filename = "dns_timings_{}".format(args.name)
        timings_diff_filename = "dns_timings_diff_{}".format(args.name)
        domains_filename = "domains_{}".format(args.name)
        pageload_resources_filename = "pageload_resources_{}".format(args.name)
        pageloads_subset_filename = "pageload_diff_subset_{}".format(args.name)
        amortization_filename = "amortization_{}".format(args.name)
    else:
        pageload_diff_filename = "pageload_diff"
        cf_pageloads_filename = "cf_pageloads"
        cf_pageloads_4g_3g_filename = "cf_pageloads_4g_3g"
        timings_filename = "dns_timings"
        timings_diff_filename = "dns_timings_diff"
        domains_filename = "domains"
        pageload_resources_filename = "pageload_resources"
        pageloads_subset_filename = "pageload_diff_subset"
        amortization_filename = "amortization"

    # Make plots
    if args.cf_pageloads:
        print("Plotting Cloudflare pageloads")
        cf_pageloads(db, domains, xlimit=30, filename=cf_pageloads_filename,
                     experiments=args.experiments)

    if args.cf_pageloads_4g_3g:
        print("Plotting Cloudflare pageloads (4G lossy and 3G)")
        cf_pageloads_4g_3g(domains, xlimit=30, filename=cf_pageloads_4g_3g_filename,
                           experiments=args.experiments)

    if args.pageload_diffs:
        print("Plotting pageload differences")
        pageload_diffs(db, domains, xlimit=10, filename=pageload_diff_filename,
                       experiments=args.experiments)

    if args.timing:
        print("Plotting DNS timings")
        dns_timings(db, xlimit=650, filename=timings_filename, legend=True,
                    experiments=args.experiments)

    if args.timing_cf:
        print("Plotting DNS timings")
        dns_timings_cf(db, xlimit=650, filename=timings_filename, legend=True,
                       experiments=args.experiments)

    if args.domain:
        print("Plotting domains")
        ext_domains(db, domains, xlimit=75, filename=domains_filename)

    if args.pageload_resources:
        print("Plotting pageloads vs. resources")
        pageload_vs_resources(db, xlimit=800, filename=pageload_resources_filename,
                              experiments=args.experiments)

    if args.pageload_diffs_cf:
        print("Plotting subset of pageload differences for Cloudflare")
        joint_configs = ('cloudflare_doh-cloudflare_dns',
                         'cloudflare_dot-cloudflare_dns')
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_google:
        print("Plotting subset of pageload differences for Google")
        joint_configs = ('google_doh-google_dns',
                         'google_dot-google_dns')
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_quad9:
        print("Plotting subset of pageload differences for Quad9")
        joint_configs = ('quad9_doh-quad9_dns',
                         'quad9_dot-quad9_dns')
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.pageload_diffs_doh:
        print("Plotting subset of pageload differences for all DoH providers")
        joint_configs = ('cloudflare_doh-quad9_doh',
                         'cloudflare_doh-google_doh',
                         'google_doh-quad9_doh')
        pageload_diffs(db, domains, xlimit=10, filename=pageloads_subset_filename,
                       configs_subset=joint_configs,
                       experiments=args.experiments)

    if args.amortization:
        print("Plotting Do53/DoH/DoT amortization")
        amortization(xlimit=100, filename=amortization_filename)


if __name__ == "__main__":
    main()
