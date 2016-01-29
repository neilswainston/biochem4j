'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import os
import sys
import tarfile
import tempfile
import urllib

import py2neo

import sbcdb


__NCBITAXONOMY_URL = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz'


def load(url, source=__NCBITAXONOMY_URL):
    '''Loads NCBI Taxonomy data.'''
    # Parse data:
    nodes_filename, names_filename = __get_ncbi_taxonomy_files__(source)
    data = __parse_nodes(nodes_filename)
    __parse_names(data, names_filename)

    # Contact Neo4j database, create Graph object:
    graph = sbcdb.py2neo_utils.get_graph(url)
    __submit(graph, data)


def __get_ncbi_taxonomy_files__(source):
    temp_dir = tempfile.gettempdir()
    temp_gzipfile = tempfile.NamedTemporaryFile()
    urllib.urlretrieve(source, temp_gzipfile.name)

    temp_tarfile = tarfile.open(temp_gzipfile.name, 'r:gz')
    temp_tarfile.extractall(temp_dir)

    temp_gzipfile.close()
    temp_tarfile.close()

    return os.path.join(temp_dir, 'nodes.dmp'), \
        os.path.join(temp_dir, 'names.dmp')


def __parse_nodes(filename):
    '''Parses nodes file.'''
    data = {}

    with open(filename, 'r') as textfile:
        for line in textfile:
            tokens = [x.strip() for x in line.split('|')]
            data[tokens[0]] = {'parent_id': tokens[1], 'rank': tokens[2]}

    return data


def __parse_names(data, filename):
    '''Parses names file.'''
    with open(filename, 'r') as textfile:
        for line in textfile:
            tokens = [x.strip() for x in line.split('|')]
            typ = tokens[3]

            if typ == 'synonym':
                if 'synonym' not in data[tokens[0]]:
                    data[tokens[0]][typ] = [tokens[1]]
                else:
                    data[tokens[0]][typ].append(tokens[1])
            else:
                data[tokens[0]][typ] = tokens[1]


def __submit(graph, data):
    '''Submit data to the graph.'''
    nodes = {}
    rels = []

    # Create nodes:
    for node_id, properties in data.iteritems():
        rank = properties.pop('rank')
        properties['id'] = node_id

        node = py2neo.Node.cast(properties)
        node.labels.add('Taxonomic rank')
        node.labels.add(rank)
        nodes[node_id] = node

    # Create relationships;
    for node_id in data:
        node = nodes[node_id]
        parent_id = node.properties.pop('parent_id')

        if node_id != '1':
            rels.append(py2neo.rel(node, 'is_a', nodes[parent_id]))

    sbcdb.py2neo_utils.create(graph, nodes.values())
    sbcdb.py2neo_utils.create(graph, rels, 256)


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
