'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import math

import libchebipy

from sbcdb import build
import synbiochem.design


def load(chem_manager):
    '''Loads ChEBI data from libChEBIpy.'''
    chebi_ids = []
    rels = []

    _add_node('CHEBI:24431', chebi_ids, rels, chem_manager)

    return [], [build.write_rels(rels, 'Chemical', 'Chemical')]


def _add_node(chebi_id, chebi_ids, rels, chem_manager):
    '''Constructs a node from libChEBI.'''
    if chebi_id not in chebi_ids:
        entity = libchebipy.ChebiEntity(chebi_id)

        properties = {}
        properties['name'] = entity.get_name()
        properties['names:string[]'] = [name.get_name()
                                        for name in entity.get_names()] + \
            [entity.get_name()]
        properties['formula'] = entity.get_formula()
        properties['charge'] = 0 if math.isnan(entity.get_charge()) \
            else entity.get_charge()

        properties['inchi'] = entity.get_inchi()
        properties['smiles'] = entity.get_smiles()

        for db_acc in entity.get_database_accessions():
            namespace = synbiochem.design.resolve_namespace(db_acc.get_type(),
                                                            True)

            if namespace is not None:
                properties[namespace] = db_acc.get_accession_number()

        chebi_ids.append(chebi_id)

        chem_id = chem_manager.add_chemical('chebi', chebi_id, properties)

        for incoming in entity.get_incomings():
            target_id = incoming.get_target_chebi_id()
            _add_node(target_id, chebi_ids, rels, chem_manager)
            rels.append([target_id, incoming.get_type(), chem_id])
