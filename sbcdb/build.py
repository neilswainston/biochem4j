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

from sbcdb import chebi_utils, chemical_utils, kegg_utils, mnxref_utils, \
    ncbi_taxonomy_utils, reaction_utils, rhea_utils


def build(db_loc):
    '''Loads data into neo4j from a number of sources.'''
    files = []

    # Get Organism data:
    print 'Parsing NCBI Taxonomy'
    files.append(ncbi_taxonomy_utils.load())

    # Get Chemical and Reaction data:
    chemical_manager = chemical_utils.ChemicalManager()
    reaction_manager = reaction_utils.ReactionManager()

    print 'Parsing MNXref'
    files.append(mnxref_utils.load(chemical_manager, reaction_manager))

    # Get Chemical data:
    print 'Parsing ChEBI'
    files.append(chebi_utils.load(chemical_manager))

    # Get Reaction / Enzyme / Organism data:
    print 'Parsing KEGG'
    kegg_utils.load(reaction_manager)

    print 'Parsing Rhea'
    rhea_utils.load(reaction_manager)

    files.append(chemical_manager.get_files())
    files.append(reaction_manager.get_files())

    print 'Creating DB'
    __create_db(db_loc, files)


def __create_db(db_loc, files):
    '''Creates the database from csv files.'''
    if os.path.exists(db_loc):
        shutil.rmtree(db_loc)

    files = [list(elem) for elem in zip(*files)]
    files = [sorted([item for f in fle for item in f]) for fle in files]

    for i in range(len(files[0])):
        files[0].insert(i * 2, '--nodes')

    for i in range(len(files[1])):
        files[1].insert(i * 2, '--relationships')

    # Import database:
    params = ['neo4j-import', '--into', db_loc] + files[0] + files[1]
    subprocess.call(params)

    # Index database:
    with open('init.cql', 'rU') as init_file:
        init = init_file.read()
        params = ['neo4j-shell', '-path', db_loc, '-c', init]
        subprocess.call(params)


def main(argv):
    '''main method'''
    build(*argv)

if __name__ == '__main__':
    main(sys.argv[1:])
