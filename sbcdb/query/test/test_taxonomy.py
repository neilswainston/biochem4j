'''
SYNBIOCHEM-DB (c) University of Manchester 2015

SYNBIOCHEM-DB is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
# pylint: disable=too-many-public-methods
import unittest

from sbcdb.query import taxonomy


class TestTaxonomy(unittest.TestCase):
    '''Test class for taxonomy.'''

    def test_get_children_by_id(self):
        '''Tests get_children_by_id method.'''
        children = taxonomy.get_children_by_id('83333')
        self.assertTrue('511145' in [child['taxonomy'] for child in children])

    def test_get_parent_by_id(self):
        '''Tests get_parent_by_id method.'''
        self.assertEquals(taxonomy.get_parent_by_id('511145')['taxonomy'],
                          '83333')

    def test_get_parent_by_name(self):
        '''Tests taxonomy method.'''
        name = 'Escherichia coli str. K-12 substr. MG1655'

        self.assertEquals(taxonomy.get_parent_by_name(name)['taxonomy'],
                          '83333')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
