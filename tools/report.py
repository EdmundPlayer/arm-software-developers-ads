#/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import csv
from datetime import datetime, timedelta


'''
Recursive content search in d. Update list of articles older than period. Returns count of articles found
'''
def content_parser(d, period):
    count = 0
    result = {}
    l = os.listdir(d)
    for i in l:
        if i.endswith(".md") and not i.startswith("_"):
            count = count + 1
            logging.debug("Checking {}...".format(d+"/"+i))

            date = subprocess.run(["git", "log", "-1" ,"--format=%cs", d +"/" + i], stdout=subprocess.PIPE)
            # strip out '\n' and decode byte to string
            date = date.stdout.rstrip().decode("utf-8")
            logging.debug(date)

            # if empty, this is a temporary file which is not part of the repo
            if(date != ""):
                date = datetime.strptime(date, "%Y-%m-%d")
                # check if article is older than the period
                if date < datetime.now() - timedelta(days = period):
                    result[d + "/" + i] = "{} days ago".format((datetime.now() - date).days)

        # if this is a folder, let's get down one level deeper
        elif os.path.isdir(d + "/" + i):
            res, c = content_parser(d + "/" + i, period)
            result.update(res)
            count = count + c

    return [result, count]


'''
List pages older than a period in days
'''
def report(period):
    global verbosity, level

    orig = os.path.abspath(os.getcwd())

    # chdir to the root folder
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
    dname = ["content/install-tools",
             "content/learning-paths/cloud",
             "content/learning-paths/desktop_and_laptop",
             "content/learning-paths/embedded",
             "content/learning-paths/microcontroller",
             "content/learning-paths/mobile"]

    result = {}

    for d in dname:
        res, count = content_parser(d, period)
        result.update(res)
        logging.info("Found {} articles in {}. {} of them are outdated.".format(count, d, len(res)))

    fn="outdated_files.csv"
    fields=["File", "Last updated"]
    os.chdir(orig)
    logging.info("Results written in " + orig + "/" + fn)

    with open(fn, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = fields)
        writer.writeheader()
        for key in result.keys():
            csvfile.write("%s, %s\n" % (key, result[key]))

