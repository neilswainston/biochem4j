'''
Grimoire (c) University of Manchester 2015

Grimoire is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from grimoire import mnxref_utils

CHEBI = 'chebi'


__NAMESPACES = {
    # value (namespace) corresponds to identifiers.org:
    'bigg': 'bigg.metabolite',
    'CAS Registry Number': 'cas',
    'chebi': 'chebi',
    'ChemIDplus accession': 'chemidplus',
    'Chemspider accession': 'chemspider',
    'DrugBank accession': 'drugbank',
    'hmdb': 'hmdb',
    'HMDB accession': 'hmdb',
    'kegg': 'kegg.compound',
    'KEGG COMPOUND accession': 'kegg.compound',
    'KEGG DRUG accession': 'kegg.drug',
    'KEGG GLYCAN accession': 'kegg.glycan',
    'KNApSAcK accession': 'knapsack',
    'lipidmaps': 'lipidmaps',
    'LIPID MAPS instance accession': 'lipidmaps',
    'MolBase accession': 'molbase',
    'PDB accession': 'pdb',
    'PubMed citation': 'pubmed',
    'reactome': 'reactome',
    'RESID accession': 'resid',
    'seed': 'seed.compound',
    'umbbd': 'umbbd.compound',
    'UM-BBD compID': 'umbbd.compound',
    'upa': 'unipathway',
    'Wikipedia accession': 'wikipedia.en',

    # Not in identifiers.org:
    'metacyc': 'metacyc',
    'MetaCyc accession': 'metacyc'
}


def resolve_namespace(name):
    '''Maps name to distinct namespace from identifiers.org.'''
    return __NAMESPACES[name] if name in __NAMESPACES else None


def load(url):
    '''Loads data into neo4j from a number of sources.'''
    graph = mnxref_utils.load(url)
    print graph
