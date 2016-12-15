'''
synbiochem (c) University of Manchester 2016

synbiochem is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from collections import Iterable
import csv
import tempfile


def write_nodes(nodes, group):
    '''Writes Nodes to csv file.'''
    if not len(nodes):
        return None

    fle = tempfile.NamedTemporaryFile(suffix='.txt', prefix=group + '_',
                                      delete=False)

    nodes = [{key: _get_value(value) for key, value in node.iteritems()}
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
    if not len(rels):
        return None

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


def _get_value(value):
    '''Formats arrays as "x;y;x"'''
    if isinstance(value, Iterable):
        if not isinstance(value, str) and not isinstance(value, unicode):
            return ';'.join([_get_value(val) for val in value])
        else:
            return value.encode('utf-8')

    return value
