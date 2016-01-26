'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import traceback

import py2neo

from synbiochem.design.mnxref import MnxRefReader
from synbiochem.utils import chem_utils as chem_utils
import grimoire.py2neo_utils


def load(url):
    '''Loads MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''
    # Read mnxref data and generate nodes:
    reader = MnxRefReader()
    chem_nodes = __get_chem_nodes(reader.get_chem_data())
    reac_nodes, reac_rels = __get_reac_nodes(reader.get_reac_data(),
                                             chem_nodes)

    # Contact Neo4j database, create Graph object:
    graph = grimoire.py2neo_utils.get_graph(url)

    # Submit chem data:
    grimoire.py2neo_utils.create(graph, chem_nodes.values())

    # Submit reac data:
    grimoire.py2neo_utils.create(graph, reac_nodes)
    grimoire.py2neo_utils.create(graph, reac_rels, 256)

    return graph


def __get_chem_nodes(chem_data):
    '''Get chemical nodes from data.'''
    chem_nodes = {}

    for properties in chem_data.values():
        __add_chem_node(properties, chem_nodes)

    return chem_nodes


def __get_reac_nodes(reac_data, chem_nodes):
    '''Get reaction nodes from data.'''
    reac_nodes = []
    reac_rels = []

    for properties in reac_data.values():
        try:
            node = py2neo.Node.cast(properties)
            node.labels.add('Reaction')
            reac_nodes.append(node)

            for prt in chem_utils.parse_equation(properties.pop('equation')):
                target_chem_node = chem_nodes[prt[0]] \
                    if prt[0] in chem_nodes \
                    else __add_chem_node({'id': prt[0]}, chem_nodes)

                reac_rels.append(py2neo.rel(node, 'HAS_REACTANT',
                                            target_chem_node,
                                            stoichiometry=prt[1]))
        except ValueError:
            print traceback.print_exc()

    return reac_nodes, reac_rels


def __add_chem_node(properties, chem_nodes):
    '''Adds a Metabolite node with given id to the graph.'''
    node = py2neo.Node.cast(properties)
    node.labels.add('Metabolite')
    chem_nodes[properties['id']] = node
    return node


if __name__ == '__main__':
    load(sys.argv[1])
