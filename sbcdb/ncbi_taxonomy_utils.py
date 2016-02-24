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


__NCBITAXONOMY_URL = 'ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz'


def load(source=__NCBITAXONOMY_URL):
    '''Loads NCBI Taxonomy data.'''
    nodes_filename, names_filename = __get_ncbi_taxonomy_files(source)
    ids, parent_ids, ranks = __parse_nodes(nodes_filename)
    names, all_names = __parse_names(names_filename)

    return __write_nodes(ids, names, all_names, ranks), \
        __write_rels(parent_ids)


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
    ids = []
    parent_ids = {}
    ranks = {}

    with open(filename, 'r') as textfile:
        for line in textfile:
            tokens = [x.strip() for x in line.split('|')]
            tax_id = tokens[0]
            ids.append(tax_id)
            parent_ids[tax_id] = tokens[1]
            ranks[tax_id] = tokens[2]

    return ids, parent_ids, ranks


def __parse_names(filename):
    '''Parses names file.'''
    names = {}
    all_names = {}

    with open(filename, 'r') as textfile:
        for line in textfile:
            tokens = [x.strip() for x in line.split('|')]
            tax_id = tokens[0]

            if tax_id not in names:
                name = __encode(tokens[1])
                names[tax_id] = name
                all_names[tax_id] = set([name])
            else:
                all_names[tax_id].add(__encode(tokens[1]))

    return names, all_names


def __write_nodes(ids, names, all_names, ranks):
    '''Write Node data to csv file.'''
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    with open(temp_file.name, 'w') as textfile:
        textfile.write('id:ID,taxonomy,name,names:string[],:LABEL\n')

        for tax_id in ids:
            textfile.write(','.join([tax_id,
                                     tax_id,
                                     names[tax_id],
                                     ';'.join(all_names[tax_id]),
                                     ';'.join(['Organism', ranks[tax_id]])]) +
                           '\n')

    return temp_file.name


def __write_rels(parent_ids):
    '''Write Relation data to csv file.'''
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    with open(temp_file.name, 'w') as textfile:
        textfile.write(':START_ID,:END_ID,:TYPE\n')

        for tax_id, parent_id in parent_ids.iteritems():
            if tax_id != '1':
                textfile.write(','.join([tax_id, parent_id, 'is_a']) + '\n')

    return temp_file.name


def __encode(string):
    '''Encodes string, removing problematic characters.'''
    return re.sub('[\'\",;]', ' ', string).strip()


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
