import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MsgModelTestCase(TestCase):
    """test mesg views"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        
        self.u = User.signup("test", "test@email.com", "password", None)
        uid = 999
        self.u.id = uid

        self.u2 = User.signup("test2", "test2@email.com", "password", None)
        u2_id = 101010
        self.u2.id = u2_id

        db.session.add(self.u)
        db.session.add(self.u2)
        db.session.commit()

        self.u = User.query.get(self.u.id)

        msg1 = Message(
            text="m1",
            user_id=self.u.id
        )

        msg2 = Message(
            text="m2",
            user_id=self.u.id 
        )

        db.session.add(msg1)
        db.session.add(msg2)
        db.session.commit()

        self.u.likes.append(msg1)

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):    
        msg = Message(
            text="test",
            user_id=self.u.id
        )

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.u.messages), 3)
        self.assertEqual(self.u.messages[0].text, "m1")
    
    def test_message_likes(self):
        l = Likes.query.filter_by(user_id = 999).all()
        self.assertEqual(len(l), 1)
