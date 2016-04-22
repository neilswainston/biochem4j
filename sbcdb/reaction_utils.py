'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sbcdb


def submit(data, source, enzyme_source):
    '''Submit data to the graph.'''
    print 'reaction_utils.submit'

    # Create Reaction and Enzyme nodes:
    reac_nodes, enzyme_ids, reac_enz_rels = __create_react_enzyme(data,
                                                                  source)

    # Create Enzyme nodes:
    enzyme_source.add_uniprot_data(enzyme_ids, source)

    return [sbcdb.write_nodes(reac_nodes.values(), 'Reaction')], \
        [sbcdb.write_rels(reac_enz_rels, 'Reaction', 'Enzyme')]


def __create_react_enzyme(data, source):
    '''Creates Reaction and Enzyme nodes and their Relationships.'''
    print 'reaction_utils.__create_react_enzyme'
    reac_nodes = {}
    enzyme_ids = []
    reac_enz_rels = []

    for reac_id, uniprot_ids in data.iteritems():
        if reac_id not in reac_nodes:
            reac_nodes[reac_id] = {':LABEL': 'Reaction',
                                   source + ':ID(Reaction)': reac_id}

        for uniprot_id in uniprot_ids:
            enzyme_ids.append(uniprot_id)
            reac_enz_rels.append([reac_id, 'catalysed_by', uniprot_id,
                                  {'source': source}])

    return reac_nodes, list(set(enzyme_ids)), reac_enz_rels
