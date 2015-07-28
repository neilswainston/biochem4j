'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import urlparse

import py2neo


def get_graph(url):
    '''Contact Neo4j database, create and return Graph object.'''
    url_components = urlparse.urlparse(url)
    py2neo.authenticate(url_components.hostname + ':' + str(url_components.port), \
                 url_components.username, \
                 url_components.password)
    return py2neo.Graph(url + '/db/data/')
