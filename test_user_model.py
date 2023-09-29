"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        test_user1 = User.signup('tU1', 'tu1@email.com', 'password', None)
        id1 = 1
        test_user1.id = id1

        test_user2 = User.signup('tU2', 'tu2@email.com', 'password', None)
        id3 = 3
        test_user1.id = id3
        
        db.session.commit()

        test_user1 = User.query.get_or_404(id1)
        test_user2 = User.query.get_or_404(id3)

        self.test_user1 = test_user1
        self.id1 = id1

        self.test_user2 = test_user2
        self.id3 = id3

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_follows(self):
        self.test_user1.following.append(self.test_user2)
        db.session.commit()

        self.assertEqual(len(self.test_user2.following), 0)
        self.assertEqual(len(self.test_user2.followers), 1)
        self.assertEqual(len(self.test_user1.followers), 0)
        self.assertEqual(len(self.test_user1.following), 1)

        self.assertEqual(self.test_user2.followers[0].id, self.test_user1.id)
        self.assertEqual(self.test_user1.following[0].id, self.test_user2.id)

    def test_is_following(self):
        self.test_user1.following.append(self.test_user2)
        db.session.commit()

        self.assertTrue(self.test_user1.is_following(self.test_user2))

    def test_is_followed(self):
        self.test_user1.following.append(self.test_user2)
        db.session.commit()

        self.assertTrue(self.test_user2.is_followed_by(self.test_user1))
    
    def test_register(self):
        new_test_user = User.signup('newTU', 'newTU@email.com', 'password', None)
        new_uid = 11
        new_test_user.id = new_uid
        db.session.commit()

        new_test_user = User.query.get(new_uid)
        self.assertIsNotNone(new_test_user)
        self.assertEqual(new_test_user.username, "newTU")
        self.assertEqual(new_test_user.email, "newTU@email.com")
        self.assertNotEqual(new_test_user.password, "password")
        self.assertTrue(new_test_user.password.startswith("$2b$"))

    def test_bad_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("test_user_1", "tu@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("test_user_2", "tu2@email.com", None, None)

    def test_valid_authentication(self):
        u = User.authenticate(self.test_user1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.id1)

