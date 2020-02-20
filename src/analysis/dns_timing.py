#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
import sys
import tldextract
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.stats as stats

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from common import prettify_label

sys.path.append('../measure')
from database import DNSDatabase


def dns_timings(db, xlimit, filename, legend=False, experiments=None):
    quad9_data = {"default_dns": {"timings":[], "color":"#000000", "linestyle":"-"},
            "quad9_dns": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "quad9_doh": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "quad9_dot": {"timings":[], "color":"#0072B2", "linestyle":"-."}}

    cloudflare_data = {"default_dns": {"timings":[], "color":"#000000", "linestyle":"-"},
            "cloudflare_dns": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "cloudflare_doh": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "cloudflare_dot": {"timings":[], "color":"#0072B2", "linestyle":"-."}}

    google_data = {"default_dns": {"timings":[], "color":"#000000", "linestyle":"-"},
            "google_dns": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "google_doh": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "google_dot": {"timings":[], "color":"#0072B2", "linestyle":"-."}}

    # Get DNS timings for each configuration
    timings = db.get_dns_timings(experiments)
    for tup in timings:
        dns_type = tup['dns_type']
        recursive = tup['recursive']
        error = tup['error']
        config = recursive + "_" + dns_type
        response_time = tup['response_time']
        response_size = tup['response_size']
        if error or (response_time == 0 and response_size == 0 and error == 0):
            continue

        if config in quad9_data:
            quad9_data[config]['timings'].append(response_time)
        if config in cloudflare_data:
            cloudflare_data[config]['timings'].append(response_time)
        if config in google_data:
            google_data[config]['timings'].append(response_time)


    # Plot a CDF
    plot_dns_timings(quad9_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_quad9.pdf", legend=legend)
    plot_dns_timings(cloudflare_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_cf.pdf", legend=legend)
    plot_dns_timings(google_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_google.pdf", legend=legend)


def dns_timings_cf(db, xlimit, filename, legend=False, experiments=None):
    cloudflare_data = {"default_dns": {"timings":[], "color":"#000000", "linestyle":"-"},
            "cloudflare_dns": {"timings":[], "color":"#0072B2", "linestyle":"-"},
            "cloudflare_doh": {"timings":[], "color":"#0072B2", "linestyle":":"},
            "cloudflare_dot": {"timings":[], "color":"#0072B2", "linestyle":"-."}}

    # Get DNS timings for each configuration
    timings = db.get_dns_timings(experiments)
    for tup in timings:
        dns_type = tup['dns_type']
        recursive = tup['recursive']
        error = tup['error']
        config = recursive + "_" + dns_type
        response_time = tup['response_time']
        response_size = tup['response_size']
        if error or (response_time == 0 and response_size == 0 and error == 0):
            continue

        if config in cloudflare_data:
            cloudflare_data[config]['timings'].append(response_time)

    # Plot a CDF
    plot_dns_timings(cloudflare_data, xlimit, 1, "DNS Response Time (ms)",
                     filename + "_cf.pdf", legend=legend)


def plot_dns_timings(data, xlimit, bin_step, xlabel, filename, legend=False):
    # Set up the plot
    margin = .033333333
    plt.figure()
    fig, ax = plt.subplots()
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Probability')
    ax.set_xlim(- margin * xlimit, xlimit * (1 + margin))
    ax.set_ylim(-0.05, 1.05)
    ax.set_xticks((0, 100, 200, 300, 400, 500, 600))

    # Set up the inset plot
    if "3g" in filename:
        ax_ins = inset_axes(ax, width=2.15, height=1.4,
                            loc='lower right', bbox_to_anchor=(375,140))
    else:
        ax_ins = inset_axes(ax, width=2.15, height=1.4,
                            loc='lower right', bbox_to_anchor=(560,75))

    ax_ins.set_xlim(- margin * 1500,
                      1500 * (1 + margin))
    ax_ins.set_ylim(-0.05, 1.05)
    ax_ins.set_xticks((0, 1500))
    ax_ins.set_yticks((0, 1))
    ax_ins.tick_params(axis='both', which='major', labelsize=16)

    for key in sorted(data.keys()):
        # Unpack the data to plot
        d = data[key]
        timings = d["timings"]

        print(key, np.mean(timings), np.std(timings))

        color = d["color"]
        linestyle = d["linestyle"]

        # Plot the data
        sorted_timings = np.sort(timings)
        probs = 1. * np.arange(len(sorted_timings))/(len(sorted_timings) - 1)
        ax.plot(sorted_timings, probs, linewidth=2, color=color,
                linestyle=linestyle, label=prettify_label(key))
        ax_ins.plot(sorted_timings, probs, linewidth=1.75, color=color,
                    linestyle=linestyle, label=prettify_label(key))

    if legend:
        # ax.legend(loc='center', bbox_to_anchor=(0.5, -0.3), mode='expand', ncol=2, fontsize=16, frameon=False)
        ax.legend(loc='center', bbox_to_anchor=(0.5, -0.45), mode='expand', ncol=2, fontsize=16, frameon=False)
    plt.savefig(filename, bbox_inches='tight')


def dns_timings_diffs(db, domains, xlimit, filename, experiments=None):
    all_dns_timings = db.get_dns_timings_domains(domains, experiments)

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

    dns_timings_per_experiment = {}
    differences_per_config = {}
    for config in configs:
        for tup in all_dns_timings:
            domain = tup['domain']
            exp = tup['experiment']

            if exp not in dns_timings_per_experiment:
                dns_timings_per_experiment[exp] = {}

            config = tup['recursive'] + '_' + tup['dns_type']
            if config not in dns_timings_per_experiment[exp]:
                dns_timings_per_experiment[exp][config] = {}

            dns_timing = tup['response_time']
            if dns_timing:
                dns_timing = float(dns_timing) / 1000.
                dns_timings_per_experiment[exp][config][domain] = dns_timing

    for c1 in configs:
        for c2 in configs:
            for exp in dns_timings_per_experiment.keys():
                domains_c1 = dns_timings_per_experiment[exp][c1].keys()
                domains_c2 = dns_timings_per_experiment[exp][c2].keys()
                for domain in (set(domains_c1) & set(domains_c2)):
                    dns_timing_c1 = dns_timings_per_experiment[exp][c1][domain]
                    dns_timing_c2 = dns_timings_per_experiment[exp][c2][domain]

                    joint_configs = c1 + '-' + c2
                    if joint_configs not in differences_per_config:
                        differences_per_config[joint_configs] = []
                    if dns_timing_c1 and dns_timing_c2:
                        if c1 != c2:
                            diff = dns_timing_c1 - dns_timing_c2
                            differences_per_config[joint_configs].append(diff)
                        else:
                            differences_per_config[joint_configs].append(dns_timing_c1)
                            differences_per_config[joint_configs].append(dns_timing_c2)

    # Plot CDFs for each configuration
    all_data = {}
    for joint_configs in differences_per_config:
        differences = differences_per_config[joint_configs]
        color = "#0072B2"
        linestyle = "-"
        data = {"data": differences, "color": color, "linestyle": linestyle}
        all_data[joint_configs] = data

    plot_dns_timings_diffs(all_data, configs, (10, 10),
                           "DNS Resolution Time (ms)", filename + "_cdf.pdf")


def plot_dns_timings_diffs(all_data, configs, shape, xlabel, filename):
    # Set up the plots
    fig, axes = plt.subplots(shape[0], shape[1], sharex=True, sharey=True)

    for i in range(shape[0]):
        c1 = configs[i]
        for j in range(shape[1]):
            c2 = configs[j]
            key = c1 + '-' + c2

            data = all_data[key]
            d = data["data"]
            color = data["color"]
            linestyle = data["linestyle"]

            ax = axes[i, j]

            if i == 0:
                # i = row
                ax.set_title("{}\n{}".format(j + 1, prettify_label(c2)))

            if j == 0:
                # j = column
                ax.set_ylabel("{}\n{}".format(chr(65 + 9 - i), prettify_label(c1)))

            # if i == j:
            #     hmean = np.mean(sortedd)
            #     hstd = np.std(sortedd)
            #     pdf = stats.norm.pdf(sortedd, hmean, hstd)
            #     ax.plot(sortedd, pdf, color=color, linestyle=linestyle)
            # else:


            sortedd = np.sort(d)
            dmean = np.mean(d)

            if j != i:
                # Differences
                dp = 1. * np.arange(len(sortedd)) / (len(sortedd) - 1)
                if j < i:
                    if dmean < -0.0: # faster
                        ax.set_facecolor((0x46/255, 0x78/255, 0x21/255, min(0.5, abs(dmean))))
                    if dmean > 0.0: # slower
                        ax.set_facecolor((0xA6/255, 0x06/255, 0x28/255, min(0.5, dmean)))
                    linecolor = data["color"]
                    meancolor = "gray"

                if j > i:
                    if dmean < -0.0: # faster
                        ax.set_facecolor((0x46/255, 0x78/255, 0x21/255, min(0.15, abs(dmean))))
                    if dmean > 0.0: # slower
                        ax.set_facecolor((0xA6/255, 0x06/255, 0x28/255, min(0.15, dmean)))
                    linecolor = "#348ABD99"
                    meancolor = "lightgray"
                    for spine in ('top', 'bottom', 'left', 'right'):
                        ax.spines[spine].set_color("lightgray")

                ax.plot(sortedd, dp, color=linecolor, linestyle=linestyle, zorder=2)
                ax.set_xscale('symlog')
                # ax.set_yscale('symlog')
                ax.set_xticklabels(['-2', '-1', '0', '1', '2'])
                ax.axvline(x=dmean, color=meancolor, linestyle='-', zorder=1)
            else:
                # Distribution
                linecolor = data["color"]
                meancolor = "gray"
                ax.set_facecolor('#BBBBBB')

                #hist, bins = np.histogram(d, 1000)
                #ax.plot(d, pdf, color=color, linestyle=linestyle)

    for i in range(shape[0]):
        for j in range(shape[1]):
            if j > i:
                axes[i, j].tick_params(axis='both', color='lightgray')

    # Set up the labels/legend
    plt.savefig(filename, bbox_inches='tight')
