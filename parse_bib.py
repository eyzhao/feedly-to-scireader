'''Parse bibtex file and extract all titles

Usage: parse_bib.py -i INPUT -o OUTPUT

Options:
    -i --input INPUT            Path to input bibtex file
    -o --output OUTPUT          Path to output
'''

from docopt import docopt
import bibtexparser
import pandas as pd
from fuzzywuzzy import fuzz
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

def parse_bibtex(input_path):
    feedly = pd.read_csv('dump.tsv', sep='\t', encoding='ISO-8859-1')
    with open(input_path, encoding = "ISO-8859-1") as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    not_found = []
    feedly_titles = [f.upper().strip().replace('-', '') for f in feedly.title.tolist()]
    new_bibtex = []
    db = BibDatabase()
    db.entries = []

    for e in bib_database.entries:
        match_phrase = e['title'].upper().strip().replace('-', '')
        if match_phrase in feedly_titles:
            db.entries.append(e)
            continue

        for t in feedly_titles:
            max_fuzz = 0
            fuzz_ratio = fuzz.ratio(match_phrase, t)
            if fuzz_ratio > max_fuzz:
                max_fuzz = fuzz_ratio
            if fuzz_ratio > 80:
                db.entries.append(e)
                break
        else:
            print(str(max_fuzz) + ': ' + e['title'] + '\n')
            not_found.append(e['title'])
    print('{} entries removed'.format(len(not_found)))

    return(db)

if __name__ == '__main__':
    args = docopt(__doc__)
    filtered_bibtex = parse_bibtex(args['--input'])

    writer = BibTexWriter()
    with open(args['--output'], 'w') as bibfile:
        bibfile.write(writer.write(filtered_bibtex))


