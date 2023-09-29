import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserMsgTestCase(TestCase):
    """test user views of msg"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.t_user = User.signup("tu","tu@email.com","password",None)
        tu_id = 111
        self.t_user.id = tu_id

        self.u1 = User.signup("one", "one@email.com", "password", None)
        u1_id = 222
        self.u1.id = u1_id

        self.u2 = User.signup("two", "two@email.com", "password", None)
        u2_id = 333
        self.u2.id = u2_id

        self.u3 = User.signup("three", "three@email.com", "password", None)
        u3_id = 444
        self.u3.id = u3_id

        db.session.commit()

        m1 = Message(id=888, text="like1", user_id=self.t_user.id)
        m2 = Message(id=777, text="like2", user_id=self.t_user.id)
        m3 = Message(id=555, text="like3", user_id=self.u1.id)
        db.session.add(m1)
        db.session.add(m2)
        db.session.add(m3)
        db.session.commit()

        like = Likes(user_id = self.t_user.id, message_id=555 )
        db.session.add(like)
        db.session.commit()

        followTu = Follows(user_being_followed_id=self.t_user.id, user_following_id=self.u1.id)
        db.session.add(followTu)
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    
    def test_show_users(self):
        with self.client as c:
            resp = c.get('/users')

            self.assertIn("tu", str(resp.data))
            self.assertIn("one", str(resp.data))
            self.assertIn("two", str(resp.data))
            self.assertIn("three", str(resp.data))

    def test_show_user(self):
        with self.client as c:
            resp = c.get(f"/users/{self.t_user.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("tu", str(resp.data))

    def test_show_user_likes(self):
        t_user_likes = Likes.query.filter_by(user_id=111).all()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.t_user.id
            resp = c.get(f"/users/{self.t_user.id}/likes")

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(t_user_likes), 1)


    def test_add_like(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2.id
            resp = c.post("/users/add_like/888", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            u2_likes = Likes.query.filter_by(message_id=888).all()
            self.assertEqual(len(u2_likes), 1)
            self.assertEqual(u2_likes[0].user_id, self.u2.id)

    def test_rmv_like(self):
        msg = Likes.query.filter_by(message_id=555).all()
        self.assertIsNotNone(msg)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.t_user.id

            resp = c.post("/users/555/like/remove", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            t_user_likes = Likes.query.filter_by(user_id=111).all()
            self.assertEqual(len(t_user_likes), 0)



        

