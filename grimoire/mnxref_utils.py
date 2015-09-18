'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import csv
import re
import sys
import urllib2

import py2neo

import grimoire.py2neo_utils


__METANETX_URL = 'http://metanetx.org/cgi-bin/mnxget/mnxref/'


def load(url, source=__METANETX_URL):
    '''Loads MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''

    # Contact Neo4j database, create Graph object:
    graph = grimoire.py2neo_utils.get_graph(url)

    # Read chemical properties and create Nodes:
    chem_prop_keys = ['id', 'name', 'formula', 'charge', 'mass', 'inchi',
                      'smiles', 'source']
    chem_prop_nodes = {}

    for values in __read_data(source, 'chem_prop.tsv'):
        if not values[0].startswith('#'):
            node = py2neo.Node.cast(dict(zip(chem_prop_keys, values)))
            node.labels.add('Metabolite')
            graph.create(node)
            chem_prop_nodes[values[0]] = node

    __read_xrefs(source, chem_prop_nodes)

    # Read reaction properties and create Nodes:
    equation_key = 'equation'
    reac_prop_keys = ['id', equation_key, 'description', 'balance', 'ec',
                      'Source']

    for values in __read_data(source, 'reac_prop.tsv'):
        if not values[0].startswith('#'):
            try:
                reac_prop_values = dict(zip(reac_prop_keys, values))
                equation = reac_prop_values.pop(equation_key)
                participants = __parse_equation(equation, '=')
                node = py2neo.Node.cast(reac_prop_values)
                node.labels.add('Reaction')
                reaction = graph.create(node)

                for participant in participants:
                    graph.create(py2neo.rel(reaction[0],
                                            "HAS_REACTANT",
                                            chem_prop_nodes[participant[0]],
                                            stoichiometry=participant[1]))

            except (IndexError, KeyError, ValueError) as err:
                print err


def __read_data(source, filename):
    '''Downloads and reads tab-limited files into lists of lists of strings.'''
    return list(csv.reader(urllib2.urlopen(source + filename), delimiter='\t'))


def __read_xrefs(source, chem_prop_nodes):
    '''Read chemical xrefs and update Nodes'''
    chem_xref_keys = ['XREF', 'MNX_ID', 'Evidence', 'Description']

    for values in __read_data(source, 'chem_xref.tsv'):
        if not values[0].startswith('#'):
            xrefs = dict(zip(chem_xref_keys, values))
            xref = xrefs['XREF'].split(':')
            node = chem_prop_nodes[xrefs['MNX_ID']]
            node.properties[xref[0]] = xref[1]


def __parse_equation(equation, separator):
    '''Parses chemical equation strings.'''
    equation_terms = [re.split('\\s*\\+\\s*', equation_side)
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
                            else (terms[1], stoich_factor * float(terms[0])))


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
