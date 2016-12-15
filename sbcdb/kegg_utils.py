'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
from collections import defaultdict
import urllib2


def load(reaction_manager, organisms=None):
    '''Loads KEGG data.'''

    if organisms is None:
        organisms = \
            sorted([line.split()[1] for line in
                    urllib2.urlopen('http://rest.kegg.jp/list/organism')])

    # EC to gene, gene to Uniprot:
    ec_genes, gene_uniprots = _get_gene_data(organisms)

    data = defaultdict(list)

    # KEGG Reaction to EC:
    kegg_reac_ec = _parse('http://rest.kegg.jp/link/ec/reaction')

    for kegg_reac, ec_terms in kegg_reac_ec.iteritems():
        for ec_term in ec_terms:
            if ec_term in ec_genes:
                for gene in ec_genes[ec_term]:
                    if gene in gene_uniprots:
                        uniprots = [val[3:] for val in gene_uniprots[gene]]
                        data[kegg_reac[3:]].extend(uniprots)

    reaction_manager.add_react_to_enz(data, 'kegg.reaction')


def _parse(url, attempts=128):
    '''Parses url to form key to list of values dictionary.'''
    data = defaultdict(list)

    for _ in range(attempts):
        try:
            for line in urllib2.urlopen(url):
                tokens = line.split()

                if len(tokens) > 1:
                    data[tokens[0]].append(tokens[1])

            return data
        except urllib2.URLError, err:
            # Take no action, but try again...
            print '\t'.join([url, str(err)])

    return data


def _get_gene_data(organisms):
    '''Gets gene data.'''
    ec_genes = defaultdict(list)
    gene_uniprots = defaultdict(list)

    for org in organisms:
        print 'KEGG: loading ' + org

        for key, value in _parse('http://rest.kegg.jp/link/' + org.lower() +
                                 '/enzyme').iteritems():
            ec_genes[key].extend(value)

        for key, value in _parse('http://rest.kegg.jp/conv/uniprot/' +
                                 org.lower()).iteritems():
            gene_uniprots[key].extend(value)

    return ec_genes, gene_uniprots
