#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import sys

import tldextract
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import scipy.stats as stats

sys.path.append('../measure')

from database import DNSDatabase
from common import plot_pdf, plot_cdf
from numpy.polynomial.polynomial import polyfit
from common import plot_pdf, plot_cdf, prettify_label


def _colorize(ax, dm, shaded=False):
    if not shaded:
        if abs(dm) <= 0.033: # faster
            ax.set_facecolor("white")
        if dm > -0.10 and dm <= -0.033: # slower
            ax.set_facecolor("#d1e5f0")
        if dm > -1.0 and dm <= -0.10: # slower
            ax.set_facecolor("#67a9cfd9")
        if dm <= -1.0: # slower
            ax.set_facecolor("#2166accc")
        if dm < 0.10 and dm >= 0.033:
            ax.set_facecolor("#fddbc7")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xfd/255, 0xdb/255, 0xc7/255, 0.5))
        if dm < 1.0 and dm >= 0.10:
            ax.set_facecolor("#ef8a62d9")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xef/255, 0x8a/255, 0x62/255, 0.5))
        if dm >= 1.0: #
            ax.set_facecolor("#b2182bcc")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xb2/255, 0x18/255, 0x2b/255, 0.5))
    else:
        if abs(dm) <= 0.033: # faster
            ax.set_facecolor("#ffffff40")
        if dm > -0.10 and dm <= -0.033: # slower
            ax.set_facecolor("#d1e5f066")
        if dm > -1.0 and dm <= -0.10: # slower
            ax.set_facecolor("#67a9cf66")
        if dm <= -1.0: # slower
            ax.set_facecolor("#2166ac73")
        if dm < 0.10 and dm >= 0.033:
            ax.set_facecolor("#fddbc7")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xfd/255, 0xdb/255, 0xc7/255, 0.5))
        if dm < 1.0 and dm >= 0.10:
            ax.set_facecolor("#ef8a62bf")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xef/255, 0x8a/255, 0x62/255, 0.5))
        if dm >= 1.0: #
            ax.set_facecolor("#b2182b99")
            ax.fill_between([-40,40],-0.05,1.05,
                            facecolor="none",
                            linewidth=0.0,
                            hatch="......",
                            edgecolor=(0xb2/255, 0x18/255, 0x2b/255, 0.5))

    return ax


def cf_pageloads(db, domains, xlimit, filename, experiments=None):
    # Get page load timings for each configuration
    pageloads = db.get_pageloads(domains, experiments)
    pageloads_per_config = {}

    for tup in pageloads:
        config = tup['recursive'] + '_' + tup['dns_type']
        if config not in pageloads_per_config:
            pageloads_per_config[config] = []

        pageload = tup['pageload']
        if pageload:
            pageload = float(pageload) / 1000
            pageloads_per_config[config].append(pageload)

    # Plot a CDF
    data = {"Cloudflare DNS": {"data": pageloads_per_config['cloudflare_dns'],
                               "color": "#000000", "linestyle": "-"},
            "Cloudflare DoT": {"data": pageloads_per_config['cloudflare_dot'],
                               "color": "#0072B2", "linestyle": "-."},
            "Cloudflare DoH": {"data": pageloads_per_config['cloudflare_doh'],
                               "color": "#A60628", "linestyle": ":"}}
    plot_cdf(data, xlimit, 0.1, "Page Load Time (seconds)", filename + "_cdf.pdf")


def cf_pageloads_4g_3g(domains, xlimit, filename):
    # Get page load timings for 4G lossy and 3G each configuration
    raise Exception("needs to be updated")
    db_lossy_4g = DNSDatabase.init_from_config_file("../../data/heehaw_4g_lossy.ini")
    db_3g = DNSDatabase.init_from_config_file("../../data/oink_3g.ini")

    pageloads_lossy_4g = db_lossy_4g.get_pageloads(domains)
    pageloads_3g = db_3g.get_pageloads(domains)

    pageloads_per_config_lossy_4g = {}
    for tup in pageloads_lossy_4g:
        config = tup['recursive'] + '_' + tup['dns_type']
        if config not in pageloads_per_config_lossy_4g:
            pageloads_per_config_lossy_4g[config] = []

        pageload = tup['pageload']
        if pageload:
            pageload = float(pageload) / 1000
            pageloads_per_config_lossy_4g[config].append(pageload)

    pageloads_per_config_3g = {}
    for tup in pageloads_3g:
        config = tup['recursive'] + '_' + tup['dns_type']
        if config not in pageloads_per_config_3g:
            pageloads_per_config_3g[config] = []

        pageload = tup['pageload']
        if pageload:
            pageload = float(pageload) / 1000
            pageloads_per_config_3g[config].append(pageload)

    # Plot a CDF
    data = {"Lossy 4G Do53": {"data": pageloads_per_config_lossy_4g['cloudflare_dns'],
                                 "color": "#000000", "linestyle": "-"},
            "Lossy 4G DoH": {"data": pageloads_per_config_lossy_4g['cloudflare_doh'],
                                 "color": "#000000", "linestyle": ":"},
            "Lossy 4G DoT": {"data": pageloads_per_config_lossy_4g['cloudflare_dot'],
                                 "color": "#000000", "linestyle": "-."},
            "3G Do53": {"data": pageloads_per_config_3g['cloudflare_dns'],
                                 "color": "gray", "linestyle": "-"},
            "3G DoH": {"data": pageloads_per_config_3g['cloudflare_doh'],
                                 "color": "gray", "linestyle": ":"},
            "3G DoT": {"data": pageloads_per_config_3g['cloudflare_dot'],
                                 "color": "gray", "linestyle": "-."}}
    plot_cdf(data, xlimit, 0.1, "Page load time (seconds)", filename + "_cdf.pdf")


def pageload_vs_resources(db, xlimit, filename, experiments=None):
    pageloads_resources = db.get_resource_counts(experiments)

    # Get pageloads for each resource count for DNS, DoH, and DoT
    data = {}
    for tup in pageloads_resources:
        dns_type = tup['dns_type']
        resources = tup['resources']
        pageload = tup['pageload']

        if not dns_type or not resources or not pageload or pageload <= 0:
            continue

        if dns_type not in data:
            data[dns_type] = {'x': [], 'y': []}
        data[dns_type]['x'].append(resources)
        data[dns_type]['y'].append(pageload / 1000)

    # Make a scatterplot
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim(right=xlimit)
    for dns_type in data:
        x = data[dns_type]['x']
        y = data[dns_type]['y']
        b, m = polyfit(x, y, 1)
        print(dns_type, b, m)

        if dns_type == 'dns':
            color = 'red'
            zorder = 2
        if dns_type == 'dot':
            color = 'blue'
            zorder = 1
        if dns_type == 'doh':
            color = 'black'
            zorder = 0

        ax.scatter(x, y, s=0.2, alpha=0.3,
                   zorder=zorder, c=color, label=dns_type)

        fit_y = [(b + m * x_val) for x_val in x]
        ax.plot(x, fit_y, color=color, linewidth=2)
    plt.legend(loc='lower right')
    plt.savefig(filename)


def pageload_diffs(db, domains, xlimit, filename, configs_subset=None, experiments=None):
    all_pageloads = db.get_pageloads(domains, experiments)
    configs = ('default_dns',
               'quad9_dns',
               'quad9_dot',
               'quad9_doh',
               'google_dns',
               'google_dot',
               'google_doh',
               'cloudflare_dns',
               'cloudflare_dot',
               'cloudflare_doh')

    pageloads_per_experiment = {}
    differences_per_config = {}
    for config in configs:
        for tup in all_pageloads:
            domain = tup['domain']
            exp = tup['experiment']

            if exp not in pageloads_per_experiment:
                pageloads_per_experiment[exp] = {}

            config = tup['recursive'] + '_' + tup['dns_type']
            if config not in pageloads_per_experiment[exp]:
                pageloads_per_experiment[exp][config] = {}

            pageload = tup['pageload']
            if pageload:
                pageload = float(pageload) / 1000.
                pageloads_per_experiment[exp][config][domain] = pageload

    for c1 in configs:
        for c2 in configs:
            for exp in pageloads_per_experiment.keys():
                domains_c1 = pageloads_per_experiment[exp][c1].keys()
                domains_c2 = pageloads_per_experiment[exp][c2].keys()
                for domain in (set(domains_c1) & set(domains_c2)):
                    pageload_c1 = pageloads_per_experiment[exp][c1][domain]
                    pageload_c2 = pageloads_per_experiment[exp][c2][domain]

                    joint_configs = c1 + '-' + c2
                    if joint_configs not in differences_per_config:
                        differences_per_config[joint_configs] = []
                    if pageload_c1 and pageload_c2:
                        if c1 != c2:
                            diff = pageload_c1 - pageload_c2
                            differences_per_config[joint_configs].append(diff)
                        else:
                            differences_per_config[joint_configs].append(pageload_c1)
                            differences_per_config[joint_configs].append(pageload_c2)

    # Plot CDFs for each configuration
    all_data = {}
    for joint_configs in differences_per_config:
        differences = differences_per_config[joint_configs]
        color = "#0072B2"
        linestyle = "-"
        data = {"data": differences, "color": color, "linestyle": linestyle}
        all_data[joint_configs] = data

    if configs_subset:
        plot_pageload_diffs_subset(all_data, configs_subset, "Page load time (seconds)",
                                   filename + "_cdf.pdf")
    else:
        plot_pageload_diffs(all_data, configs, (10, 10), "Page load time (seconds)",
                            filename + "_cdf.pdf")


def plot_pageload_diffs_subset(all_data, joint_configs, xlabel, filename, experiments=None):
    for key in joint_configs:
        fig, ax = plt.subplots(1, 1)

        data = all_data[key]
        d = data["data"]
        linestyle = data["linestyle"]

        dm = np.median(d)
        ax = _colorize(ax, dm)
        linecolor = 'black'
        meancolor = "#333333"

        sortedd = np.sort(d)
        dp = 1. * np.arange(len(sortedd)) / (len(sortedd) - 1)
        ax.plot(sortedd, dp, color=linecolor, linestyle=linestyle, zorder=2, linewidth=2)
        ax.set_xscale('symlog')
        ax.set_xticklabels(['-10', '-1', '0', '1', '10'], fontsize=24)
        ax.set_yticklabels(['0.0', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=24)
        ax.axvline(x=dm, color=meancolor, linestyle='-', zorder=1, linewidth=1.75)

        c1, c2 = key.split('-', 2)
        ax.set_title("{} - {}".format(prettify_label(c1), prettify_label(c2)), fontsize=20)

        ax.set_xlabel("Page Load Time Difference (seconds)", labelpad=18, fontsize=24)
        ax.set_ylabel("Probability", labelpad=18, fontsize=24)
        plt.savefig(key + "_" + filename, bbox_inches='tight')

    figlegend = plt.figure(figsize=(15.25, 0.55))
    p1 = mpatches.Patch(facecolor="#b2182b", edgecolor="#333333", linewidth=0.25, hatch='......',label='Diff ≥ 1s')
    p2 = mpatches.Patch(facecolor="#ef8a62", edgecolor="#333333", linewidth=0.25, hatch='......',label='0.1s ≤ Diff < 1s')
    p3 = mpatches.Patch(facecolor="#fddbc7", edgecolor="#333333", linewidth=0.25, hatch='......',label='0.03s ≤ Diff < 0.1s')
    p4 = mpatches.Patch(facecolor="#ffffff", edgecolor="#333333", linewidth=0.25, label='-0.03s < Diff < 0.03s')
    p5 = mpatches.Patch(facecolor="#d1e5f0", edgecolor="#333333", linewidth=0.25, label='-0.1s < Diff ≤ -0.03s')
    p6 = mpatches.Patch(facecolor="#67a9cf", edgecolor="#333333", linewidth=0.25, label='-1s < Diff ≤ -0.1s')
    p7 = mpatches.Patch(facecolor="#2166ac", edgecolor="#333333", linewidth=0.25, label='Diff ≤ -1s')
    figlegend.legend(handles = [p1,p2,p3,p4,p5,p6,p7],ncol=7,frameon=False, fontsize=12,handlelength=3, handleheight=2)
    figlegend.savefig('pageload_diff_subset_legend.pdf')


def plot_pageload_diffs(all_data, configs, shape, xlabel, filename, experiments=None):
    fig, axes = plt.subplots(shape[0], shape[1], sharex=True, sharey=True)

    for i in range(shape[0]):
        c1 = configs[i]
        for j in range(shape[1]):
            c2 = configs[j]
            key = c1 + '-' + c2

            data = all_data[key]
            d = data["data"]
            linestyle = data["linestyle"]

            ax = axes[i, j]

            if i == 0:
                # i = row
                ax.set_title("{}\n{}".format(j + 1, prettify_label(c2)), size=4)

            if j == 0:
                # j = column
                ax.set_ylabel("{}\n{}".format(chr(65 + i), prettify_label(c1)),
                              rotation=0, labelpad=18, y=0.33, size=4)

            sortedd = np.sort(d)
            dm = np.median(d)
            mpl.rc('hatch', color='r', linewidth=0.000)

            print(key, dm)

            if j != i:
                # Differences
                if j < i:
                    linecolor = 'black'
                    meancolor = "#333333"
                    ax = _colorize(ax, dm)

                if j > i:
                    ax = _colorize(ax, dm, shaded=True)
                    linecolor = "#00000080"
                    meancolor = "#33333380"

                    for spine in ('top', 'bottom', 'left', 'right'):
                        ax.spines[spine].set_color("lightgray")

                dp = 1. * np.arange(len(sortedd)) / (len(sortedd) - 1)
                ax.plot(sortedd, dp, color=linecolor, linestyle=linestyle, zorder=2, linewidth=0.75)
                ax.set_xscale('symlog')
                ax.set_xticklabels(['-10', '-1', '0', '1', '10'])
                ax.axvline(x=dm, color=meancolor, linestyle='--', zorder=1, linewidth=0.5)
            else:
                # Distribution
                linecolor = data["color"]
                meancolor = "gray"
                ax.set_facecolor('#BBBBBB')

    for i in range(shape[0]):
        for j in range(shape[1]):
            if j > i:
                axes[i, j].tick_params(axis='both', color='lightgray')

    p1 = mpatches.Patch(facecolor="#b2182b", edgecolor="#333333", linewidth=0.25, hatch='......',label='x ≥ 1s')
    p2 = mpatches.Patch(facecolor="#ef8a62", edgecolor="#333333", linewidth=0.25, hatch='......',label='0.1s ≤ x < 1s')
    p3 = mpatches.Patch(facecolor="#fddbc7", edgecolor="#333333", linewidth=0.25, hatch='......',label='0.03s ≤ x < 0.1s')
    p4 = mpatches.Patch(facecolor="#ffffff", edgecolor="#333333", linewidth=0.25, label='-0.03s < x < 0.03s')
    p5 = mpatches.Patch(facecolor="#d1e5f0", edgecolor="#333333", linewidth=0.25, label='-0.1s < x ≤ -0.03s')
    p6 = mpatches.Patch(facecolor="#67a9cf", edgecolor="#333333", linewidth=0.25, label='-1s < x ≤ -0.1s')
    p7 = mpatches.Patch(facecolor="#2166ac", edgecolor="#333333", linewidth=0.25, label='x ≤ -1s')

    plt.figlegend(handles = [p7,p6,p5,p4,p3,p2,p1], loc="lower center", ncol=7, frameon=False, fontsize=4, bbox_to_anchor=(0.45, 0.02), handlelength=5, handleheight=4)

    plt.savefig(filename, bbox_inches='tight')
