'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import traceback

import libchebipy

from synbiochem.design.mnxref import MnxRefReader
from synbiochem.utils import chem_utils as chem_utils
import sbcdb


def load():
    '''Loads MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''
    # Read mnxref data and generate nodes:
    reader = MnxRefReader()
    chem_nodes = __get_chem_nodes(reader.get_chem_data())
    reac_nodes, rels = __get_reac_nodes(reader.get_reac_data(),
                                        chem_nodes)

    return [sbcdb.write_nodes(chem_nodes.values(), 'Chemical'),
            sbcdb.write_nodes(reac_nodes.values(), 'Reaction')], \
        [sbcdb.write_rels(rels, 'Reaction', 'Chemical')]


def __get_chem_nodes(chem_data):
    '''Get chemical nodes from data.'''
    chem_nodes = {}

    for properties in chem_data.values():
        __add_chem_node(properties, chem_nodes)

    return chem_nodes


def __get_reac_nodes(reac_data, chem_nodes):
    '''Get reaction nodes from data.'''
    reac_nodes = {}
    rels = []

    for properties in reac_data.values():
        try:
            mnx_id = properties.pop('id')

            properties[':LABEL'] = 'Reaction'
            properties['mnx:ID(Reaction)'] = mnx_id
            reac_nodes[mnx_id] = properties

            for prt in chem_utils.parse_equation(properties.pop('equation')):
                chem_id = prt[0] \
                    if prt[0] in chem_nodes \
                    else __add_chem_node({'id': prt[0]}, chem_nodes)

                rels.append([mnx_id, 'has_reactant', chem_id,
                             {'stoichiometry:float': prt[1]}])
        except ValueError:
            print traceback.print_exc()

    return reac_nodes, rels


def __add_chem_node(properties, chem_nodes):
    '''Adds a Chemical node with given id to the graph.'''
    if 'chebi' in properties:
        chebi_entity = libchebipy.ChebiEntity(properties['chebi'])

        if chebi_entity.get_parent_id() is not None:
            properties['chebi'] = chebi_entity.get_parent_id()

    sbcdb.normalise_masses(properties)

    mnx_id = properties.pop('id')
    properties[':LABEL'] = 'Chemical'
    properties['mnx:ID(Chemical)'] = mnx_id

    chem_nodes[mnx_id] = properties

    return mnx_id


def main(argv):
    '''main method'''
    load(*argv)

if __name__ == '__main__':
    main(sys.argv[:1])
