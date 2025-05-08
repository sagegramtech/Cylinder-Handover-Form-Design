import reflex as rx
from app.components.sign_in_card import sign_in_card


def sign_in_page() -> rx.Component:
    return rx.el.div(
        sign_in_card(),
        class_name="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 px-4",
    )