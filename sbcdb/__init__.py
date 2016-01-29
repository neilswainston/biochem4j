'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
from sbcdb import chebi_utils, mnxref_utils


def load(url):
    '''Loads data into neo4j from a number of sources.'''
    chebi_utils.load(url)
    mnxref_utils.load(url)


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
