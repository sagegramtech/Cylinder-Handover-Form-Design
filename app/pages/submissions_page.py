import reflex as rx
from app.states.cylinder_state import (
    CylinderState,
    HandoverEntry,
    CylinderCheckData,
)
from app.components.navbar import main_layout
from typing import List


def display_cylinder_checks_for_size(
    checks_list: rx.Var[List[CylinderCheckData]],
    size_label: str,
) -> rx.Component:
    return rx.cond(
        checks_list.length() > 0,
        rx.el.div(
            rx.el.h5(
                f"{size_label} Cylinders:",
                class_name="text-sm font-semibold text-gray-700 mt-2 mb-1",
            ),
            rx.foreach(
                checks_list,
                lambda check, idx: rx.el.div(
                    rx.el.p(
                        f"Cylinder {idx + 1}: ID: {rx.cond(check['cylinder_id'], check['cylinder_id'], 'N/A')}, Purity: {check['purity']}%, Pressure: {check['pressure']} psi",
                        class_name="text-xs text-gray-600",
                    ),
                    class_name="ml-4 mb-1",
                ),
            ),
        ),
        rx.fragment(),
    )


def submission_card(
    submission: HandoverEntry, index: int
) -> rx.Component:
    return rx.el.details(
        rx.el.summary(
            rx.el.h3(
                f"Submission #{index + 1} - Facility: {submission['facility']}",
                class_name="text-lg font-semibold text-indigo-700 cursor-pointer",
            )
        ),
        rx.el.div(
            rx.el.p(
                f"BMT In Charge: {submission['bmt_in_charge']}",
                class_name="text-sm text-gray-600 mt-2",
            ),
            rx.el.p(
                f"Receiving Personnel: {rx.cond(submission['receiving_personnel'], submission['receiving_personnel'], 'N/A')}",
                class_name="text-sm text-gray-600",
            ),
            rx.el.p(
                f"Submitted By: {submission['submitted_by']} at {submission['submission_timestamp']}",
                class_name="text-xs text-gray-500 mt-1",
            ),
            rx.el.div(
                rx.el.h4(
                    "Quantities:",
                    class_name="text-md font-medium text-gray-700 mt-3 mb-1",
                ),
                rx.el.ul(
                    rx.el.li(
                        f"2m³: {submission['qty_2m']}"
                    ),
                    rx.el.li(
                        f"4m³: {submission['qty_4m']}"
                    ),
                    rx.el.li(
                        f"7m³: {submission['qty_7m']}"
                    ),
                    class_name="list-disc list-inside text-sm text-gray-600",
                ),
                class_name="mt-2",
            ),
            rx.cond(
                (
                    rx.Var(
                        submission["cylinder_checks_2m"]
                    ).length()
                    > 0
                )
                | (
                    rx.Var(
                        submission["cylinder_checks_4m"]
                    ).length()
                    > 0
                )
                | (
                    rx.Var(
                        submission["cylinder_checks_7m"]
                    ).length()
                    > 0
                ),
                rx.el.div(
                    rx.el.h4(
                        "Cylinder Checks:",
                        class_name="text-md font-medium text-gray-700 mt-3 mb-1",
                    ),
                    display_cylinder_checks_for_size(
                        rx.Var(
                            submission["cylinder_checks_2m"]
                        ),
                        "2m³",
                    ),
                    display_cylinder_checks_for_size(
                        rx.Var(
                            submission["cylinder_checks_4m"]
                        ),
                        "4m³",
                    ),
                    display_cylinder_checks_for_size(
                        rx.Var(
                            submission["cylinder_checks_7m"]
                        ),
                        "7m³",
                    ),
                    class_name="mt-2",
                ),
                rx.fragment(),
            ),
            rx.el.button(
                "Delete",
                on_click=lambda: CylinderState.prepare_delete_submission(
                    submission["_id"]
                ),
                class_name="mt-4 px-3 py-1.5 text-xs font-medium text-white bg-red-600 rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500",
            ),
            class_name="pt-2 pb-4 px-4",
        ),
        class_name="bg-white p-4 rounded-lg shadow border mb-6",
    )


def submissions_page() -> rx.Component:
    return main_layout(
        rx.el.div(
            rx.el.h1(
                "Submitted Handover Entries",
                class_name="text-3xl font-bold text-gray-800 mb-8",
            ),
            rx.cond(
                CylinderState.is_loading_submissions,
                rx.el.div(
                    rx.icon(
                        tag="loader",
                        class_name="animate-spin h-10 w-10 text-indigo-600",
                    ),
                    class_name="flex justify-center py-10",
                ),
                rx.cond(
                    CylinderState.all_submissions.length()
                    > 0,
                    rx.el.div(
                        rx.foreach(
                            CylinderState.all_submissions,
                            lambda sub, idx: submission_card(
                                sub, idx
                            ),
                        )
                    ),
                    rx.el.p(
                        "No submissions found.",
                        class_name="text-gray-600 text-center py-10",
                    ),
                ),
            ),
            rx.el.dialog(
                rx.el.h3(
                    "Confirm Deletion",
                    class_name="text-lg font-bold text-gray-800 mb-2",
                ),
                rx.el.p(
                    "Are you sure you want to delete this submission? This action cannot be undone.",
                    class_name="text-sm text-gray-600 mb-4",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=CylinderState.cancel_delete_submission,
                        class_name="mr-2 px-4 py-2 text-sm font-medium bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500",
                    ),
                    rx.el.button(
                        "Confirm Delete",
                        on_click=CylinderState.confirm_delete_submission,
                        class_name="px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500",
                    ),
                    class_name="mt-4 flex justify-end",
                ),
                open=CylinderState.show_delete_confirm_dialog,
                class_name="p-6 bg-white rounded-lg shadow-xl border border-gray-200 max-w-md mx-auto z-50 fixed inset-x-0 top-1/4",
            ),
            class_name="max-w-4xl mx-auto",
        )
    )