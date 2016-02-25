'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import math
import sys
import libchebipy
import sbcdb
import synbiochem.design


def load():
    '''Loads ChEBI data from libChEBIpy.'''
    nodes = {}
    rels = []

    __add_node('CHEBI:24431', nodes, rels)

    return [sbcdb.write_nodes(nodes.values())], [sbcdb.write_rels(rels)]


def __add_node(chebi_id, nodes, rels):
    '''Constructs a node from libChEBI.'''
    if chebi_id not in nodes:
        entity = libchebipy.ChebiEntity(chebi_id)

        properties = {}
        properties[':LABEL'] = 'Chemical'
        properties['chebi:ID'] = entity.get_id()
        properties['name'] = entity.get_name()
        properties['names:string[]'] = [name.get_name()
                                        for name in entity.get_names()] + \
            [entity.get_name()]
        properties['formula'] = entity.get_formula()
        properties['charge:int'] = 0 if math.isnan(entity.get_charge()) \
            else entity.get_charge()

        properties['inchi'] = entity.get_inchi()
        properties['smiles'] = entity.get_smiles()

        for db_acc in entity.get_database_accessions():
            namespace = synbiochem.design.resolve_namespace(db_acc.get_type(),
                                                            True)

            if namespace is not None:
                properties[namespace] = db_acc.get_accession_number()

        sbcdb.normalise_masses(properties)

        nodes[chebi_id] = properties

        for incoming in entity.get_incomings():
            target_id = incoming.get_target_chebi_id()
            __add_node(target_id, nodes, rels)
            rels.append([target_id, incoming.get_type(), chebi_id])


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
