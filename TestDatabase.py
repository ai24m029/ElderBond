import unittest
from ElderBond import app 
from flask import jsonify
import json

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):

        self.app = app.test_client()
        self.app.testing = True

    def test_search(self):
  
        search_user = 'TestUser'
        response = self.app.get(f'/search?user={search_user}')
        
      
        self.assertEqual(response.status_code, 200)
        
     
        html = response.data.decode('utf-8')
        
      
        self.assertIn(search_user, html)
        

if __name__ == '__main__':
    unittest.main()
