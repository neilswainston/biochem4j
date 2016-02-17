'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import py2neo

from synbiochem.utils import sequence_utils
import sbcdb


def submit(graph, data, source):
    '''Submit data to the graph.'''
    # Create / find Reaction nodes:
    reac_nodes = __create_reac_nodes(data, source)

    # Create Enzyme nodes and relationships:
    enzyme_nodes, rels = __create_enzyme_nodes(data, source, reac_nodes)

    # Get Uniprot details:
    organism_nodes = __get_uniprot_data(enzyme_nodes, rels, source)

    # Submit to neo4j:
    sbcdb.py2neo_utils.create(
        graph, reac_nodes, match_criteria=[('Reaction', source)])
    sbcdb.py2neo_utils.create(
        graph, enzyme_nodes, match_criteria=[('Enzyme', 'uniprot')])
    sbcdb.py2neo_utils.create(
        graph, organism_nodes, match_criteria=[('Organism', 'taxonomy')])
    sbcdb.py2neo_utils.create(graph, rels, 256)


def __create_reac_nodes(data, source):
    '''Creates reaction nodes.'''
    reac_nodes = {}

    for reac_id in data:
        if reac_id not in reac_nodes:
            reac_nodes[reac_id] = py2neo.Node.cast(
                'Reaction', {source: reac_id})

    return reac_nodes


def __create_enzyme_nodes(data, source, reac_nodes):
    '''Creates enzyme nodes.'''
    enzyme_nodes = {}
    rels = {}

    for reac_id, uniprot_ids in data.iteritems():
        for uniprot_id in uniprot_ids:
            if uniprot_id not in enzyme_nodes:
                enzyme_nodes[uniprot_id] = py2neo.Node.cast(
                    'Enzyme', {'uniprot': uniprot_id})

            rels[len(rels)] = py2neo.rel(reac_nodes[reac_id], 'catalysed_by',
                                         enzyme_nodes[uniprot_id],
                                         source=source)

    return enzyme_nodes, rels


def __get_uniprot_data(enzyme_nodes, rels, source):
    '''Gets Uniprot data.'''
    organism_nodes = {}

    fields = ['entry name', 'protein names', 'organism-id']
    uniprot_values = sequence_utils.get_uniprot_values(enzyme_nodes.keys(),
                                                       fields)

    for uniprot_id, uniprot_value in uniprot_values.iteritems():
        uniprot_value.pop('Entry')

        organism_id = uniprot_value.pop('Organism ID')

        if organism_id not in organism_nodes:
            organism_nodes[organism_id] = py2neo.Node.cast(
                'Organism', {'taxonomy': organism_id})

        for key, value in uniprot_value.iteritems():
            enzyme_nodes[uniprot_id][key] = value

        rels[len(rels)] = py2neo.rel(organism_nodes[organism_id], 'expresses',
                                     enzyme_nodes[uniprot_id],
                                     source=source)

    return organism_nodes
