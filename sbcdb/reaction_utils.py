'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import re

from synbiochem.utils import sequence_utils
import sbcdb


def submit(data, source):
    '''Submit data to the graph.'''

    # Create Reaction and Enzyme nodes:
    reac_nodes, enzyme_nodes, reac_enz_rels = __create_react_enzyme(data,
                                                                    source)

    # Create Enzyme nodes:
    org_enz_rels = __get_uniprot_data(enzyme_nodes, source)

    return [sbcdb.write_nodes(reac_nodes.values()),
            sbcdb.write_nodes(enzyme_nodes.values()),
            ], \
        [sbcdb.write_rels(reac_enz_rels),
         sbcdb.write_rels(org_enz_rels)]


def __create_react_enzyme(data, source):
    '''Creates Reaction and Enzyme nodes and their Relationships.'''
    reac_nodes = {}
    enzyme_nodes = {}
    reac_enz_rels = []

    for reac_id, uniprot_ids in data.iteritems():
        if reac_id not in reac_nodes:
            reac_nodes[reac_id] = {':LABEL': 'Reaction', source: reac_id}

        for uniprot_id in uniprot_ids:
            if uniprot_id not in enzyme_nodes:
                enzyme_nodes[uniprot_id] = {
                    ':LABEL': 'Enzyme', 'uniprot': uniprot_id}

            reac_enz_rels.append([reac_id, 'catalysed_by', uniprot_id,
                                  {'source': source}])

    return reac_nodes, enzyme_nodes, reac_enz_rels


def __get_uniprot_data(enzyme_nodes, source):
    '''Gets Uniprot data.'''
    org_enz_rels = []

    fields = ['entry name', 'protein names', 'organism-id', 'ec']
    uniprot_values = sequence_utils.get_uniprot_values(enzyme_nodes.keys(),
                                                       fields)

    for uniprot_id, uniprot_value in uniprot_values.iteritems():
        uniprot_value.pop('Entry')
        enzyme_node = enzyme_nodes[uniprot_id]
        organism_id = uniprot_value.pop('Organism ID')

        if 'Entry name' in uniprot_value:
            enzyme_node['entry'] = uniprot_value['Entry name']

        if 'Protein names' in uniprot_value:
            regexp = re.compile(r'(?<=\()[^)]*(?=\))|^[^\(]*(?= \()')
            enzyme_node['names'] = regexp.findall(
                uniprot_value['Protein names'])

            if len(enzyme_node['names']) > 0:
                enzyme_node['name'] = enzyme_node['names'][0]

        if 'EC number' in uniprot_value:
            enzyme_node['ec-code'] = uniprot_value['EC number']

        org_enz_rels.append([organism_id, 'expresses', uniprot_id,
                             {'source': source}])

    return org_enz_rels
