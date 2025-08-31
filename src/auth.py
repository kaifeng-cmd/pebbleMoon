from .database import Database


class Auth:
    def __init__(self) -> None:
        self.db = Database()

    def sign_up(self, email: str, password: str):
        return self.db.client.auth.sign_up({"email": email, "password": password})

    def sign_in(self, email: str, password: str):
        return self.db.client.auth.sign_in_with_password({"email": email, "password": password})

    def sign_out(self) -> None:
        self.db.client.auth.sign_out()

    def get_current_user(self):
        return self.db.client.auth.get_user()
