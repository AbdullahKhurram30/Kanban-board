import unittest
from app import app, db
from faker import Faker
from app.routes import User

class TestUser(unittest.TestCase):
    def setUp(self):
        '''
        This function is used to setup the test environment
        '''
        with app.app_context():
            app.config['TESTING'] = True
            app.config['DEBUG'] = False
            self.app = app.test_client()
            db.create_all()

    def tearDown(self):
        '''
        This function is used to tear down the test environment
        '''
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def user_creation():
        '''
        This function is used to create a user for testing purposes
        '''
        fake = Faker()
        user = User(username='John', password=fake.password())
        db.session.add(user)
        db.session.commit()
        return user
    
    def test_user_creation(self):
        '''
        This function is used to test the user creation and ensure that the user is created in the database
        '''
        with app.app_context():
            TestUser.user_creation()
            query = User.query.filter_by(username='John').first()
            self.assertEqual(query.username, 'John')

    def test_login(self):
        '''
        This function is used to test the login functionality
        '''
        with app.app_context():
            TestUser.user_creation()
            response = self.app.post('/login', data=dict(username='John', password='password'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_logout(self):
        '''
        This function is used to test the logout functionality
        '''
        with app.app_context():
            TestUser.user_creation()
            response = self.app.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_register(self):
        '''
        This function is used to test the register functionality
        '''
        with app.app_context():
            TestUser.user_creation()
            response = self.app.post('/register', data=dict(username='John', password='password'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_home(self):
        '''
        This function is used to test the home functionality
        '''
        with app.app_context():
            TestUser.user_creation()
            response = self.app.get('/', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()