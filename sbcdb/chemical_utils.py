'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import math

from sbcdb import build
from synbiochem.utils import chem_utils


class ChemicalManager(object):
    '''Class to implement a manager of Chemical data.'''

    def __init__(self):
        '''Constructor.'''
        self.__nodes = {}
        self.__chem_ids = {}

    def get_files(self):
        '''Gets neo4j import files.'''
        return ([build.write_nodes(self.__nodes.values(), 'Chemical')],
                [])

    def add_chemical(self, source, chem_id, properties):
        '''Adds a chemical to the collection of nodes, ensuring uniqueness.'''
        chem_id = self.__chem_ids[source + chem_id] \
            if source + chem_id in self.__chem_ids else chem_id

        if 'charge' in properties:
            properties['charge:int'] = int(properties.pop('charge'))

        if chem_id not in self.__nodes:
            properties[':LABEL'] = 'Chemical'
            properties['id:ID(Chemical)'] = chem_id
            properties['source'] = source
            properties[source] = chem_id

            _normalise_masses(properties)
            self.__nodes[chem_id] = properties

            if 'chebi' in properties:
                self.__chem_ids['chebi' + properties['chebi']] = chem_id
        else:
            self.__nodes[chem_id].update(properties)

        return chem_id


def _normalise_masses(properties):
    '''Removes ambiguity in mass values by recalculating according to chemical
    formula.'''
    properties.pop('mass', None)

    if 'formula' in properties and properties['formula'] is not None:
        mono_mass = chem_utils.get_molecular_mass(properties['formula'])

        if not math.isnan(mono_mass):
            properties['monoisotopic_mass:float'] = mono_mass
