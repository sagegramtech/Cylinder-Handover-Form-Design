import reflex as rx
from pymongo import MongoClient, errors
from typing import Any

MONGO_URI_TEMPLATE = "mongodb+srv://{db_username}:{db_password}@cluster0.hoaldgw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


class AuthState(rx.State):
    username_form_input: str = ""
    password_form_input: str = ""
    authenticated_username: str | None = None
    _authenticated_password_DO_NOT_EXPOSE: str | None = None
    is_authenticated: bool = False

    @rx.event
    def sign_in(self, form_data: dict):
        self.username_form_input = form_data.get(
            "username", ""
        )
        self.password_form_input = form_data.get(
            "password", ""
        )
        if (
            not self.username_form_input
            or not self.password_form_input
        ):
            yield rx.toast.error(
                "Username and password are required."
            )
            return
        current_username = self.username_form_input
        current_password = self.password_form_input
        uri = MONGO_URI_TEMPLATE.format(
            db_username=current_username,
            db_password=current_password,
        )
        try:
            client = MongoClient(
                uri, serverSelectionTimeoutMS=5000
            )
            client.admin.command("ping")
            self.is_authenticated = True
            self.authenticated_username = current_username
            self._authenticated_password_DO_NOT_EXPOSE = (
                current_password
            )
            self.username_form_input = ""
            self.password_form_input = ""
            client.close()
            return rx.redirect("/handover_entry_p1")
        except errors.ConnectionFailure:
            self.is_authenticated = False
            self.authenticated_username = None
            self._authenticated_password_DO_NOT_EXPOSE = (
                None
            )
            yield rx.toast.error(
                "Sign-in failed: Could not connect to the database. Check network or DB status."
            )
        except errors.OperationFailure:
            self.is_authenticated = False
            self.authenticated_username = None
            self._authenticated_password_DO_NOT_EXPOSE = (
                None
            )
            yield rx.toast.error(
                "Sign-in failed: Invalid username or password."
            )
        except Exception as e:
            self.is_authenticated = False
            self.authenticated_username = None
            self._authenticated_password_DO_NOT_EXPOSE = (
                None
            )
            yield rx.toast.error(
                f"An unexpected error occurred: {str(e)}"
            )

    @rx.event
    def sign_out(self):
        self.is_authenticated = False
        self.authenticated_username = None
        self._authenticated_password_DO_NOT_EXPOSE = None
        self.username_form_input = ""
        self.password_form_input = ""
        return rx.redirect("/sign-in")

    @rx.event
    def check_session(self):
        if not self.is_authenticated:
            return rx.redirect("/sign-in")