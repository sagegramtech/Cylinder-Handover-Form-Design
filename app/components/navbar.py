import reflex as rx
from app.states.auth_state import AuthState
from app.states.cylinder_state import CylinderState


def navbar() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.a(
                "Cylinder Handover",
                href="/handover_entry_p1",
                class_name="text-white text-lg font-semibold hover:text-indigo-200",
            ),
            rx.el.div(
                rx.el.a(
                    "New Entry",
                    href="/handover_entry_p1",
                    on_click=CylinderState.clear_form_and_reset_to_p1,
                    class_name="text-gray-300 hover:bg-indigo-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium",
                ),
                rx.el.a(
                    "View Submissions",
                    href="/submissions",
                    class_name="text-gray-300 hover:bg-indigo-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium",
                ),
                rx.el.button(
                    "Sign Out",
                    on_click=AuthState.sign_out,
                    class_name="ml-4 text-gray-300 hover:bg-indigo-700 hover:text-white px-3 py-2 rounded-md text-sm font-medium bg-transparent border-none",
                ),
                class_name="flex items-center space-x-4",
            ),
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16",
        ),
        class_name="bg-indigo-600 shadow-md",
    )


def main_layout(page_content: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_authenticated,
            navbar(),
            rx.fragment(),
        ),
        rx.el.main(
            rx.el.div(
                page_content,
                class_name="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8",
            )
        ),
        class_name="min-h-screen bg-gray-100",
    )