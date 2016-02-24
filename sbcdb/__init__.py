'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import math
import subprocess
import sys

from sbcdb import ncbi_taxonomy_utils
from synbiochem.utils import chem_utils

__PTH = '/Applications/Neo4j Community Edition.app/Contents/Resources/app/bin/'


def load(db_loc):
    '''Loads data into neo4j from a number of sources.'''
    files = []
    files.append(ncbi_taxonomy_utils.load())
    __create_db(db_loc, files)


def normalise_masses(properties):
    '''Removes ambiguity in mass values by recalculating according to chemical
    formula.'''
    properties.pop('mass', None)

    if 'formula' in properties and properties['formula'] is not None:
        mono_mass = chem_utils.get_molecular_mass(properties['formula'])

        if not math.isnan(mono_mass):
            properties['monoisotopic_mass'] = mono_mass


def __create_db(db_loc, files):
    '''Creates the database from csv files.'''
    files = [list(elem) for elem in zip(*files)]

    for i in range(len(files[0])):
        files[0].insert(i * 2, '--nodes')

    for i in range(len(files[1])):
        files[1].insert(i * 2, '--relationships')

    params = [__PTH + 'neo4j-import', '--into', db_loc] + files[0] + files[1]

    print str(params)

    subprocess.call(params)


def main(argv):
    '''main method'''
    load(*argv)

if __name__ == '__main__':
    main(sys.argv[1:])
