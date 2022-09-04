import sqlalchemy
import sqlalchemy.orm
import datetime


class ServerDatabaseManager:
    class Users:
        def __init__(self, username) -> None:
            self.username = username
            self.last_seen = datetime.datetime.now()
            self.id = None

    class OnlineUsers:
        def __init__(self, user_id, ip_address, port, login_time) -> None:
            self.user_id = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        def __init__(self, user_id, date, ip_address, port):
            self.user_id = user_id
            self.date = date
            self.ip_address = ip_address
            self.port = port
            self.id = None

    def __init__(self) -> None:
        self.db_engine = sqlalchemy.create_engine("sqlite:///server_base.db3", echo=False)
        self.metadata = sqlalchemy.MetaData()
        users_table = sqlalchemy.Table("Users", self.metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("username", sqlalchemy.String, unique=True),
            sqlalchemy.Column("last_seen", sqlalchemy.DateTime),
        )
        online_users = sqlalchemy.Table("Online_users", self.metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("Users.id"), unique=True),
            sqlalchemy.Column("ip_address", sqlalchemy.String),
            sqlalchemy.Column("port", sqlalchemy.String),
            sqlalchemy.Column("login_time", sqlalchemy.DateTime),
        )
        login_history = sqlalchemy.Table("Login_history", self.metadata,
            sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column("date", sqlalchemy.DateTime),
            sqlalchemy.Column("ip_address", sqlalchemy.String),
            sqlalchemy.Column("port", sqlalchemy.String),
            sqlalchemy.Column("user_id", sqlalchemy.ForeignKey("Users.id")),
        )
        self.metadata.create_all(self.db_engine)
        sqlalchemy.orm.mapper(self.Users, users_table)
        sqlalchemy.orm.mapper(self.OnlineUsers, online_users)
        sqlalchemy.orm.mapper(self.LoginHistory, login_history)

        Session = sqlalchemy.orm.sessionmaker(bind=self.db_engine)
        self.session = Session()

        self.session.query(self.OnlineUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        print(f"{username} login {ip_address}:{port}")
        query = self.session.query(self.Users).filter_by(username=username)
        if query.count():
            user = query.first()
            user.last_seen = datetime.datetime.now()
        else:
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()

        online_record = self.OnlineUsers(user_id=user.id, ip_address=ip_address, port=port, login_time=user.last_seen)
        login_log = self.LoginHistory(user_id=user.id, date=user.last_seen, ip_address=ip_address, port=port)
        self.session.add(online_record)
        self.session.add(login_log)
        self.session.commit()

    def user_logout(self, username):
        print(f"{username} logout")
        user = self.session.query(self.Users).filter_by(username=username).first()
        self.session.query(self.OnlineUsers).filter_by(user_id=user.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.Users.username,
            self.Users.last_seen,
        )
        return query.all()

    def get_online_users(self):
        query = self.session.query(
            self.Users.username,
            self.OnlineUsers.ip_address,
            self.OnlineUsers.port,
            self.OnlineUsers.login_time
            ).join(self.OnlineUsers)
        return query.all()

    def login_history(self, username=None):
        query = self.session.query(
            self.Users.username,
            self.LoginHistory.date,
            self.LoginHistory.ip_address,
            self.LoginHistory.port
            ).join(self.Users)
        if username:
            query = query.filter(self.Users.username == username)
        return query.all()

if __name__ == '__main__':
    test_db = ServerDatabaseManager()
    # выполняем 'подключение' пользователя
    test_db.user_login('client_1', '192.168.1.4', 8888)
    test_db.user_login('client_2', '192.168.1.5', 7777)
    # выводим список кортежей - активных пользователей
    print(test_db.get_online_users())
    # выполянем 'отключение' пользователя
    test_db.user_logout('client_1')
    # выводим список активных пользователей
    print(test_db.get_online_users())
    # запрашиваем историю входов по пользователю
    test_db.login_history('client_1')
    # выводим список известных пользователей
    print(test_db.users_list())
