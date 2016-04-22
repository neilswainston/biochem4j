'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from collections import Iterable
import csv
import math
import subprocess
import sys
import tempfile

from sbcdb import chebi_utils, enzyme_utils, kegg_utils, mnxref_utils, \
    ncbi_taxonomy_utils, rhea_utils
from synbiochem.utils import chem_utils


__PTH = '/Applications/Neo4j Community Edition.app/Contents/Resources/app/bin/'


def load(db_loc):
    '''Loads data into neo4j from a number of sources.'''
    enzyme_source = enzyme_utils.EnzymeSource()
    files = []
    files.append(chebi_utils.load())
    files.append(ncbi_taxonomy_utils.load())
    files.append(mnxref_utils.load())
    files.append(kegg_utils.load(enzyme_source))
    files.append(rhea_utils.load(enzyme_source))
    files.append(([write_nodes(enzyme_source.get_enzyme_nodes(), 'Enzyme')],
                  [write_rels(enzyme_source.get_org_enz_rels(),
                              'Organism', 'Enzyme')]))

    __create_db(db_loc, files)


def write_nodes(nodes, group):
    '''Writes Nodes to csv file.'''
    fle = tempfile.NamedTemporaryFile(suffix='.txt', prefix=group + '_',
                                      delete=False)

    nodes = [{key: __get_value(value) for key, value in node.iteritems()}
             for node in nodes]

    with open(fle.name, 'w') as node_file:
        dict_writer = csv.DictWriter(
            node_file, list(set().union(*(d.keys() for d in nodes))),
            restval=None)
        dict_writer.writeheader()
        dict_writer.writerows(nodes)

    return fle.name


def write_rels(rels, group_start, group_end):
    '''Writes Relationships to csv file.'''
    fle = tempfile.NamedTemporaryFile(delete=False)
    all_keys = [x.keys() for rel in rels for x in rel if isinstance(x, dict)]
    keys = list(set([x for sub in all_keys for x in sub]))

    with open(fle.name, 'w') as textfile:
        textfile.write(','.join([':START_ID(' + group_start + ')',
                                 ':TYPE',
                                 ':END_ID(' + group_end + ')'] + keys) +
                       '\n')

        for rel in rels:
            textfile.write(','.join(rel[:3] + [str(rel[3][key])
                                               for key in keys]) + '\n')

    return fle.name


def normalise_masses(properties):
    '''Removes ambiguity in mass values by recalculating according to chemical
    formula.'''
    properties.pop('mass', None)

    if 'formula' in properties and properties['formula'] is not None:
        mono_mass = chem_utils.get_molecular_mass(properties['formula'])

        if not math.isnan(mono_mass):
            properties['monoisotopic_mass'] = mono_mass


def __get_value(value):
    '''Formats arrays as "x;y;x"'''
    return ';'.join(value) \
        if not isinstance(value, str) and isinstance(value, Iterable) \
        else value


def __create_db(db_loc, files):
    '''Creates the database from csv files.'''
    files = [list(elem) for elem in zip(*files)]
    files = [sorted([item for f in fle for item in f]) for fle in files]

    for i in range(len(files[0])):
        files[0].insert(i * 2, '--nodes')

    for i in range(len(files[1])):
        files[1].insert(i * 2, '--relationships')

    params = [__PTH + 'neo4j-import', '--into', db_loc] + files[0] + files[1]

    print str(params)

    subprocess.call(params)


def main(argv):
    '''main method'''
    load(*argv)

if __name__ == '__main__':
    main(sys.argv[1:])
