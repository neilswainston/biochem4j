'''
Created on 21 Apr 2016

@author: neilswainston
'''
import re

from synbiochem.utils import sequence_utils


class EnzymeManager(object):
    '''Class to implement a manager of Enzyme data.'''

    def __init__(self):
        '''Constructor.'''
        self.__nodes = {}
        self.__org_enz_rels = []

    def get_nodes(self):
        '''Gets enzyme nodes.'''
        return self.__nodes.values()

    def get_org_enz_rels(self):
        '''Gets organism-to-enzyme relationships.'''
        return self.__org_enz_rels

    def add_uniprot_data(self, enzyme_ids, source):
        '''Gets Uniprot data.'''

        fields = ['entry name', 'protein names', 'organism-id', 'ec']
        enzyme_ids = [enzyme_id for enzyme_id in enzyme_ids
                      if enzyme_id not in self.__nodes]
        uniprot_values = sequence_utils.get_uniprot_values(enzyme_ids, fields)

        for uniprot_id, uniprot_value in uniprot_values.iteritems():
            enzyme_node = {':LABEL': 'Enzyme',
                           'uniprot:ID(Enzyme)': uniprot_id}
            self.__nodes[uniprot_id] = enzyme_node
            uniprot_value.pop('Entry')
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

            if organism_id is not None and len(organism_id) > 0:
                self.__org_enz_rels.append([organism_id, 'expresses',
                                            uniprot_id, {'source': source}])
