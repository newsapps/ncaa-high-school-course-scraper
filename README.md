NCAA High School Eligibility Center Portal Scraper
==================================================

Scraper for the NCAA's Elgibility Center high school portal.

This portal can be accessed at https://web3.ncaa.org/hsportal/exec/hsAction

TODO: Explain what this is, and why it matters.  

Assumptions
-----------

Machine assumptions:

* Python 2.7 (probably works with Python 3.2+ also)
* Virtualenvwrapper

Human assumptions (running):

* Command line familiarity

Human assumptions (updating):

* Intermediate Python programming
* Knowledge of HTML and HTTP requests
* Familiarity with requests package

Installation
------------

Clone this repository:

    git clone https://github.com/newsapps/ncaa-high-school-course-scraper.git ncaa-high-school-course-scraper

Create a virtualenv:

    mkvirtualenv ncaa-high-school-course-scraper

Change to the project directory:

    cd ncaa-high-school-course-scraper

Install dependencies:

    pip install -r requirements.txt

Running
-------

Scrape all denied courses for every school in a state:

    ./scrape_denied_courses.py IL > denied_courses.csv

Note that running the scraper caches HTML for the school list pages and the school detail pages in a subdirectory of the directory where you run the program named `_ncaa_courses_cache`.

Authors
-------

* Geoff Hing <geoffhing@gmail.com>
