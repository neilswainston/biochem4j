'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import math
import sys

from sbcdb import chebi_utils, kegg_utils, mnxref_utils, rhea_utils
from synbiochem.utils import chem_utils


def load(url, organisms=None):
    '''Loads data into neo4j from a number of sources.'''
    # chebi_utils.load(url)
    mnxref_utils.load(url)
    rhea_utils.load(url)
    kegg_utils.load(url, organisms)


def normalise_masses(properties):
    '''Removes ambiguity in mass values by recalculating according to chemical
    formula.'''
    properties.pop('mass', None)

    if 'formula' in properties and properties['formula'] is not None:
        mono_mass = chem_utils.get_molecular_mass(properties['formula'])

        if not math.isnan(mono_mass):
            properties['monoisotopic_mass'] = mono_mass


def main(argv):
    '''main method'''
    load(*argv)

if __name__ == "__main__":
    main([sys.argv[1], sys.argv[2:]])
