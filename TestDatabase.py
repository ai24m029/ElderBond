import unittest
from ElderBond import app  # Importiere die Flask-App
from flask import jsonify
import json

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Wir setzen die Testumgebung für die Flask-App
        self.app = app.test_client()
        self.app.testing = True

    def test_search(self):
        # Beispiel für eine Suchanfrage nach einem Benutzer (user='test_user')
        search_user = 'TestUser'
        response = self.app.get(f'/search?user={search_user}')
        
        # Überprüfen, ob der Statuscode 200 (OK) zurückgegeben wird
        self.assertEqual(response.status_code, 200)
        
        # Überprüfen, ob die Antwort die gesuchten Posts enthält
        # In deinem Fall gibt es keine JSON-Antwort, sondern die HTML-Seite mit den Posts
        # Wir suchen also nach einer spezifischen HTML-Struktur
        html = response.data.decode('utf-8')
        
        # Sicherstellen, dass der Benutzername im HTML-Inhalt enthalten ist
        self.assertIn(search_user, html)
        

if __name__ == '__main__':
    unittest.main()
