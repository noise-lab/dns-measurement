import json
import argparse
import sys

import tldextract
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.stats as stats

sys.path.append('../measure')
from database import DNSDatabase


def prettify_label(label):
    label = label.replace("_dns", " Do53")
    label = label.replace("_dot", " DoT")
    label = label.replace("_doh", " DoH")
    label = label.replace("default", "Default")
    label = label.replace("cloudflare", "Cloudflare")
    label = label.replace("google", "Google")
    label = label.replace("quad9", "Quad9")
    return label


def get_all_hars(db, domains):
    default_dns_hars = db.get_hars("default", "dns", domains=domains)
    quad9_dns_hars = db.get_hars("quad9", "dns", domains=domains)
    quad9_doh_hars = db.get_hars("quad9", "doh", domains=domains)
    quad9_dot_hars = db.get_hars("quad9", "dot", domains=domains)
    cf_dns_hars = db.get_hars("cloudflare", "dns", domains=domains)
    cf_doh_hars = db.get_hars("cloudflare", "doh", domains=domains)
    cf_dot_hars = db.get_hars("cloudflare", "dot", domains=domains)
    google_dns_hars = db.get_hars("google", "dns", domains=domains)
    google_doh_hars = db.get_hars("google", "doh", domains=domains)
    google_dot_hars = db.get_hars("google", "dot", domains=domains)
    all_hars = {"default_dns": default_dns_hars,
                "quad9_dns": quad9_dns_hars,
                "quad9_doh": quad9_doh_hars,
                "quad9_dot": quad9_dot_hars,
                "cf_dns": cf_dns_hars,
                "cf_doh": cf_doh_hars,
                "cf_dot": cf_dot_hars,
                "google_dns": google_dns_hars,
                "google_doh": google_doh_hars,
                "google_dot": google_dot_hars}
    return all_hars


def load_domains(filename):
    with open(filename, "r") as f:
        domains = f.read().splitlines()
    return domains


def plot_cdf(all_data, xlimit, bin_step, xlabel, filename, neg_xlimit=False, ccdf=False, legend_loc='lower right'):
    # Set up the plot
    plt.figure()
    margin = .033333333

    # Plot the CDF
    fig, ax = plt.subplots()
    if neg_xlimit:
        ax.set_xlim([- (xlimit * (1 + margin)), xlimit * (1 + margin)])
    else:
        ax.set_xlim([- margin * xlimit, xlimit * (1 + margin)])
    ax.set_ylim([-0.05, 1.05])

    i = 0
    for key in sorted(all_data.keys()):
        data = all_data[key]
        d = data["data"]
        color = data["color"]
        linestyle = data["linestyle"]

        sortedd = np.sort(d)
        dp = 1. * np.arange(len(sortedd))/(len(sortedd) - 1)
        if ccdf:
            dp = [1 - dp_val for dp_val in dp]
        ax.plot(sortedd, dp, linewidth=1.5, color=color, linestyle=linestyle,
                label=key)
        i +=1

    # Set up the labels/legend
    plt.xlabel(xlabel)
    plt.ylabel('Probability')
    legend = plt.legend(loc=legend_loc)
    legend.get_frame().set_linewidth(1)
    plt.savefig(filename, bbox_inches='tight')


def plot_pdf(all_data, xlabel, filename):
    # Set up the plot
    plt.figure()

    # Plot the PDF
    fig, ax = plt.subplots()
    for key in sorted(all_data.keys()):
        data = all_data[key]
        d = data["data"]
        color = data["color"]
        linestyle = data["linestyle"]

        d.sort()
        hmean = np.mean(d)
        hstd = np.std(d)
        pdf = stats.norm.pdf(d, hmean, hstd)
        ax.plot(d, pdf, linewidth=1.5, color=color,
                linestyle=linestyle, label=key)
        ax.axvline(x=hmean, color='gray',
                   linewidth=0.75, linestyle='--')

    # Set up the labels/legend
    plt.xlabel(xlabel)
    plt.ylabel('Probability')
    legend = plt.legend(loc='upper right')
    legend.get_frame().set_linewidth(1)
