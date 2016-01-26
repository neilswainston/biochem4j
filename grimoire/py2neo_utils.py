'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import urlparse

from py2neo.packages.httpstream import http
import py2neo


http.socket_timeout = 9999


def get_graph(url):
    '''Contact Neo4j database, create and return Graph object.'''
    url_components = urlparse.urlparse(url)
    py2neo.authenticate(url_components.hostname + ':' +
                        str(url_components.port),
                        url_components.username,
                        url_components.password)
    return py2neo.Graph(url + '/db/data/')


def create(graph, entities, batch_size=1024):
    '''Creates multiple entities, limited by batch size.'''
    entities = [entity for entity in entities if not entity.bound]

    for i in xrange(0, len(entities), batch_size):
        graph.create(*entities[i:min(i + batch_size, len(entities))])
        print str(i) + '\t' + str(len(entities))
