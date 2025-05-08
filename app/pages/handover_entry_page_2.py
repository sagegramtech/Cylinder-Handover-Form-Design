import reflex as rx
from app.states.cylinder_state import (
    CylinderState,
    CylinderCheckData,
)
from app.components.navbar import main_layout
from typing import List


def cylinder_check_row(
    size_key: str,
    check_data_list_var: rx.Var[List[CylinderCheckData]],
    index: int,
    cylinder_label_prefix: str,
) -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            f"{cylinder_label_prefix} Cylinder {index + 1}",
            class_name="text-lg font-semibold text-indigo-700 mb-3 border-b border-indigo-200 pb-2",
        ),
        rx.el.div(
            rx.el.label(
                "Cylinder ID (Optional)",
                class_name="block text-sm font-medium text-gray-700",
            ),
            rx.el.input(
                type="text",
                default_value=check_data_list_var[index][
                    "cylinder_id"
                ].to_string(),
                on_change=lambda val: CylinderState.update_cylinder_check_field(
                    size_key, index, "cylinder_id", val
                ),
                class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Purity (%) *",
                class_name="block text-sm font-medium text-gray-700",
            ),
            rx.el.input(
                type="number",
                min="0",
                max="99",
                step="0.1",
                default_value=check_data_list_var[index][
                    "purity"
                ].to_string(),
                on_change=lambda val: CylinderState.update_cylinder_check_field(
                    size_key, index, "purity", val
                ),
                required=True,
                class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Pressure (psi) *",
                class_name="block text-sm font-medium text-gray-700",
            ),
            rx.el.input(
                type="number",
                min="0",
                max="2000",
                step="1",
                default_value=check_data_list_var[index][
                    "pressure"
                ].to_string(),
                on_change=lambda val: CylinderState.update_cylinder_check_field(
                    size_key, index, "pressure", val
                ),
                required=True,
                class_name="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm",
            ),
            class_name="mb-4",
        ),
        class_name="p-6 bg-white rounded-lg shadow-md border border-gray-200 mb-6 transition-all hover:shadow-lg",
    )


def cylinder_checks_section(
    size_key: str,
    num_forms_var: rx.Var[int],
    checks_list_var: rx.Var[List[CylinderCheckData]],
    section_title: str,
    cylinder_label_prefix: str,
) -> rx.Component:
    return rx.cond(
        num_forms_var > 0,
        rx.el.section(
            rx.el.h2(
                section_title,
                class_name="text-2xl font-bold text-gray-800 mt-8 mb-6 border-b-2 border-gray-300 pb-3",
            ),
            rx.foreach(
                rx.Var.range(num_forms_var),
                lambda i: cylinder_check_row(
                    size_key,
                    checks_list_var,
                    i,
                    cylinder_label_prefix,
                ),
            ),
        ),
        rx.fragment(),
    )


def handover_entry_page_2() -> rx.Component:
    return main_layout(
        rx.el.div(
            rx.el.h1(
                "Cylinder Handover Entry - Part 2: Cylinder Checks",
                class_name="text-3xl font-bold text-gray-800 mb-4 text-center",
            ),
            rx.el.p(
                f"Please provide details for the cylinders. Displaying check forms for: 2m³ ({CylinderState.num_cylinder_forms_to_show_2m}), 4m³ ({CylinderState.num_cylinder_forms_to_show_4m}), 7m³ ({CylinderState.num_cylinder_forms_to_show_7m}). Max 5 per size.",
                class_name="text-md text-gray-600 mb-8 text-center",
            ),
            rx.el.form(
                rx.cond(
                    CylinderState.total_forms_to_show > 0,
                    rx.el.div(
                        cylinder_checks_section(
                            "2m",
                            CylinderState.num_cylinder_forms_to_show_2m,
                            CylinderState.cylinder_checks_2m,
                            "2 Cubic Meter Cylinders",
                            "2m³",
                        ),
                        cylinder_checks_section(
                            "4m",
                            CylinderState.num_cylinder_forms_to_show_4m,
                            CylinderState.cylinder_checks_4m,
                            "4 Cubic Meter Cylinders",
                            "4m³",
                        ),
                        cylinder_checks_section(
                            "7m",
                            CylinderState.num_cylinder_forms_to_show_7m,
                            CylinderState.cylinder_checks_7m,
                            "7 Cubic Meter Cylinders",
                            "7m³",
                        ),
                    ),
                    rx.el.p(
                        "No cylinder checks required based on the quantities entered on the previous page.",
                        class_name="text-gray-700 text-center py-10 bg-white rounded-lg shadow p-6",
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        "Previous",
                        on_click=CylinderState.go_to_page_1,
                        class_name="mt-8 py-2 px-6 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500",
                    ),
                    rx.el.button(
                        "Submit Handover",
                        on_click=CylinderState.submit_final_form,
                        disabled=CylinderState.total_forms_to_show
                        <= 0,
                        class_name=rx.cond(
                            CylinderState.total_forms_to_show
                            <= 0,
                            "mt-8 py-2 px-6 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-300 cursor-not-allowed",
                            "mt-8 py-2 px-6 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500",
                        ),
                    ),
                    class_name="flex justify-between mt-10",
                ),
                class_name="space-y-8",
            ),
            class_name="max-w-3xl mx-auto pb-12",
        )
    )