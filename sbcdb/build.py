'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys

from sbcdb import chebi_utils, chemical_utils, kegg_utils, mnxref_utils, \
    ncbi_taxonomy_utils, reaction_utils, rhea_utils, spectra_utils, utils


def build_csv(dest_dir):
    '''Build database CSV files.'''
    writer = utils.Writer(dest_dir)

    # Get Organism data:
    print 'Parsing NCBI Taxonomy'
    ncbi_taxonomy_utils.load(writer)

    # Get Chemical and Reaction data:
    reac_man = _write_chem_csv_files(writer)

    # Get Reaction / Enzyme / Organism data:
    print 'Parsing KEGG'
    kegg_utils.load(reac_man)

    print 'Parsing Rhea'
    rhea_utils.load(reac_man)

    reac_man.get_files()


def _write_chem_csv_files(writer):
    '''Write chemistry csv files.'''
    chem_man = chemical_utils.ChemicalManager()
    reac_man = reaction_utils.ReactionManager()

    print 'Parsing MNXref'
    mnx_loader = mnxref_utils.MnxRefLoader(chem_man, reac_man, writer)
    mnx_loader.load()

    print 'Parsing ChEBI'
    chebi_utils.load(chem_man, writer)

    # Get Spectrum data:
    print 'Parsing spectrum data'
    spectra_utils.load(writer, chem_man)

    chem_man.write_files(writer)

    return reac_man


def main(argv):
    '''main method'''
    build_csv(argv[0])


if __name__ == '__main__':
    main(sys.argv[1:])
