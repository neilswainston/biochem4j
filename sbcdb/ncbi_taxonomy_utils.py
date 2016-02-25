'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import os
import re
import sys
import tarfile
import tempfile
import urllib
import sbcdb


__NCBITAXONOMY_URL = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz'


def load(source=__NCBITAXONOMY_URL):
    '''Loads NCBI Taxonomy data.'''
    nodes_filename, names_filename = __get_ncbi_taxonomy_files(source)
    nodes, rels = __parse_nodes(nodes_filename)
    __parse_names(nodes, names_filename)

    return [sbcdb.write_nodes(nodes.values())], [sbcdb.write_rels(rels)]


def __get_ncbi_taxonomy_files(source):
    '''Downloads and extracts NCBI Taxonomy files.'''
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
    nodes = {}
    rels = []

    with open(filename, 'r') as textfile:
        for line in textfile:
            tokens = [x.strip() for x in line.split('|')]
            tax_id = tokens[0]

            if tax_id is not '1':
                rels.append([tax_id, 'is_a', tokens[1]])

            nodes[tax_id] = {'taxonomy:ID': tax_id,
                             ':LABEL': 'Organism;' + tokens[2]}

    return nodes, rels


def __parse_names(nodes, filename):
    '''Parses names file.'''

    with open(filename, 'r') as textfile:
        for line in textfile:
            tokens = [x.strip() for x in line.split('|')]
            node = nodes[tokens[0]]

            if 'name' not in node:
                node['name'] = __encode(tokens[1])
                node['names:string[]'] = set([node['name']])
            else:
                node['names:string[]'].add(__encode(tokens[1]))


def __encode(string):
    '''Encodes string, removing problematic characters.'''
    return re.sub('[\'\",;]', ' ', string).strip()


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
