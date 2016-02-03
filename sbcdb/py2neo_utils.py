'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

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


def create(graph, entities, batch_size=1024, match_criteria=None):
    '''Creates multiple entities, limited by batch size.'''
    unbound = []

    if match_criteria is not None:
        for key, entity in entities.iteritems():
            for value in match_criteria:
                if entity[value[1]] is not None:
                    bound = find_one(graph, value[0], value[1],
                                     entity[value[1]])

                    if bound is not None:
                        for prop in entity.properties:
                            if bound[prop] is None:
                                bound[prop] = entity[prop]
                                bound.push()

                        entities[key] = bound
                        break

            if not entities[key].bound:
                entities[key] = entity
                unbound.append(entity)
    else:
        unbound = entities.values()

    for i in xrange(0, len(unbound), batch_size):
        graph.create(*unbound[i:min(i + batch_size, len(entities))])
        print str(i) + '\t' + str(len(unbound))

    return entities


def find_one(graph, label, property_key, property_value):
    '''Finds a single node constraint by label, property_key and
    property_value.'''
    return graph.find_one(label, property_key, property_value)
