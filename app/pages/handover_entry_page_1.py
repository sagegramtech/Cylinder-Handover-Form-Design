import reflex as rx
from app.states.cylinder_state import CylinderState
from app.components.navbar import main_layout


def handover_entry_page_1() -> rx.Component:
    return main_layout(
        rx.el.div(
            rx.el.h1(
                "Cylinder Handover Entry - Part 1",
                class_name="text-3xl font-bold text-gray-800 mb-8",
            ),
            rx.el.form(
                rx.el.section(
                    rx.el.h2(
                        "Handover Details",
                        class_name="text-xl font-semibold text-gray-700 mb-4 border-b pb-2",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Facility *",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.select(
                            rx.el.option(
                                "Select Facility",
                                value="",
                                disabled=True,
                            ),
                            rx.foreach(
                                CylinderState.facilities,
                                lambda facility: rx.el.option(
                                    facility, value=facility
                                ),
                            ),
                            default_value=CylinderState.selected_facility,
                            on_change=CylinderState.set_selected_facility,
                            required=True,
                            class_name="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "BMT In Charge",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.p(
                            CylinderState.bmt_in_charge_display,
                            class_name="mt-1 p-2 bg-gray-100 border border-gray-300 rounded-md text-gray-700",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Personnel Receiving Cylinders (Optional)",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            type="text",
                            name="receiving_personnel",
                            default_value=CylinderState.receiving_personnel,
                            class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                        ),
                        class_name="mb-4",
                    ),
                    class_name="mb-8 p-6 bg-white rounded-lg shadow border",
                ),
                rx.el.section(
                    rx.el.h2(
                        "Cylinder Quantity *",
                        class_name="text-xl font-semibold text-gray-700 mb-4 border-b pb-2",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "2 Cubic Meter *",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            type="number",
                            name="qty_2m",
                            min="0",
                            default_value=CylinderState.qty_2m.to_string(),
                            required=True,
                            class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "4 Cubic Meter *",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            type="number",
                            name="qty_4m",
                            min="0",
                            default_value=CylinderState.qty_4m.to_string(),
                            required=True,
                            class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "7 Cubic Meter *",
                            class_name="block text-sm font-medium text-gray-700",
                        ),
                        rx.el.input(
                            type="number",
                            name="qty_7m",
                            min="0",
                            default_value=CylinderState.qty_7m.to_string(),
                            required=True,
                            class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
                        ),
                        class_name="mb-4",
                    ),
                    class_name="p-6 bg-white rounded-lg shadow border",
                ),
                rx.el.button(
                    "Next",
                    type="submit",
                    class_name="w-full mt-6 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
                ),
                on_submit=CylinderState.handle_page_1_submit,
                reset_on_submit=False,
            ),
            class_name="max-w-2xl mx-auto",
        )
    )