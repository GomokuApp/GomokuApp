from time import time
from dataclasses import dataclass, field
from flask import session
import gomoku


class User:
    last_checkin: float = time()

    def refresh(self) -> None:
        self.last_checkin = time()

    def get_displayed_name(self) -> str:
        raise NotImplementedError

    def get_profile_picture(self) -> str:
        return "/static/gomoku/avatar/default.png"


@dataclass
class GuestUser(User):
    ip: str

    def get_displayed_name(self) -> str:
        return self.ip


@dataclass
class RegisteredUser(User):
    token: str
    displayed_name: str = field(compare=False)
    profile_picture: str = field(compare=False)

    def get_displayed_name(self) -> str:
        return self.displayed_name

    def get_profile_picture(self) -> str:
        return self.profile_picture


def get_current_user() -> User:
    if session.get("user"):
        print(session["user"])
        return RegisteredUser(str(session["user"]["access_token"]),
                              str(session["user"]["userinfo"]["name"]),
                              str(session["user"]["userinfo"]["picture"])
                              )
    return GuestUser(gomoku.get_client_ip())
