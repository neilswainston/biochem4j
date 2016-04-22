'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import urllib2

from sbcdb import reaction_utils


def load(enzyme_source):
    print 'kegg_utils.load'
    '''Loads KEGG data.'''

    # KEGG Reaction to EC:
    kegg_reac_ec = __parse('http://rest.kegg.jp/link/ec/reaction')

    organisms_url = 'http://rest.kegg.jp/list/organism'
    organisms = [line.split()[1]
                 for line in urllib2.urlopen(organisms_url)][12:13]

    # EC to gene, gene to Uniprot:
    ec_genes = {}
    gene_uniprots = {}

    for org in organisms:
        ec_genes.update(__parse(
            'http://rest.kegg.jp/link/' + org.lower() + '/enzyme'))
        gene_uniprots.update(__parse(
            'http://rest.kegg.jp/conv/uniprot/' + org.lower()))

    data = {}

    for kegg_reac, ec_terms in kegg_reac_ec.iteritems():
        for ec_term in ec_terms:
            if ec_term in ec_genes:
                for gene in ec_genes[ec_term]:
                    if gene in gene_uniprots:
                        data.update(
                            {kegg_reac[3:]: [val[3:]
                                             for val in gene_uniprots[gene]]})

    return reaction_utils.submit(data, 'kegg.reaction', enzyme_source)


def __parse(url):
    print 'kegg_utils._parse'
    '''Parses url to form key to list of values dictionary.'''
    data = {}

    for line in urllib2.urlopen(url):
        tokens = line.split()

        if tokens[0] in data:
            data[tokens[0]].append(tokens[1])
        else:
            data[tokens[0]] = [tokens[1]]

    return data


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main(sys.argv[1:])
