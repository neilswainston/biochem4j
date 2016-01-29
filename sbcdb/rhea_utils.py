'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import tempfile
import urllib

import py2neo

from synbiochem.utils import sequence_utils
import sbcdb


__RHEA_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/rhea/tsv/rhea2uniprot.tsv'


def load(url, source=__RHEA_URL):
    '''Loads NCBI Taxonomy data.'''
    # Parse data:
    temp_file = tempfile.NamedTemporaryFile()
    urllib.urlretrieve(source, temp_file.name)
    data = __parse(temp_file.name)

    # Contact Neo4j database, create Graph object:
    graph = sbcdb.py2neo_utils.get_graph(url)
    __submit(graph, data)


def __parse(filename):
    '''Parses file.'''
    data = {}

    with open(filename, 'r') as textfile:
        next(textfile)

        for line in textfile:
            try:
                tokens = line.split('\t')

                if len(tokens) == 4:
                    data[tokens[0]] = tokens[3].strip()
                    data[tokens[2]] = tokens[3].strip()
            except IndexError:
                print line

    return data


def __submit(graph, data):
    '''Submit data to the graph.'''
    rhea_nodes = {}
    uniprot_nodes = {}
    rels = []

    # Create nodes:
    for rhea_id, uniprot_id in data.iteritems():
        if rhea_id not in rhea_nodes:
            rhea_node = py2neo.Node.cast(
                {'id': 'rhea:' + rhea_id, 'rhea': rhea_id})
            rhea_node.labels.add('Reaction')
            rhea_nodes[rhea_id] = rhea_node

        if uniprot_id not in uniprot_nodes:
            uniprot_node = py2neo.Node.cast({'id': uniprot_id})
            uniprot_node.labels.add('Enzyme')
            uniprot_nodes[uniprot_id] = uniprot_node

        rels.append(py2neo.rel(rhea_nodes[rhea_id],
                               'catalysed_by',
                               uniprot_nodes[uniprot_id]))

    # Get Uniprot details:
    fields = ['entry name', 'protein names', 'organism-id']
    uniprot_values = sequence_utils.get_uniprot_values(uniprot_nodes.keys(),
                                                       fields)

    for uniprot_id, uniprot_value in uniprot_values.iteritems():
        uniprot_node[uniprot_id].properties.expand(uniprot_value)

    sbcdb.py2neo_utils.create(graph, rhea_nodes.values())
    sbcdb.py2neo_utils.create(graph, uniprot_nodes.values())
    sbcdb.py2neo_utils.create(graph, rels, 256)


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
