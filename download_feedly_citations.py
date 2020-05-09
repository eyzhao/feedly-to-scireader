'''Web crawler that downloads citations from Google Scholar based on JSON output of Feedly

Usage: download_feedly_citations.py -i INPUT -o OUTPUT [ -s SOURCES ]

Options:
    -i --input INPUT            Path to JSON output from Feedly
    -o --output OUTPUT          Path to output file containing google scholar citations in bibtex format
    -s --sources SOURCES        Path to a file with names of desired sources, one per line
'''

import pandas as pd
from docopt import docopt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

CHROMEDRIVER = 'C:/Users/Eric/Software/chromedriver.exe'
download_folder = 'C:/Users/Eric/Documents/code/feedly/citations'

def import_data(input_path):
    return pd.read_json(input_path)

def filter_data(data, sources_path):
    sources = pd.DataFrame([s.strip() for s in open(sources_path)], columns = ['source'])
    filtered = data.merge(sources, left_on='source_name', right_on='source', how='inner')
    return(filtered)

def download(browser, title):
    #browser.get('https://scholar.google.com/')
    browser.get('https://scholar.google.com')
    browser.execute_script("document.querySelector('#gs_hdr_frm').getElementsByClassName('gs_in_txt')[0].value = '{}'".format(title))
    browser.find_element_by_id('gs_hdr_tsb').click()
    browser.find_element_by_class_name('gs_or_cit').click()
    time.sleep(0.5)
    browser.find_element_by_class_name('gs_citi').click()
    time.sleep(0.5)
    content = browser.find_element_by_tag_name('pre').get_attribute('innerHTML')
    return(content)


if __name__ == '__main__':
    args = docopt(__doc__)
    data = import_data(args['--input'])
    if (args['--sources']):
        data = filter_data(data, args['--sources'])
    data.to_csv('dump.tsv', sep='\t', index=False)

    options = webdriver.ChromeOptions()
    profile = {"plugins.plugins_list": [{"enabled": False,
                                         "name": "Chrome PDF Viewer"}],
               "download.default_directory": download_folder,
               "download.extensions_to_open": "",
               "download.prompt_for_download": False,
               "profile.default_content_settings.popups": 0,
               "directory_upgrade": True
              }
    options.add_experimental_option("prefs", profile)
    options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(chrome_options = options, executable_path = CHROMEDRIVER)

    output_string = ''
    i = 0
    while i < len(data.values):
        row = data.values[i]
        title = row[2]
        try:
            bibtex = download(browser, title)
            output_string += bibtex + '\n\n'
            i += 1
        except:
            instruction = input('Error occured. Skip [y/N]? ')
            if instruction.strip() == 'y':
                i += 1

    with open(args['--output'], 'w') as output:
        output.write(output_string)
