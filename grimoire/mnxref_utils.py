'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import csv
import re
import sys
import traceback
import urllib2

import py2neo

import grimoire.py2neo_utils


__METANETX_URL = 'http://metanetx.org/cgi-bin/mnxget/mnxref/'


def load(url, source=__METANETX_URL):
    '''Loads MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''

    # Contact Neo4j database, create Graph object:
    graph = grimoire.py2neo_utils.get_graph(url)

    # Read chem data::
    chem_nodes = __read_chem_prop(source)
    __read_chem_xref(source, chem_nodes)

    # Submit chem data:
    grimoire.py2neo_utils.create(graph, chem_nodes.values())

    # Read reac data:
    reac_nodes, reac_rels = __read_reac_prop(source, chem_nodes, graph)

    # Submit reac data:
    grimoire.py2neo_utils.create(graph, reac_nodes)
    grimoire.py2neo_utils.create(graph, reac_rels, 512)

    return graph


def __read_data(source, filename):
    '''Downloads and reads tab-limited files into lists of lists of strings.'''
    return list(csv.reader(urllib2.urlopen(source + filename), delimiter='\t'))


def __read_chem_prop(source):
    '''Read chemical properties and create Nodes.'''
    chem_prop_keys = ['id', 'name', 'formula', 'charge', 'mass', 'inchi',
                      'smiles', 'source']
    chem_nodes = {}

    for values in __read_data(source, 'chem_prop.tsv'):
        if not values[0].startswith('#'):
            node = py2neo.Node.cast(dict(zip(chem_prop_keys, values)))
            node.labels.add('Metabolite')
            chem_nodes[values[0]] = node

    return chem_nodes


def __read_chem_xref(source, chem_nodes):
    '''Read chemical xrefs and update Nodes.'''
    chem_xref_keys = ['XREF', 'MNX_ID', 'Evidence', 'Description']

    for values in __read_data(source, 'chem_xref.tsv'):
        if not values[0].startswith('#'):
            xrefs = dict(zip(chem_xref_keys, values))
            xref = xrefs['XREF'].split(':')

            if xrefs['MNX_ID'] in chem_nodes:
                node = chem_nodes[xrefs['MNX_ID']]
                node.properties[xref[0]] = xref[1]


def __read_reac_prop(source, chem_nodes, graph):
    '''Read reaction properties and create Nodes.'''
    equation_key = 'equation'
    reac_prop_keys = ['id', equation_key, 'description', 'balance', 'ec',
                      'Source']

    reac_nodes = []
    reac_rels = []

    for values in __read_data(source, 'reac_prop.tsv'):
        if not values[0].startswith('#'):
            try:
                properties = dict(zip(reac_prop_keys, values))
                equation = properties.pop(equation_key)
                participants = __parse_equation(equation, '=')
                node = py2neo.Node.cast(properties)
                node.labels.add('Reaction')
                reac_nodes.append(node)

                for participant in participants:
                    target_chem_node = chem_nodes[participant[0]] \
                        if participant[0] in chem_nodes \
                        else __add_chem_node(participant[0], chem_nodes, graph)
                    reac_rels.append(py2neo.rel(node, 'HAS_REACTANT',
                                                target_chem_node,
                                                stoichiometry=participant[1]))

            except (IndexError, KeyError, ValueError):
                print traceback.print_exc()

    return reac_nodes, reac_rels


def __parse_equation(equation, separator):
    '''Parses chemical equation strings.'''
    equation_terms = [re.split('\\s+\\+\\s+', equation_side)
                      for equation_side in
                      re.split('\\s*' + separator + '\\s*', equation)]

    participants = []

    # Add reactants:
    __add_reaction_participants(equation_terms[0], -1, participants)

    # Add products:
    __add_reaction_participants(equation_terms[1], 1, participants)

    return participants


def __add_reaction_participants(equation_term, stoich_factor, participants):
    '''Adds reaction participants to a list of participants.'''
    for participant in equation_term:
        terms = participant.split()
        participants.append((participant, stoich_factor) if len(terms) == 1
                            else (terms[1], __get_stoichiometry(stoich_factor,
                                                                terms[0])))


def __get_stoichiometry(stoich_factor, term):
    '''Returns +/- term if term is numeric, else returns term as string,
    catching non-specific stoichiometries such as (n+1).'''
    try:
        return stoich_factor * float(term)
    except ValueError:
        return term


def __add_chem_node(chem_id, chem_nodes, graph):
    '''Adds a Metabolite node with given id to the graph.'''
    node = py2neo.Node('Metabolite', id=chem_id)
    chem_nodes[chem_id] = node
    graph.create(node)
    return node


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
