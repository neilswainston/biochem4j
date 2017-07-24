'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import os
import shutil
import subprocess
import sys

from sbcdb import index, chebi_utils, chemical_utils, kegg_utils, \
    mnxref_utils, ncbi_taxonomy_utils, reaction_utils, rhea_utils


def create_db(db_loc, files):
    '''Creates the database from csv files.'''
    if os.path.exists(db_loc):
        shutil.rmtree(db_loc)

    files = [list(elem) for elem in zip(*files)]
    files = [sorted([item for f in fle for item in f if item is not None])
             for fle in files]

    for i in range(len(files[0])):
        files[0].insert(i * 2, '--nodes')

    for i in range(len(files[1])):
        files[1].insert(i * 2, '--relationships')

    # Import database:
    params = ['neo4j-import', '--into', db_loc] + files[0] + files[1]

    print ' '.join([val for val in params])

    subprocess.call(params)


def _get_chem_csv_files(files):
    '''Create chemistry csv files.'''
    chem_man = chemical_utils.ChemicalManager()
    reac_man = reaction_utils.ReactionManager()

    print 'Parsing MNXref'
    mnx_loader = mnxref_utils.MnxRefLoader(chem_man, reac_man)
    files.append(mnx_loader.load())

    print 'Parsing ChEBI'
    files.append(chebi_utils.load(chem_man))

    # Get Spectrum data:
    # print 'Parsing spectrum data'
    # files.append(spectra_utils.load(chem_man))

    files.append(chem_man.get_files())

    print str(files)

    return reac_man


def main(argv):
    '''main method'''
    create_db(argv[1], argv[2:])


if __name__ == '__main__':
    main(sys.argv[1:])
