'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import tempfile
import urllib
import zipfile

import grimoire


__NCBITAXONOMY_URL = 'ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip'

def load(url, source=__NCBITAXONOMY_URL):
    '''Loads NCBI Taxonomy data.'''

    # Contact Neo4j database, create Graph object:
    graph = grimoire.py2neo_utils.get_graph(url)

    __get_ncbi_taxonomy_files__(source)


def __get_ncbi_taxonomy_files__(source):
    temp_dir = tempfile.gettempdir()
    temp_zipfile = tempfile.NamedTemporaryFile()
    urllib.urlretrieve(source, temp_zipfile.name)

    zpfile = zipfile.ZipFile(temp_zipfile)
    zpfile.extractall(temp_dir)

    zpfile.close()
    temp_zipfile.close()


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
