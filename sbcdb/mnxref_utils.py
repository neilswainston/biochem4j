'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys

import libchebipy

from synbiochem.design.mnxref import MnxRefReader
from synbiochem.utils import chem_utils as chem_utils
import sbcdb


def load(reaction_manager):
    '''Loads MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''
    # Read mnxref data and generate nodes:
    reader = MnxRefReader()
    chem_nodes = __get_chem_nodes(reader.get_chem_data())
    rels = __add_reac_nodes(reader.get_reac_data(),
                            chem_nodes,
                            reaction_manager)

    return [sbcdb.write_nodes(chem_nodes.values(), 'Chemical')], \
        [sbcdb.write_rels(rels, 'Reaction', 'Chemical')]


def __get_chem_nodes(chem_data):
    '''Get chemical nodes from data.'''
    chem_nodes = {}

    for properties in chem_data.values():
        __add_chem_node(properties, chem_nodes)

    return chem_nodes


def __add_reac_nodes(reac_data, chem_nodes, reaction_manager):
    '''Get reaction nodes from data.'''
    rels = []

    for properties in reac_data.values():
        mnx_id = properties.pop('id')
        reac_id = reaction_manager.add_reaction('mnx', mnx_id, properties)

        for prt in chem_utils.parse_equation(properties.pop('equation')):
            chem_id = prt[0] \
                if prt[0] in chem_nodes \
                else __add_chem_node({'id': prt[0]}, chem_nodes)

            rels.append([reac_id, 'has_reactant', chem_id,
                         {'stoichiometry:float': prt[1]}])

    return rels


def __add_chem_node(properties, chem_nodes):
    '''Adds a Chemical node with given id to the graph.'''
    if 'chebi' in properties:
        chebi_entity = libchebipy.ChebiEntity(properties['chebi'])

        if chebi_entity.get_parent_id() is not None:
            properties['chebi'] = chebi_entity.get_parent_id()

    sbcdb.normalise_masses(properties)

    reac_id = properties.pop('id')
    properties[':LABEL'] = 'Chemical'
    properties['mnx:ID(Chemical)'] = reac_id

    chem_nodes[reac_id] = properties

    return reac_id


def main(argv):
    '''main method'''
    load(*argv)

if __name__ == '__main__':
    main(sys.argv[:1])
