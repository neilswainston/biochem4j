'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys

from synbiochem.design.brenda import BrendaReader
import sbcdb


def load(url, username, password):
    '''Loads BRENDA data.'''
    graph = sbcdb.py2neo_utils.get_graph(url)
    reader = BrendaReader(username, password)

    for ec_number, organism in __get_ec_organisms(graph):
        kcat_values = reader.get_kcat_values(ec_number, organism)
        print kcat_values

def __get_ec_organisms(graph):

def main(argv):
    '''main method'''
    load(*argv)


if __name__ == '__main__':
    main(sys.argv[1:])
