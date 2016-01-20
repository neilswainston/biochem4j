'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import math
import sys

import libchebipy
import py2neo

import grimoire


def load(url):
    '''Loads ChEBI data from libChEBIpy.'''
    nodes = {}
    rels = []

    # Add root, applying recursion:
    __add_node('CHEBI:24431', nodes, rels)

    # Contact Neo4j database, create Graph object:
    graph = grimoire.py2neo_utils.get_graph(url)
    grimoire.py2neo_utils.create(graph, nodes.values())
    grimoire.py2neo_utils.create(graph, rels, 8192)


def __add_node(chebi_id, nodes, rels):
    '''Constructs a node from libChEBI.'''
    if chebi_id not in nodes:
        properties = {}
        entity = libchebipy.ChebiEntity(chebi_id)

        properties['id'] = entity.get_id()
        properties['name'] = entity.get_name()
        properties['formula'] = entity.get_formula()
        properties['charge'] = 0 if math.isnan(entity.get_charge()) \
            else entity.get_charge()

        if not math.isnan(entity.get_mass()):
            properties['mass'] = entity.get_mass()

        properties['inchi'] = entity.get_inchi()
        properties['smiles'] = entity.get_smiles()

        node = py2neo.Node.cast(properties)
        node.labels.add('Chemical')
        nodes[chebi_id] = node

        for incoming in entity.get_incomings():
            target_id = incoming.get_target_chebi_id()
            target_node = __add_node(target_id, nodes, rels)
            rels.append(py2neo.rel(target_node, incoming.get_type(), node))
    else:
        node = nodes[chebi_id]

    return node


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
