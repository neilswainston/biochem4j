'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from grimoire import mnxref_utils


def load(url):
    '''Loads data into neo4j from a number of sources.'''
    graph = mnxref_utils.load(url)
    print graph
