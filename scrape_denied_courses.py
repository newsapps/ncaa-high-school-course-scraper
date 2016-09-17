#!/usr/bin/env python

import argparse
import csv
import os
import errno
from six.moves.html_parser import HTMLParser
import sys

from lxml.html.soupparser import fromstring
import requests

BASE_URL = "https://web3.ncaa.org/hsportal/exec/hsAction"
FAKE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36"
CACHE_DIR_NAME = "_ncaa_courses_cache"

def get_state_schools_html_cache_path(state_abbrev, cache_path):
    return os.path.join(cache_path, 'schools_' + state_abbrev + '.html')

def get_state_schools_html_from_cache(state_abbrev, cache_path):
    schools_html_path = get_state_schools_html_cache_path(state_abbrev,
        cache_path)

    with open(schools_html_path) as f:
        return f.read()

def save_state_schools_html_to_cache(state_abbrev, schools_html, cache_path):
    schools_html_path = get_state_schools_html_cache_path(state_abbrev,
        cache_path)

    with open(schools_html_path, 'w') as f:
        f.write(schools_html)

def fetch_state_schools(state_abbrev, user_agent=FAKE_USER_AGENT):
    data = {
        'hsCode': '',
        'ceebCode': '',
        'state': state_abbrev,
        'city': '',
        'name': '',
        'hsActionSubmit': 'Search',
    }

    headers = {
        'User-Agent': user_agent
    }

    r = requests.post(BASE_URL, data=data, headers=headers)
    return r.content

def parse_state_schools(schools_html):
    schools = []

    root = fromstring(schools_html)
    schools_form = root.cssselect('form[name="selectHsForm"]')[0]
    for row in schools_form.cssselect('tr'):
        form_input = row.cssselect('input[name="hsCode"]')
        if len(form_input) == 0:
            continue

        school = {}

        school['hs_code'] = form_input[0].get('value')

        cols = row.cssselect('td')

        school['high_school_name'] = cols[1].text_content().strip()
        school['city'] = cols[2].text_content().strip()
        school['state'] = cols[3].text_content().strip()[:2]

        schools.append(school)

    return schools

def fetch_school_html(hs_code, user_agent=FAKE_USER_AGENT):
    data = {
        'hsCode': hs_code,
        'ceebCode': '',
        'state': '',
        'city': '',
        'name': '',
        'hsActionSubmit': 'Search',
    }

    headers = {
        'User-Agent': user_agent
    }

    r = requests.post(BASE_URL, data=data, headers=headers)
    return r.content

def get_school_html_cache_path(hs_code, cache_path):
    return os.path.join(cache_path, 'school_' + hs_code + '.html')

def get_school_html_from_cache(hs_code, cache_path):
    school_html_path = get_school_html_cache_path(hs_code, cache_path)

    with open(school_html_path) as f:
        return f.read()

def save_school_html_to_cache(hs_code, school_html, cache_path):
    school_html_path = get_school_html_cache_path(hs_code, cache_path)

    with open(school_html_path, 'w') as f:
        f.write(school_html)

def parse_denied_courses(school_html):
    root = fromstring(school_html)
    denied_table = root.cssselect('#NcaaCrs_DeniedCategory_All')
    courses = []
    for tr in denied_table[0].cssselect('tr')[1:]:
        tables = tr.cssselect('table')
        try:
            subject = tables[0].cssselect('.hs_tableHeader')[0].text_content()
        except IndexError:
            continue

        for course_tr in tables[1].cssselect('tbody tr'):
            course = {}

            tds = course_tr.cssselect('td')

            course['subject'] = subject
            course['course_weight'] = tds[0].text_content().strip()
            h = HTMLParser()
            course['title'] = h.unescape(tds[1].text_content().strip())
            course['notes'] = tds[2].text_content().strip()
            course['max_credits'] = tds[3].text_content().strip()
            course['ok_through'] = tds[4].text_content().strip()
            course['reason_code'] = tds[5].text_content().strip()
            course['disability_course'] = tds[6].text_content().strip()

            courses.append(course)

    return courses


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape denied courses")
    parser.add_argument('state', help='State abbreviation')
    parser.add_argument('--cache-path',
        default=os.path.join(os.getcwd(), CACHE_DIR_NAME),
        help="Cache directory")
    args = parser.parse_args()

    make_sure_path_exists(args.cache_path)

    try:
        schools_html = get_state_schools_html_from_cache(args.state, args.cache_path)
    except IOError:
        schools_html = fetch_state_schools(args.state)
        save_state_schools_html_to_cache(args.state, schools_html, args.cache_path)

    schools = parse_state_schools(schools_html)


    fieldnames = [
        'hs_code',
        'high_school_name',
        'city',
        'state',
        'subject',
        'course_weight',
        'title',
        'notes',
        'max_credits',
        'ok_through',
        'reason_code',
        'disability_course',
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    for school in schools:
        try:
            school_html = get_school_html_from_cache(school['hs_code'], args.cache_path)
        except IOError:
            school_html = fetch_school_html(school['hs_code'])
            save_school_html_to_cache(school['hs_code'], school_html, args.cache_path)

        courses = parse_denied_courses(school_html)

        for course in courses:
            course.update(**school)
            writer.writerow(course)
