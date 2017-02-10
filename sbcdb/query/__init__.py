'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import json
from synbiochem.utils import net_utils


def run_query(query, parameters):
    '''Gets a reaction.'''
    url = 'http://www.biochem4j.org/db/data/transaction/commit'

    data = {'statements': [
        {
            'statement': query,
            'parameters': parameters
        }
    ]}

    headers = {'Accept': 'application/json; charset=UTF-8',
               'Content-Type': 'application/json'}

    return json.loads(net_utils.post(url, json.dumps(data), headers))
