'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
from collections import Counter
import csv
import itertools
import math
import re
import urllib2

from synbiochem.utils import chem_utils as chem_utils
import numpy

from sbcdb import namespace_utils, utils


_METANETX_URL = 'http://metanetx.org/cgi-bin/mnxget/mnxref/'


class MnxRefReader(object):
    '''Class to read MnxRef data from the chem_prop.tsv, the chem_xref.tsv and
    reac_prop.tsv files.'''

    def __init__(self, source=_METANETX_URL):
        self.__source = source
        self.__mnx_id_patt = re.compile(r'(MNX[MR])(\d+)')
        self.__chem_data = {}
        self.__reac_data = {}

    def get_chem_data(self):
        '''Gets chemical data.'''
        if len(self.__chem_data) == 0:
            self.__read_chem_prop()
            self.__read_xref('chem_xref.tsv', self.__chem_data, True)

            # Add missing xrefs:
            self.__add_xref(['chebi', '28938'],
                            self.__chem_data['MNXM84'], True)  # NH4
            self.__add_xref(['chebi', '30616'],
                            self.__chem_data['MNXM114062'], True)  # ATP

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
                values[0] = self.__parse_id(values[0])
                values[7] = self.__parse_id(values[7])
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
                evidence = xrefs.get('Evidence', 'identity')

                if evidence == 'identity' or evidence == 'structural':
                    xrefs['MNX_ID'] = self.__parse_id(xrefs['MNX_ID'])
                    xref = xrefs['XREF'].split(':')

                    if xrefs['MNX_ID'] in data:
                        entry = data[xrefs['MNX_ID']]
                        self.__add_xref(xref, entry, chemical)

    def __add_xref(self, xref, entry, chemical):
        '''Adds an xref.'''
        namespace = namespace_utils.resolve_namespace(xref[0],
                                                      chemical)

        if namespace is not None:
            xref[1] = self.__parse_id(xref[1])

            entry[namespace] = xref[1] \
                if namespace is not 'chebi' \
                else 'CHEBI:' + xref[1]

    def __read_reac_prop(self):
        '''Read reaction properties and create Nodes.'''
        reac_prop_keys = ['id', 'equation', 'description', 'balance', 'ec',
                          'Source']

        for values in self.__read_data('reac_prop.tsv'):
            if not values[0].startswith('#'):
                values[0] = self.__parse_id(values[0])
                values[5] = self.__parse_id(values[5])

                props = dict(zip(reac_prop_keys, values))

                try:
                    participants = chem_utils.parse_equation(
                        props.pop('equation'))

                    for participant in participants:
                        participant[0] = self.__parse_id(participant[0])

                        if participant[0] not in self.__chem_data:
                            self.__add_chem(participant[0])

                    props['reac_defn'] = participants
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

    def __parse_id(self, item_id):
        '''Parses mnx ids.'''
        matches = self.__mnx_id_patt.findall(item_id)

        for mat in matches:
            return mat[0] + str(int(mat[1]))

        return item_id


class MnxRefLoader(object):
    '''Loads MNXref data into neo4j format.'''

    def __init__(self, chem_man, reac_man):
        self.__chem_man = chem_man
        self.__reac_man = reac_man

    def load(self):
        '''Loads MnxRef data from chem_prop.tsv, chem_xref.tsv,
        reac_prop.tsv and reac_xref.tsv files.'''
        reader = MnxRefReader()

        for properties in reader.get_chem_data().values():
            properties['mnx'] = properties.pop('id')
            self.__chem_man.add_chemical(properties)

        rels = self.__add_reac_nodes(reader.get_reac_data())

        return [], [utils.write_rels(rels, 'Reaction', 'Chemical')]

    def __add_reac_nodes(self, reac_data):
        '''Get reaction nodes from data.'''
        reac_id_def = {}

        for properties in reac_data.values():
            reac_def = []
            mnx_id = properties.pop('id')

            # Remove equation and description (may be inconsistent with
            # balanced reaction):
            if 'description' in properties:
                properties.pop('description')

            for prt in properties.pop('reac_defn'):
                chem_id, _ = self.__chem_man.add_chemical({'mnx': prt[0]})

                reac_def.append([self.__chem_man.get_prop(prt[0], 'formula'),
                                 self.__chem_man.get_prop(prt[0],
                                                          'charge:int', 0),
                                 prt[1],
                                 chem_id])

            if all([values[0] is not None for values in reac_def]):
                balanced, _, balanced_def = chem_utils.balance(reac_def)
                properties['balance'] = balanced
            else:
                properties['balance'] = 'unknown'
                balanced_def = reac_def

            reac_id = self.__reac_man.add_reaction('mnx', mnx_id,
                                                   properties)
            reac_id_def[reac_id] = balanced_def

        chem_id_mass = self.__chem_man.get_props('monoisotopic_mass:float',
                                                 float('NaN'))
        cofactors = [chem_id
                     for chem_id, mass in chem_id_mass.iteritems()
                     if mass > 0 and mass < 44]  # Assume mass < CO2 = cofactor

        for cofact in cofactors:
            mono_mass = self.__chem_man.get_prop(cofact,
                                                 'monoisotopic_mass:float')
            print '\t'.join([cofact,
                             self.__chem_man.get_prop(cofact, 'name'),
                             str(mono_mass)])

        cofactor_pairs = self.__calc_cofactors(reac_id_def.values(), cofactors)
        rels = []

        for reac_id, defn in reac_id_def.iteritems():
            reactants = [term[3] for term in defn if term[2] < 0]
            products = [term[3] for term in defn if term[2] > 0]
            reac_cofactors = []

            # Set metabolites as cofactors:
            for met in [term[3] for term in defn]:
                if met in cofactors:
                    reac_cofactors.append(met)

            # Set pairs as cofactors:
            for pair in itertools.product(reactants, products):
                if tuple(sorted(pair)) in cofactor_pairs:
                    reac_cofactors.extend(pair)

            for term in defn:
                rels.append([reac_id,
                             'has_cofactor' if term[3] in reac_cofactors
                             else 'has_reactant',
                             term[3],
                             {'stoichiometry:float': term[2]}])

        return rels

    def __calc_cofactors(self, reaction_defs, cofactors, cutoff=0.8):
        '''Calculates cofactors.'''
        # metabolites = Counter()
        pairs = Counter()

        # Count occurances of metabolites in all reactions...
        # for reaction_def in reaction_defs:
        #     metabolites.update([term[3] for term in reaction_def])

        # self.__filter(metabolites, cutoff)

        # Calculate all reactant / product pairs...
        for reaction_def in reaction_defs:
            reactants = [term[3] for term in reaction_def if term[2] < 0 and
                         term[3] not in cofactors]
            products = [term[3] for term in reaction_def if term[2] > 0 and
                        term[3] not in cofactors]

            pairs.update([tuple(sorted(pair))
                          for pair in itertools.product(reactants, products)])

        return self.__filter(pairs, cutoff)

    def __filter(self, counter, cutoff):
        '''Filter counter items according to cutoff.'''
        for key in counter:
            if isinstance(key, str):
                name = self.__chem_man.get_prop(key, 'name' '')
            else:
                name = '; '.join([self.__chem_man.get_prop(term, 'name', '')
                                  for term in key])

            print str(key) + '\t' + (name if name else str(key)) + '\t' + \
                str(counter[key])

        # Count occurences of pairs, then bin into a histogram...
        hist_counter = Counter(counter.values())

        # Fit straight-line to histogram log-log plot and filter...
        x, y = zip(*list(hist_counter.items()))
        m, b = numpy.polyfit(numpy.log(x), numpy.log(y), 1)

        print str(cutoff) + '\t' + str(math.exp(cutoff * -b / m))

        return [item[0] for item in counter.items()
                if item[1] > math.exp(cutoff * -b / m)]


def _convert_to_float(dictionary, key):
    '''Converts a key value in a dictionary to a float.'''
    if len(dictionary.get(key, '')):
        dictionary[key] = float(dictionary[key])
    else:
        # Remove key:
        dictionary.pop(key, None)
