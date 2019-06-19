
import re

import requests

r = requests.get('https://gist.githubusercontent.com/jamesbar2/1c677c22df8f21e869cca7e439fc3f5b/raw/21662445653ac861f8ab81caa8cfaee3185aed15/postal-codes.json')
data = r.json()

country_regex_dict = {}

for d in data:
    country_regex_dict[d["Country"]] = re.compile(d["Regex"])

country_list = list(country_regex_dict.keys())

