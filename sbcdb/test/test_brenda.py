'''
synbiochem (c) University of Manchester 2015

synbiochem is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
# pylint: disable=too-many-public-methods
import getpass
import unittest

from sbcdb.brenda import BrendaReader


class TestBrendaReader(unittest.TestCase):
    '''Test class for BrendaReader.'''

    @classmethod
    def setUpClass(cls):
        username = raw_input('BRENDA username: ')
        password = getpass.getpass(prompt='BRENDA password: ')
        cls.__reader = BrendaReader(password, username)

    def test_get_km_values(self):
        '''Tests get_km_values method.'''

        self.assertTrue(
            len(self.__reader.get_km_values('1.1.1.1', 'Homo sapiens')) > 0)

    def test_get_kcat_values(self):
        '''Tests get_kcat_values method.'''
        self.assertTrue(
            len(self.__reader.get_kcat_values('1.1.1.1', 'Homo sapiens')) > 0)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
