import datetime
import json

from data import db_session
from data.sounds import Sound
from data.users import User


def add_test_users(db_sess):
    user = User()
    user.name = 'Jerainee'
    user.about = 'ШедевроОписание'
    user.email = 'ilinspavel07@gmail.com'
    user.password = '11111'
    user.created_date = datetime.datetime.now()

    db_sess.add(user)
#  db_sess.commit()
