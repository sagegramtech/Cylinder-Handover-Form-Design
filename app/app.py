import reflex as rx
from app.states.auth_state import AuthState
from app.states.cylinder_state import CylinderState
from app.pages.sign_in_page import sign_in_page
from app.pages.handover_entry_page_1 import (
    handover_entry_page_1,
)
from app.pages.handover_entry_page_2 import (
    handover_entry_page_2,
)
from app.pages.submissions_page import submissions_page

app = rx.App(theme=rx.theme(appearance="light"))
app.add_page(sign_in_page, route="/sign-in")
app.add_page(sign_in_page, route="/")
app.add_page(
    handover_entry_page_1,
    route="/handover_entry_p1",
    on_load=AuthState.check_session,
)
app.add_page(
    handover_entry_page_2,
    route="/handover_entry_p2",
    on_load=AuthState.check_session,
)
app.add_page(
    submissions_page,
    route="/submissions",
    on_load=[
        AuthState.check_session,
        CylinderState.fetch_db_submissions,
    ],
)