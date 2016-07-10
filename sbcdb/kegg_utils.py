'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
import urllib2


def load(reaction_manager, organisms=None):
    '''Loads KEGG data.'''
    # KEGG Reaction to EC:
    kegg_reac_ec = _parse('http://rest.kegg.jp/link/ec/reaction')

    if organisms is None:
        organisms_url = 'http://rest.kegg.jp/list/organism'
        organisms = sorted([line.split()[1]
                            for line in urllib2.urlopen(organisms_url)])

    # EC to gene, gene to Uniprot:
    ec_genes = {}
    gene_uniprots = {}

    for org in organisms:
        print 'KEGG: loading ' + org

        ec_genes.update(_parse(
            'http://rest.kegg.jp/link/' + org.lower() + '/enzyme'))
        gene_uniprots.update(_parse(
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

    reaction_manager.add_react_to_enz(data, 'kegg.reaction')


def _parse(url, attempts=128):
    '''Parses url to form key to list of values dictionary.'''
    data = {}

    for _ in range(attempts):
        try:
            for line in urllib2.urlopen(url):
                tokens = line.split()

                if len(tokens) > 1:
                    if tokens[0] in data:
                        data[tokens[0]].append(tokens[1])
                    else:
                        data[tokens[0]] = [tokens[1]]

                return data
        except urllib2.URLError, err:
            # Take no action, but try again...
            print '\t'.join([url, str(err)])

    return data
