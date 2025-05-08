import reflex as rx
from app.states.auth_state import AuthState


def sign_in_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Sign In",
            class_name="text-2xl font-bold mb-6 text-center text-gray-700",
        ),
        rx.el.form(
            rx.el.div(
                rx.el.label(
                    "Username",
                    class_name="block text-sm font-medium text-gray-700",
                ),
                rx.el.input(
                    type="text",
                    name="username",
                    placeholder="Enter your database username",
                    required=True,
                    class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label(
                    "Password",
                    class_name="block text-sm font-medium text-gray-700",
                ),
                rx.el.input(
                    type="password",
                    name="password",
                    placeholder="Enter your database password",
                    required=True,
                    class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                ),
                class_name="mb-6",
            ),
            rx.el.button(
                "Sign In",
                type="submit",
                class_name="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
            ),
            on_submit=AuthState.sign_in,
            class_name="space-y-6",
        ),
        class_name="max-w-md w-full bg-white p-8 rounded-lg shadow-xl border border-gray-200",
    )