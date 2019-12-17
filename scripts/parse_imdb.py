import pandas as pd
# from scrapely import Scraper
from os import path
from bs4 import BeautifulSoup
import json
from pprint import pprint
from pathlib import Path

def discover_files(path_root, file_ext="html"):
    """Discover html files
    :param path_root: Path to search for files with matching extension
    :returns: list -- list of files and absolute path
    """
    list_files = []
    for filename in Path(path_root).rglob(f'*.{file_ext}'):
        list_files.append(str(filename))
    return list_files


def parse_review_file(path_file):
    """Parse a movie review from imdb.com
    
    :param path_file: Absolute path to load/read. 
    :returns: dict -- a dictionary or parsed information from the html file
    """
    with open(path_file, 'rt') as f:
        return parse_review(f.read())
    
    
def parse_review(html_text):
    """Parse a movie review from imdb.com
    
    :param html_text: Content of a file to be parsed. 
    :returns: dict -- a dictionary or parsed information from the html file
    """
    review_info = {}
    soup = BeautifulSoup(html_text)
    if soup.head is None or soup.body is None:
        return None

    for obj in soup.head.find_all('script', {"type" : "application/ld+json"}):  # special embedded JSON section
        parsed = json.loads(obj.string)
        review_info['title'] = parsed['name']
        review_info['url'] = parsed['url']
        if 'image' in parsed:
            review_info['poster'] = parsed['image']
        if 'genre' in parsed:
            review_info['genre'] = parsed['genre']
        if 'description' in parsed:
            review_info['brief_oneline'] = parsed['description']
        if 'review' in parsed:
            review_info['summary'] = parsed['review']['reviewBody']
        if 'contentRating' in parsed:
            review_info['rating'] = parsed['contentRating']
        if 'duration' in parsed:
            review_info['duration_markup'] = parsed['duration']  # PT1H49M
        if 'keywords' in parsed:
            review_info['keywords'] = parsed['keywords'].split(',')
        if 'datePublished' in parsed:
            review_info['release'] = parsed['datePublished']  # "1990-07-18"
        if 'aggregateRating' in parsed:
            review_info['scores'] = {}
            review_info['scores']['overall'] = parsed['aggregateRating']['ratingValue']
            review_info['scores']['min'] = parsed['aggregateRating']['worstRating']
            review_info['scores']['max'] = parsed['aggregateRating']['bestRating']
            review_info['scores']['count'] = parsed['aggregateRating']['ratingCount']
        # print(parsed)
        
        for type_val in ['actor', 'director', 'creator']:  # pull lists for each of these
            if type_val in parsed:
                review_info[type_val] = []
                for subobj in parsed[type_val]:
                    if type(subobj) != str and 'name' in subobj:
                        review_info[type_val].append(subobj['name'])

    review_info['details'] = {}
    for obj in soup.body.find_all('div', {'id': 'titleDetails'}):  # lots of production details
        for subobj in obj.find_all('div', {'class': 'txt-block'}):  
            type_block = ' '.join(subobj.stripped_strings)
            list_str = [v.strip() for v in list(subobj.stripped_strings) if len(v) > 2]
            if 'Budget' in type_block:
                review_info['details']['money_budget'] = list_str[1]
            elif 'Opening Weekend USA' in type_block:
                review_info['details']['money_opening'] = list_str[1]
            elif 'Gross USA' in type_block:
                review_info['details']['money_gross'] = list_str[1]
            elif 'Cumulative Worldwide Gross' in type_block:
                review_info['details']['money_gross_world'] = list_str[1]
            elif 'Runtime' in type_block:
                review_info['duration'] = list_str[1]
            elif 'Production Co' in type_block:
                review_info['details']['production'] = list_str

    if review_info['details']:  # needed some details
        return review_info
    return None
   