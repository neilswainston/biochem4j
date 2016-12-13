'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from decimal import Decimal
from urllib import urlretrieve
import json
import os
import sys
import tempfile
import zipfile

import ijson

from sbcdb import utils


__MONA_URL = 'http://mona.fiehnlab.ucdavis.edu/rest/downloads/retrieve/' + \
    'a7ee3ffd-5900-4fac-b82a-9e8e0b5d6db5'

_NAME_MAP = {'kegg': 'kegg.compound',
             'molecular formula': 'formula',
             'total exact mass': 'monoisotopic_mass'}


def load(chem_manager, url=__MONA_URL):
    '''Build Spectrum nodes and relationships.'''
    # return _parse(_get_file(url))
    nodes = []
    rels = []

    records = _parse()

    for record in records:
        chem_id, _ = chem_manager.add_chemical(record['chemical'])
        nodes.append(record['spectrum'])
        rels.append([chem_id, 'has', record['spectrum']['id:ID(Spectrum)']])

    return [utils.write_nodes(nodes, 'Spectrum')], \
        [utils.write_rels(rels, 'Chemical', 'Spectrum')]


def _parse(filename='/Users/neilswainston/git/SYNBIOCHEM-DB/sbcdb/' +
           'MoNA-export-GC-MS.json'):
    '''Parses MoNA json file.'''
    records = []
    record = {'chemical': {'names:string[]': []},
              'spectrum': {':LABEL': 'Spectrum', 'tags:string[]': []}}
    name = None

    for prefix, typ, value in ijson.parse(open(filename)):
        try:
            if prefix == 'item' and typ == 'start_map':
                record = {'chemical': {'names:string[]': []},
                          'spectrum': {':LABEL': 'Spectrum', 'tags:string[]': []}}
            elif prefix == 'item.compound.item.inchi':
                record['chemical']['inchi'] = str(value)
            elif prefix == 'item.compound.item.names.item.name':
                if 'name' not in record['chemical']:
                    record['chemical']['name'] = str(value)
                record['chemical']['names:string[]'].append(
                    value.encode('utf-8'))
            elif prefix == 'item.compound.item.metaData.item.name' or \
                    prefix == 'item.metaData.item.name':
                name = _normalise_name(str(value).lower())
            elif prefix == 'item.compound.item.metaData.item.value':
                key = name + ':float' if isinstance(value, Decimal) else name
                value = float(value) if isinstance(value, Decimal) else \
                    (str(value.encode('utf-8')) if isinstance(value, str) or
                     isinstance(value, unicode) else str(value))
                record['chemical'][key] = value
                name = None
            elif prefix == 'item.id':
                record['spectrum']['id:ID(Spectrum)'] = str(value)
            elif prefix == 'item.metaData.item.value':
                try:
                    if name == 'retention time' or name == 'retention index' or \
                            name == 'derivative mw' or name == 'derivative mass':
                        tokens = str(value).split()
                        value = Decimal(float(tokens[0]))

                    key = name + \
                        ':float' if isinstance(value, Decimal) else name
                    value = float(value) if isinstance(value, Decimal) else \
                        (str(value.encode('utf-8')) if isinstance(value, str) or
                         isinstance(value, unicode) else str(value))
                    record['spectrum'][key] = value
                except ValueError, err:
                    print err
                    print '\t'.join([name, value, str(type(value))])
                name = None
            elif prefix == 'item.spectrum':
                values = [float(val) for term in value.split()
                          for val in term.split(':')]
                record['spectrum']['m/z:float[]'] = values[0::2]
                record['spectrum']['intensity:float[]'] = values[1::2]
            elif prefix == 'item.tags.item.text':
                record['spectrum']['tags:string[]'].append(str(value))
            elif prefix == 'item' and typ == 'end_map':
                records.append(record)

        except UnicodeEncodeError:
            print value
            print str(type(value))

    return records


def _get_file(url):
    '''Gets file from url.'''
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    urlretrieve(url, tmp_file.name)
    zfile = zipfile.ZipFile(tmp_file.name, 'r')
    destination = tempfile.mkdtemp()
    filepath = os.path.join(destination, zfile.namelist()[0])
    zfile.extractall(destination)
    return filepath


def _normalise_name(name):
    '''Normalises name in name:value pairs.'''
    return _NAME_MAP.get(name, name)


def main(args):
    '''main method'''
    records = _parse(args[0])
    print json.dumps(records, indent=4, sort_keys=True)

if __name__ == '__main__':
    main(sys.argv[1:])
