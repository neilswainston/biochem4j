'''
synbiochem (c) University of Manchester 2016

synbiochem is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from collections import Iterable
import csv
import os
from shutil import rmtree


class Writer(object):
    '''CSV file writer class for biochem4j files.'''

    def __init__(self, dest_dir):
        self.__nodes_dir = os.path.join(os.path.abspath(dest_dir), 'nodes')
        self.__rels_dir = os.path.join(os.path.abspath(dest_dir), 'rels')

        if os.path.exists(self.__nodes_dir):
            rmtree(self.__nodes_dir)

        os.makedirs(self.__nodes_dir)

        if os.path.exists(self.__rels_dir):
            rmtree(self.__rels_dir)

        os.makedirs(self.__rels_dir)

    def write_nodes(self, nodes, group):
        '''Writes Nodes to csv file.'''
        if not nodes:
            return None

        filename = os.path.join(self.__nodes_dir, group + '.csv')

        nodes = [{key: _get_value(value) for key, value in node.iteritems()}
                 for node in nodes]

        with open(filename, 'w') as node_file:
            dict_writer = csv.DictWriter(
                node_file, list(set().union(*(d.keys() for d in nodes))),
                restval=None)
            dict_writer.writeheader()
            dict_writer.writerows(nodes)

        return filename

    def write_rels(self, rels, group_start, group_end):
        '''Writes Relationships to csv file.'''
        if not rels:
            return None

        filename = os.path.join(self.__rels_dir,
                                group_start + '_' + group_end + '.csv')

        all_keys = [x.keys()
                    for rel in rels for x in rel if isinstance(x, dict)]
        keys = list(set([x for sub in all_keys for x in sub]))

        with open(filename, 'w') as textfile:
            textfile.write(','.join([':START_ID(' + group_start + ')',
                                     ':TYPE',
                                     ':END_ID(' + group_end + ')'] + keys) +
                           '\n')

            for rel in rels:
                textfile.write(','.join([_get_value(val)
                                         for val in rel[:3]] +
                                        [_get_value(rel[3][key])
                                         for key in keys]) + '\n')

        return filename


def _get_value(value):
    '''Formats arrays as "x;y;x"'''
    if isinstance(value, Iterable):
        if not isinstance(value, str) and not isinstance(value, unicode):
            return ';'.join([_get_value(val) for val in value])

        return value.encode('utf-8')

    return str(value)
