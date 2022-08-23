from pydoc import cli
import unittest
from client_api_new import client
from client_api_old import client_two

class TestAPI(unittest.TestCase):

    def test_positive_dif(self):
        result_new = client.positive_dif() 
        result_old = client_two.positive_dif()
        self.assertEqual(result_new,result_old)

    def test_negative_dif(self):
        result_new = client.negative_dif() 
        result_old = client_two.negative_dif()
        self.assertEqual(result_new,result_old)