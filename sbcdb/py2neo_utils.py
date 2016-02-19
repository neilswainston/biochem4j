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


def create(graph, entities, batch_size=1024, verbose=False,
           match_criteria=None):
    '''Creates multiple entities, limited by batch size.'''
    unbound = []

    if __check_match_criteria(graph, match_criteria):
        for key, entity in entities.iteritems():
            if verbose:
                print 'py2neo_utils: Checking ' + str(entity)

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

    __create(graph, unbound, batch_size, verbose)


def find_one(graph, label, property_key, property_value):
    '''Finds a single node constraint by label, property_key and
    property_value.'''
    return graph.find_one(label, property_key, property_value)


def __check_match_criteria(graph, match_criteria):
    ''''Check to see if any nodes of this Label exist.'''
    if match_criteria is not None:
        for value in match_criteria:
            result = graph.cypher.execute('MATCH (n:' + value[0] + ') ' +
                                          'WHERE HAS (n.' + value[1] + ') ' +
                                          'RETURN COUNT(n)')

            if result.one == 0:
                match_criteria.remove(value)

    return match_criteria is not None and len(match_criteria) > 0


def __create(graph, unbound, batch_size, verbose=False):
    '''Creates unbound nodes.'''
    for i in xrange(0, len(unbound), batch_size):
        graph.create(*unbound[i:min(i + batch_size, len(unbound))])

        if verbose:
            print 'py2neo_utils: Creating entry ' + str(i) + ' of ' + \
                str(len(unbound))
