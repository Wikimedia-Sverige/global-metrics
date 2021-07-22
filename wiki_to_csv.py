#!/usr/bin/env python3


import re
import logging
from collections import defaultdict
from collections import OrderedDict
import datetime
import csv
import sys
import argparse

import pywikibot
from pywikibot import pagegenerators


METRIC_NAMES = [
    "deltagare_♀",
    "deltagare_♂",
    "deltagare_⚥",
    "deltagare_?",
    "deltagare_total",
    "nya_♀",
    "nya_♂",
    "nya_⚥",
    "nya_?",
    "nya_total",
    "org_♀",
    "org_♂",
    "org_⚥",
    "org_?",
    "org_total",
    "audience_♀",
    "audience_♂",
    "audience_⚥",
    "audience_?",
    "audience_total",
    "content_wp",
    "content_com",
    "content_wd",
    "content_other",
    "content_total"
]


def is_int(value):
    """Check if the given value is an integer.

    @param value: The value to check
    @type value: str, or int
    @return bool
    """
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def extract_elements_from_template_param(template_param):

    """Extract and sanitize the contents of a parsed template param."""

    (field, _, value) = template_param.partition('=')
    # Remove leading or trailing spaces
    field = field.strip()
    return (field, sanitize_wikitext_string(value))


def sanitize_wikitext_string(value):

    """Remove undesirable wikitext features from a string."""

    value = value.split("<ref")[0].strip()
    value = re.sub(r"\s?<!--.*?-->\s?", ' ', value)
    return value.strip()


def extract_all_data_on_page(page, year):
    logging.debug("=== {} ===".format(page))
    templates = page.templatesWithParams()
    contents = defaultdict(int)
    number_of_events = 0
    for (template, params) in templates:
        logging.debug("--- Template ---")
        template_name = template.title(withNamespace=False)
        if template_name != 'GlobalMetrics':
            logging.info(
                "Skipping template with incorrect name '{}'".format(template)
            )
            continue
        template_metrics = {}
        for param in params:
            (field, value) = extract_elements_from_template_param(param)
            template_metrics[field] = value
        if template_metrics["year"] != str(year):
            logging.info(
                "Skipping template with wrong year: {} on page {}."
                .format(template_metrics["year"], page)
            )
        else:
            number_of_events += 1
            logging.debug("--- GlobalMetrics #{} ---".format(number_of_events))
            for key, value in template_metrics.items():
                if key in METRIC_NAMES:
                    if value == "":
                        logging.warn(
                            "Empty value on page '{}' for key '{}'"
                            .format(page, key)
                        )
                        continue
                    elif not is_int(value):
                        logging.warn(
                            "Non-integer value on page '{}' for key '{}': {}"
                            .format(page, key, value)
                        )
                        continue
                    logging.debug("Adding value to {}, {}".format(key, value))
                    contents[key] += int(value)
                    category = key.split("_")[0]
                    contents[category + "_total"] += int(value)
    project_data = {
        "metrics": contents,
        "number_of_events": number_of_events
    }
    return project_data


def get_all_page_data(year):
    site = pywikibot.Site('se', 'wikimediachapter')
    cat = pywikibot.Category(site, 'Globala mätetal {}'.format(year))
    pages = cat.articles()
    data = OrderedDict()
    for page in pagegenerators.PreloadingGenerator(pages, 100):
        if page.title().endswith("/Global Metrics"):
            project_data = extract_all_data_on_page(page, year)
            if project_data:
                project_name = page.title().split(":")[1].split("/")[0]
                data[project_name] = project_data
        else:
            logging.warn(
                "Template found outside of Global Metrics subpage: {}."
                .format(page.title())
            )
    return data


def print_csv(data):
    writer = csv.writer(sys.stdout)
    meta_data = ["meta_data"]

	# Order projects according to file, if given.
    if args.project_order_file:
        ordered_data = {}
        order = []
        for l in open(args.project_order_file):
            name = l.strip()
            order.append(name)
        for project in order:
            if project in data:
                ordered_data[project] = data[project]
            else:
                # If no data was found for a project,
                # make a set of empty data.
                ordered_data[project] = {
                    "number_of_events": 0,
                    "metrics" : {metric: 0 for metric in METRIC_NAMES}
                }
        data = ordered_data

    writer.writerow([""] + list(data.keys()))
    for project in data.values():
        meta_data.append(
            "{} ({} st. event)"
            .format(datetime.date.today(), project["number_of_events"])
        )
    writer.writerow(meta_data)
    for key in METRIC_NAMES:
        printed_metric_names = data[list(data.keys())[0]]["metrics"]
        line = [key]
        for project in data:
            metric_value = str(data[project]["metrics"][key])
            line.append(metric_value)
        writer.writerow(line)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", "-y", required=True)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "project_order_file",
        help=("Path to a file containing project names in Swedish, one per line."
              "The projects in the output will have the same order."),
        nargs="?"
    )
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    print_csv(get_all_page_data(args.year))
