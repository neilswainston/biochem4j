'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from _collections import defaultdict
import json
import re
import sys
import urllib

from libsbml import CVTerm, SBMLDocument, writeSBMLToFile, \
    BIOLOGICAL_QUALIFIER, BQB_IS
from synbiochem.utils import net_utils


def get_document(params):
    '''Gets a model.'''
    document = SBMLDocument(2, 5)
    model = document.createModel()
    cmpt = model.createCompartment()
    cmpt.setId('c')
    cmpt.setSize(1)

    nodes = defaultdict(dict)
    rels = []

    for param in params:
        data = json.loads(_get_reaction(param))
        _parse(data, nodes, rels)

    for cid, chemical in nodes['c'].iteritems():
        _add_species(model, cid, chemical)

    for cid, reaction in nodes['r'].iteritems():
        _add_reaction(model, cid, reaction)

    for rel in rels:
        _add_species_ref(model, str(rel[0]), str(rel[2]),
                         rel[1]['stoichiometry'])

    return document


def _get_reaction(reac_id):
    '''Gets a reaction.'''
    url = 'http://www.biochem4j.org/db/data/transaction/commit'
    query = 'MATCH (r:Reaction {id: {reac_id}})-[rel]-(c:Chemical) ' + \
        'RETURN r, rel, c'

    data = {'statements': [
        {
            'statement': query,
            'parameters': {'reac_id': reac_id}
        }
    ]}

    headers = {'Accept': 'application/json; charset=UTF-8',
               'Content-Type': 'application/json'}

    return net_utils.post(url, json.dumps(data), headers)


def _parse(data, nodes, rels):
    '''Parses data.'''
    if len(data['errors']) > 0:
        raise ValueError(str(data['errors']))

    columns = data['results'][0]['columns']

    for datum in data['results'][0]['data']:
        from_node = None
        to_node = None
        rel = None

        for idx, meta_row in enumerate(zip(datum['meta'], datum['row'])):
            if meta_row[0]['type'] == 'node':
                cid = _get_id(meta_row[1]['id'])
                nodes[columns[idx]][cid] = meta_row[1]

                if from_node is None:
                    from_node = cid
                else:
                    to_node = cid

            elif meta_row[0]['type'] == 'relationship':
                rel = meta_row[1]

        if rel is not None:
            rels.append((from_node, rel, to_node))


def _get_id(cid):
    '''Gets an SBML-friendly id.'''
    return '_' + re.sub('\\W', '_', cid)


def _add_species(model, cid, data):
    '''Adds a species.'''
    spec = model.createSpecies()
    _init_sbase(spec, cid, data)
    spec.setSBOTerm(247)
    spec.setName(str(data['name']))
    spec.setCompartment('c')
    spec.setInitialConcentration(0)


def _add_reaction(model, cid, data):
    '''Adds a reaction.'''
    react = model.createReaction()
    _init_sbase(react, cid, data)
    react.setSBOTerm(167)


def _add_species_ref(model, react_id, spec_id, stoic):
    '''Adds species reference.'''
    react = model.getReaction(react_id)

    if stoic > 0:
        react.addProduct(model.getSpecies(spec_id), stoic)
    else:
        react.addReactant(model.getSpecies(spec_id), abs(stoic))


def _init_sbase(sbase, cid, data):
    '''Initialises an sbase.'''
    sbase.setSBOTerm(247)
    sbase.setId(str(cid))
    sbase.setMetaId('_meta' + str(cid))
    _add_identifiers(data, sbase)


def _add_identifiers(properties, sbase):
    '''Gets semantic identifiers.'''
    for key, value in properties.iteritems():
        url = 'http://identifiers.org/' + key + '/' + str(value)

        if urllib.urlopen(url).getcode() == 200:
            _add_cv_term(url, sbase)


def _add_cv_term(url, sbase):
    '''Adds a CVTerm.'''
    cv_term = CVTerm()
    cv_term.setQualifierType(BIOLOGICAL_QUALIFIER)
    cv_term.setBiologicalQualifierType(BQB_IS)
    cv_term.addResource(str(url))
    sbase.addCVTerm(cv_term)


def main(args):
    '''main method'''
    document = get_document(args[1:])
    document.checkConsistency()
    document.printErrors()
    writeSBMLToFile(document, args[0])


if __name__ == '__main__':
    main(sys.argv[1:])
