'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import sys
import urllib2

from sbcdb import py2neo_utils, reaction_utils


def load(url, organisms=None):
    '''Loads KEGG data.'''

    # KEGG Reaction to EC:
    kegg_reac_ec = __parse('http://rest.kegg.jp/link/ec/reaction')

    if organisms is None:
        organisms = [line.split()[1]
                     for line in urllib2.urlopen(
            'http://rest.kegg.jp/list/organism')]

    # EC to gene, gene to Uniprot:
    ec_genes = {}
    gene_uniprots = {}

    for org in organisms:
        ec_genes.update(__parse(
            'http://rest.kegg.jp/link/' + org.lower() + '/enzyme'))
        gene_uniprots.update(__parse(
            'http://rest.kegg.jp/conv/uniprot/' + org.lower()))

    data = {}

    # for ec_term in set(kegg_reac_ec.values()):
    #    print ec_term
    #    ec_genes[ec_term] = __parse_ec('http://rest.kegg.jp/get/' + ec_term,
    #                                   org_genes)

    for kegg_reac, ec_terms in kegg_reac_ec.iteritems():
        for ec_term in ec_terms:
            if ec_term in ec_genes:
                for gene in ec_genes[ec_term]:
                    if gene in gene_uniprots:
                        data.update(
                            {kegg_reac[3:]: [val[3:]
                                             for val in gene_uniprots[gene]]})

    # Contact Neo4j database, create Graph object:
    reaction_utils.submit(py2neo_utils.get_graph(url), data, 'kegg.reaction')


def __parse(url):
    '''Parses url to form key to list of values dictionary.'''
    data = {}

    for line in urllib2.urlopen(url):
        tokens = line.split()

        if tokens[0] in data:
            data[tokens[0]].append(tokens[1])
        else:
            data[tokens[0]] = [tokens[1]]

    return data


def __parse_ec(url, org_genes):
    '''Parses a KEGG EC entry.'''
    in_genes = False
    genes = []

    for line in urllib2.urlopen(url):
        if line.startswith('GENES'):
            in_genes = True
            line = line[len('GENES'):]

        if in_genes:
            if line.startswith(' '):
                tokens = line.strip().split(':')
                org = tokens[0]
                gene_ids = [x[:x.index('(')] if '(' in x else x
                            for x in tokens[1].strip().split()]

                if org not in org_genes:
                    org_genes[org] = gene_ids
                else:
                    org_genes[org].extend(gene_ids)

                genes.extend([org + ':' + gene_id for gene_id in gene_ids])
            else:
                break

    return genes


def main(argv):
    '''main method'''
    load(*argv)


if __name__ == "__main__":
    main([sys.argv[1], sys.argv[2:]])
