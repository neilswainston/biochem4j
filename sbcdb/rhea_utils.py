'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import tempfile
import urllib


__RHEA_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/rhea/tsv/rhea2uniprot.tsv'


def load(reaction_manager, source=__RHEA_URL):
    '''Loads Rhea data.'''
    print 'rhea_utils.load'
    # Parse data:
    temp_file = tempfile.NamedTemporaryFile()
    urllib.urlretrieve(source, temp_file.name)
    data = __parse(temp_file.name)
    reaction_manager.add_react_to_enz(data, 'rhea')


def __parse(filename):
    '''Parses file.'''
    print 'rhea_utils.__parse'
    data = {}

    with open(filename, 'r') as textfile:
        next(textfile)

        for line in textfile:
            try:
                tokens = line.split('\t')

                if len(tokens) == 4:
                    uniprot_id = tokens[3].strip()
                    __add(data, tokens[0], uniprot_id)
                    __add(data, tokens[2], uniprot_id)

                if len(data) > 10:
                    return data

            except IndexError:
                print line

    return data


def __add(data, rhea_id, uniprot_id):
    '''Adds Rhea id and Uniprot id to data.'''
    if rhea_id in data:
        data[rhea_id].append(uniprot_id)
    else:
        data[rhea_id] = [uniprot_id]


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
