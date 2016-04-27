'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import libchebipy

from synbiochem.design.mnxref import MnxRefReader
from synbiochem.utils import chem_utils as chem_utils
import sbcdb


def load(chemical_manager, reaction_manager):
    '''Loads MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''
    # Read mnxref data and generate nodes:
    reader = MnxRefReader()
    mnx_ids = _add_chemicals(reader.get_chem_data(), chemical_manager)
    rels = _add_reac_nodes(reader.get_reac_data(),
                           mnx_ids,
                           chemical_manager,
                           reaction_manager)

    return [], [sbcdb.write_rels(rels, 'Reaction', 'Chemical')]


def _add_chemicals(chem_data, chem_manager):
    '''Get chemical nodes from data.'''
    mnx_ids = {}

    for properties in chem_data.values():
        _add_chemical(properties, mnx_ids, chem_manager)

    return mnx_ids


def _add_reac_nodes(reac_data, mnx_ids, chem_manager, reaction_manager):
    '''Get reaction nodes from data.'''
    rels = []

    for properties in reac_data.values():
        mnx_id = properties.pop('id')
        reac_id = reaction_manager.add_reaction('mnx', mnx_id, properties)

        for prt in chem_utils.parse_equation(properties.pop('equation')):
            chem_id = mnx_ids[prt[0]] \
                if prt[0] in mnx_ids \
                else _add_chemical({'id': prt[0]}, mnx_ids, chem_manager)

            rels.append([reac_id, 'has_reactant', chem_id,
                         {'stoichiometry:float': prt[1]}])

    return rels


def _add_chemical(properties, mnx_ids, chem_manager):
    '''Adds a Chemical node with given id to the graph.'''
    if 'chebi' in properties:
        chebi_entity = libchebipy.ChebiEntity(properties['chebi'])

        if chebi_entity.get_parent_id() is not None:
            properties['chebi'] = chebi_entity.get_parent_id()

    mnx_id = properties['mnx'] = properties.pop('id')
    chem_id = chem_manager.add_chemical('chebi'
                                        if 'chebi' in properties
                                        else 'mnx',
                                        properties['chebi']
                                        if 'chebi' in properties
                                        else mnx_id,
                                        properties)
    mnx_ids[mnx_id] = chem_id
    return chem_id
