'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import json
import sys

from libsbml import SBMLDocument, writeSBMLToFile
from synbiochem.utils import net_utils


def get_document(params):
    '''Gets a model.'''
    document = SBMLDocument(2, 5)
    model = document.createModel()

    for param in params:
        print _get_reaction(param)

    return document


def _get_reaction(reac_id):
    '''Gets a reaction.'''
    url = 'http://www.biochem4j.org/db/data/transaction/commit'
    query = 'MATCH (r:Reaction {id: {reac_id}})--(c:Chemical) RETURN r, c'
    data = {'statements': [
        {
            'statement': query,
            'parameters': {'reac_id': reac_id}
        }
    ]}
    headers = {'Accept': 'application/json; charset=UTF-8',
               'Content-Type': 'application/json'}
    return net_utils.post(url, json.dumps(data), headers)


def main(args):
    '''main method'''
    document = get_document(args[1:])
    writeSBMLToFile(document, args[0])


if __name__ == '__main__':
    main(sys.argv[1:])
