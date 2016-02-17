'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import traceback

import libchebipy
import py2neo

from synbiochem.design.mnxref import MnxRefReader
from synbiochem.utils import chem_utils as chem_utils
import sbcdb


def load(url, verbose=False):
    '''Loads MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''
    # Contact Neo4j database, create Graph object:
    graph = sbcdb.py2neo_utils.get_graph(url)

    # Read mnxref data and generate nodes:
    reader = MnxRefReader()
    chem_nodes = __get_chem_nodes(reader.get_chem_data())

    # Submit chem data:
    sbcdb.py2neo_utils.create(graph, chem_nodes, match_criteria=[('Chemical',
                                                                  'chebi')],
                              verbose=verbose)

    reac_nodes, reac_rels = __get_reac_nodes(reader.get_reac_data(),
                                             chem_nodes)

    # Submit reac data:
    sbcdb.py2neo_utils.create(graph, reac_nodes, verbose=verbose)
    sbcdb.py2neo_utils.create(graph, reac_rels, 256, verbose=verbose)

    return graph


def __get_chem_nodes(chem_data):
    '''Get chemical nodes from data.'''
    chem_nodes = {}

    for properties in chem_data.values():
        __add_chem_node(properties, chem_nodes)

    return chem_nodes


def __get_reac_nodes(reac_data, chem_nodes):
    '''Get reaction nodes from data.'''
    reac_nodes = {}
    reac_rels = {}

    for properties in reac_data.values():
        try:
            mnx_id = properties.pop('id')
            properties['mnx'] = mnx_id

            node = py2neo.Node.cast('Reaction', properties)
            reac_nodes[mnx_id] = node

            for prt in chem_utils.parse_equation(properties.pop('equation')):
                target_chem_node = chem_nodes[prt[0]] \
                    if prt[0] in chem_nodes \
                    else __add_chem_node({'id': prt[0]}, chem_nodes)

                reac_rels[len(reac_rels)] = py2neo.rel(node, 'has_reactant',
                                                       target_chem_node,
                                                       stoichiometry=prt[1])
        except ValueError:
            print traceback.print_exc()

    return reac_nodes, reac_rels


def __add_chem_node(properties, chem_nodes):
    '''Adds a Chemical node with given id to the graph.'''
    if 'chebi' in properties:
        chebi_entity = libchebipy.ChebiEntity(properties['chebi'])

        if chebi_entity.get_parent_id() is not None:
            properties['chebi'] = chebi_entity.get_parent_id()

    sbcdb.normalise_masses(properties)

    mnx_id = properties.pop('id')
    properties['mnx'] = mnx_id

    node = py2neo.Node.cast('Chemical', properties)
    chem_nodes[mnx_id] = node

    return node


if __name__ == '__main__':
    load(sys.argv[1], bool(sys.argv[2]))
