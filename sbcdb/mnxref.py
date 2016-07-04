'''
synbiochem (c) University of Manchester 2015

synbiochem is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import csv
import urllib2

from sbcdb import namespace_utils
import synbiochem.utils.chem_utils as chem_utils


_METANETX_URL = 'http://metanetx.org/cgi-bin/mnxget/mnxref/'


class MnxRefReader(object):
    '''Class to read MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''

    def __init__(self, source=_METANETX_URL):
        self.__source = source
        self.__chem_data = {}
        self.__reac_data = {}

    def get_chem_data(self):
        '''Gets chemical data.'''
        if len(self.__chem_data) == 0:
            self.__read_chem_prop()
            self.__read_xref('chem_xref.tsv', self.__chem_data, True)

        return self.__chem_data

    def get_reac_data(self):
        '''Gets reaction data.'''
        if len(self.__reac_data) == 0:
            self.__read_reac_prop()
            self.__read_xref('reac_xref.tsv', self.__reac_data, False)

        return self.__reac_data

    def __read_chem_prop(self):
        '''Read chemical properties and create Nodes.'''
        chem_prop_keys = ['id', 'name', 'formula', 'charge', 'mass', 'inchi',
                          'smiles', 'source']

        for values in self.__read_data('chem_prop.tsv'):
            if not values[0].startswith('#'):
                props = dict(zip(chem_prop_keys, values))
                props.pop('source')
                _convert_to_float(props, 'charge')
                _convert_to_float(props, 'mass')
                props = {key: value for key, value in props.iteritems()
                         if value != ''}
                self.__chem_data[values[0]] = props

    def __read_xref(self, filename, data, chemical):
        '''Read xrefs and update Nodes.'''
        xref_keys = ['XREF', 'MNX_ID', 'Evidence', 'Description']

        for values in self.__read_data(filename):
            if not values[0].startswith('#'):
                xrefs = dict(zip(xref_keys[:len(values)], values))
                xref = xrefs['XREF'].split(':')

                if xrefs['MNX_ID'] in data:
                    entry = data[xrefs['MNX_ID']]
                    namespace = namespace_utils.resolve_namespace(xref[0],
                                                                  chemical)

                    if namespace is not None:
                        entry[namespace] = xref[1] if namespace is not 'chebi' \
                            else 'CHEBI:' + xref[1]

    def __read_reac_prop(self):
        '''Read reaction properties and create Nodes.'''
        equation_key = 'equation'
        reac_prop_keys = ['id', equation_key, 'description', 'balance', 'ec',
                          'Source']

        for values in self.__read_data('reac_prop.tsv'):
            if not values[0].startswith('#'):
                props = dict(zip(reac_prop_keys, values))

                try:
                    participants = chem_utils.parse_equation(
                        props[equation_key])

                    for participant in participants:
                        if participant[0] not in self.__chem_data:
                            self.__add_chem(participant[0])

                    self.__reac_data[values[0]] = props
                except ValueError:
                    print 'WARNING: Suspected polymerisation reaction: ' + \
                        values[0] + '\t' + str(props)

    def __add_chem(self, chem_id):
        '''Adds a chemical with given id.'''
        props = {'id': chem_id}
        self.__chem_data[chem_id] = props
        return props

    def __read_data(self, filename):
        '''Downloads and reads tab-limited files into lists of lists of
        strings.'''
        return list(csv.reader(urllib2.urlopen(self.__source + filename),
                               delimiter='\t'))


def _convert_to_float(dictionary, key):
    '''Converts a key value in a dictionary to a float.'''
    if key in dictionary and dictionary[key] is not None and \
            len(str(dictionary[key])) > 0:
        dictionary[key] = float(dictionary[key])
    else:
        # Remove key:
        dictionary.pop(key, None)


def main():
    '''main method'''
    reader = MnxRefReader()
    print len(reader.get_chem_data())
    print len(reader.get_reac_data())


if __name__ == "__main__":
    main()
