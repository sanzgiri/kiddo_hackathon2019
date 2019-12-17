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
    """Parse a movie review from commonsensemedia.org
    
    :param path_file: Absolute path to load/read. 
    :returns: dict -- a dictionary or parsed information from the html file
    """
    with open(path_file, 'rt') as f:
        return parse_review(f.read())
    
    
def parse_review(html_text):
    """Parse a movie review from commonsensemedia.org
    
    :param html_text: Content of a file to be parsed. 
    :returns: dict -- a dictionary or parsed information from the html file
    """
    review_info = {}
    soup = BeautifulSoup(html_text)

    for obj in soup.head.find_all('script', {"type" : "application/ld+json"}):  # special embedded JSON section
        parsed = json.loads(obj.string)
        review_info['title'] = parsed['name']
        review_info['brief'] = parsed['description']
        review_info['url'] = parsed['url']
        review_info['summary'] = parsed['reviewBody']
        review_info['rating'] = parsed['reviewRating']['ratingValue']
        if 'itemReviewed' in parsed:
            review_info['url_imdb'] = parsed['itemReviewed']['sameAs']
        # print(parsed)
    for obj in soup.head.find_all('meta', {'name': "keywords"}):  # keywords
        review_info['keywords'] = obj['content'].split(',')

    for obj in soup.body.find_all('div', {'class': "field-name-field-product-image"}):  # poster image
        subobj = obj.find('img')
        if subobj is not None:
            review_info['poster'] = subobj['src']

    for obj in soup.body.find_all('div', {'class':'user-review-statistics'}):  # ratings by age
        type_obj = 'adult' if 'adult' in obj.attrs['class'] else 'child'
        subobj = obj.find('div', {'class':'age'})
        if subobj is not None:
            review_info[f'age_{type_obj}'] = obj.find('div', {'class':'age'}).string
            review_info[f'age_{type_obj}_count'] = obj.find('a', {'class':'link-all-user-reviews'}).string

    obj = soup.body.find('div', {'class':'pane-node-field-one-liner'})  # one-line info
    if obj is not None:
        review_info['brief_oneline'] = obj.find('div', {'class':'field-name-field-one-liner'}).string

    for obj in soup.body.find_all('div', {'class':'pane-product-subtitle'}):  # movie info
        idx = 0
        parts = ['rating', 'release_year', 'duration']
        for subobj in obj.find_all('li'):    
            review_info[parts[idx]] = subobj.string
            idx += 1

    for obj in soup.body.find_all('div', {'class':'field-name-field-parents-need-to-know'}):
        subobj = obj.find('p')
        if subobj is not None:
            review_info['summary_parents'] = " ".join(subobj.stripped_strings)

    review_info['scores'] = {}
    review_info['scores_text'] = {}
    for obj in soup.body.find_all('div', {'class':'entity-field-collection-item'}):  # critical ratings
        subobj = obj.find('div', {'class':'field-name-field-content-grid-type'})
        if subobj is not None:
            rating = [v for v in obj.find('div', {'class':'content-grid-rating'}).attrs['class'] \
                      if v.startswith('content') and not v.endswith('rating')]
            # print(rating)
            review_info['scores'][subobj.string] = rating[0][-1]  # ['content-grid-2'] -> 2
            # print(subobj) 
        subobj_text = obj.find('div', {'class':'field-name-field-content-grid-rating-text'})
        if subobj_text is not None:
            subobj_text = subobj_text.find('p')
        if subobj_text is not None:
            review_info['scores_text'][subobj.string] = subobj_text.string

    review_info['questions'] = []
    for obj in soup.body.find_all('div', {'class':'field-name-field-family-topics'}):  # discussion topics
        for subobj in obj.find_all('li'):
            val_test = subobj.strings
            if val_test:
                review_info['questions'].append(' '.join(subobj.strings).strip())

    review_info['details'] = {}
    obj_details = soup.body.find('div', {'class':'pane-product-details'})
    if obj_details is not None:
        for obj in obj_details.find_all('li'):  # movie details
            rel_val = list(obj.strings)
            rel_name = rel_val.pop(0)
            rel_val = [v.strip() for v in rel_val if len(v) > 2]
            if len(rel_val):
                review_info['details'][rel_name] = rel_val if len(rel_val) > 1 else rel_val[0]

    if review_info['details']:  # needed some details
        return review_info
    return None
   