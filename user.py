from time import time
from dataclasses import dataclass
from flask import session
import gomoku


class User:
    last_checkin: float

    def __init__(self):
        self.refresh()

    def refresh(self) -> None:
        self.last_checkin = time()

    def get_displayed_name(self) -> str:
        raise NotImplementedError


@dataclass
class GuestUser(User):
    ip: str

    def get_displayed_name(self) -> str:
        return self.ip

    def __post_init__(self):
        super().__init__()


@dataclass
class RegisteredUser(User):
    token: str
    displayed_name: str

    def get_displayed_name(self) -> str:
        return self.displayed_name

    def __hash__(self):
        return self.token.__hash__()

    def __post_init__(self):
        super().__init__()


def get_current_user() -> User:
    if session["user"]:
        print(session["user"])
        return RegisteredUser(str(session["user"]["access_token"]), str(session["user"]["userinfo"]["name"]))
    return GuestUser(gomoku.get_client_ip())
