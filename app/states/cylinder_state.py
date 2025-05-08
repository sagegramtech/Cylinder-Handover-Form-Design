import reflex as rx
from typing import TypedDict, List
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from app.states.auth_state import MONGO_URI_TEMPLATE
import datetime


class CylinderCheckData(TypedDict):
    cylinder_id: str | None
    purity: float | None
    pressure: int | None


class HandoverEntry(TypedDict):
    _id: str
    facility: str
    bmt_in_charge: str
    receiving_personnel: str | None
    qty_2m: int
    qty_4m: int
    qty_7m: int
    cylinder_checks_2m: list[CylinderCheckData]
    cylinder_checks_4m: list[CylinderCheckData]
    cylinder_checks_7m: list[CylinderCheckData]
    submitted_by: str
    submission_timestamp: str


class CylinderState(rx.State):
    facilities: list[str] = [
        "Ajeromi General Hospital",
        "Harvey Road General Hospital",
        "Massey Children Hospital",
        "God's Hope",
    ]
    selected_facility: str = ""
    receiving_personnel: str = ""
    qty_2m: int = 0
    qty_4m: int = 0
    qty_7m: int = 0
    cylinder_checks_2m: list[CylinderCheckData] = []
    cylinder_checks_4m: list[CylinderCheckData] = []
    cylinder_checks_7m: list[CylinderCheckData] = []
    current_form_page: int = 1
    all_submissions: list[HandoverEntry] = []
    is_loading_submissions: bool = False
    _DB_NAME = "Cylinder_Inventory"
    _COLLECTION_NAME = "Handover_records"
    show_delete_confirm_dialog: bool = False
    submission_to_delete_id: str | None = None

    @rx.var
    async def bmt_in_charge_display(self) -> str:
        from app.states.auth_state import AuthState

        auth_s = await self.get_state(AuthState)
        if (
            auth_s.is_authenticated
            and auth_s.authenticated_username
        ):
            return f"Mr. {auth_s.authenticated_username}"
        return "N/A"

    @rx.var
    def num_cylinder_forms_to_show_2m(self) -> int:
        return min(self.qty_2m, 5)

    @rx.var
    def num_cylinder_forms_to_show_4m(self) -> int:
        return min(self.qty_4m, 5)

    @rx.var
    def num_cylinder_forms_to_show_7m(self) -> int:
        return min(self.qty_7m, 5)

    @rx.var
    def total_forms_to_show(self) -> int:
        return (
            self.num_cylinder_forms_to_show_2m
            + self.num_cylinder_forms_to_show_4m
            + self.num_cylinder_forms_to_show_7m
        )

    def _plain_python_checks_list(
        self, checks_list_proxy: list[CylinderCheckData]
    ) -> list[CylinderCheckData]:
        return [dict(item) for item in checks_list_proxy]

    def _adjust_cylinder_checks_list(
        self,
        current_checks_list: list[CylinderCheckData],
        num_forms_needed: int,
    ) -> list[CylinderCheckData]:
        plain_list = self._plain_python_checks_list(
            current_checks_list
        )
        if len(plain_list) > num_forms_needed:
            return plain_list[:num_forms_needed]
        elif len(plain_list) < num_forms_needed:
            plain_list.extend(
                [
                    {
                        "cylinder_id": None,
                        "purity": None,
                        "pressure": None,
                    }
                    for _ in range(
                        num_forms_needed - len(plain_list)
                    )
                ]
            )
        return plain_list

    @rx.event
    def handle_page_1_submit(self, form_data: dict):
        self.receiving_personnel = form_data.get(
            "receiving_personnel", ""
        )
        raw_qty_2m = form_data.get("qty_2m", "")
        self.qty_2m = (
            int(raw_qty_2m) if raw_qty_2m.isdigit() else 0
        )
        raw_qty_4m = form_data.get("qty_4m", "")
        self.qty_4m = (
            int(raw_qty_4m) if raw_qty_4m.isdigit() else 0
        )
        raw_qty_7m = form_data.get("qty_7m", "")
        self.qty_7m = (
            int(raw_qty_7m) if raw_qty_7m.isdigit() else 0
        )
        if not self.selected_facility:
            yield rx.toast.error("Facility is required.")
            return
        if (
            self.qty_2m < 0
            or self.qty_4m < 0
            or self.qty_7m < 0
        ):
            yield rx.toast.error(
                "Cylinder quantities cannot be negative."
            )
            return
        if (
            self.qty_2m == 0
            and self.qty_4m == 0
            and (self.qty_7m == 0)
        ):
            yield rx.toast.error(
                "At least one cylinder quantity must be greater than 0."
            )
            return
        self.cylinder_checks_2m = (
            self._adjust_cylinder_checks_list(
                self.cylinder_checks_2m,
                self.num_cylinder_forms_to_show_2m,
            )
        )
        self.cylinder_checks_4m = (
            self._adjust_cylinder_checks_list(
                self.cylinder_checks_4m,
                self.num_cylinder_forms_to_show_4m,
            )
        )
        self.cylinder_checks_7m = (
            self._adjust_cylinder_checks_list(
                self.cylinder_checks_7m,
                self.num_cylinder_forms_to_show_7m,
            )
        )
        self.current_form_page = 2
        yield rx.redirect("/handover_entry_p2")

    @rx.event
    def go_to_page_1(self):
        self.current_form_page = 1
        return rx.redirect("/handover_entry_p1")

    @rx.event
    def update_cylinder_check_field(
        self,
        size_key: str,
        index: int,
        field_name: str,
        value: str,
    ):
        target_list_proxy: (
            list[CylinderCheckData] | None
        ) = None
        if size_key == "2m":
            target_list_proxy = self.cylinder_checks_2m
        elif size_key == "4m":
            target_list_proxy = self.cylinder_checks_4m
        elif size_key == "7m":
            target_list_proxy = self.cylinder_checks_7m
        if target_list_proxy is None:
            yield rx.toast.error(
                f"Invalid cylinder size key: {size_key}"
            )
            return
        if not 0 <= index < len(target_list_proxy):
            yield rx.toast.error(
                f"Error accessing cylinder data for {size_key} cylinder {index + 1}. List index out of bounds."
            )
            return
        try:
            if field_name == "purity":
                target_list_proxy[index]["purity"] = (
                    float(value) if value else None
                )
            elif field_name == "pressure":
                target_list_proxy[index]["pressure"] = (
                    int(value) if value else None
                )
            elif field_name == "cylinder_id":
                target_list_proxy[index]["cylinder_id"] = (
                    value if value else None
                )
        except ValueError:
            yield rx.toast.error(
                f"Invalid input for {field_name} at {size_key} cylinder {index + 1}"
            )
        except (TypeError, IndexError):
            yield rx.toast.error(
                f"Error accessing cylinder data for {size_key} cylinder {index + 1}. Please re-enter quantities or refresh."
            )

    async def _get_db_client(self) -> MongoClient | None:
        from app.states.auth_state import AuthState

        auth_s = await self.get_state(AuthState)
        username = auth_s.authenticated_username
        password = (
            auth_s._authenticated_password_DO_NOT_EXPOSE
        )
        if not username or not password:
            return None
        uri = MONGO_URI_TEMPLATE.format(
            db_username=username, db_password=password
        )
        try:
            client = MongoClient(
                uri, serverSelectionTimeoutMS=5000
            )
            client.admin.command("ping")
            return client
        except (
            errors.ConnectionFailure,
            errors.OperationFailure,
        ):
            return None

    async def _get_cylinder_check_validation_errors(
        self,
        checks_list: list[CylinderCheckData],
        size_label: str,
    ) -> list[str]:
        error_messages: list[str] = []
        for i, check in enumerate(checks_list):
            if check["purity"] is None:
                error_messages.append(
                    f"Purity is required for {size_label} cylinder {i + 1}."
                )
            elif not 0 <= check["purity"] <= 99:
                error_messages.append(
                    f"Purity for {size_label} cylinder {i + 1} must be between 0 and 99."
                )
            if check["pressure"] is None:
                error_messages.append(
                    f"Pressure is required for {size_label} cylinder {i + 1}."
                )
            elif not 0 <= check["pressure"] <= 2000:
                error_messages.append(
                    f"Pressure for {size_label} cylinder {i + 1} must be between 0 and 2000."
                )
        return error_messages

    @rx.event
    async def submit_final_form(self):
        all_validation_errors: list[str] = []
        plain_checks_2m = self._plain_python_checks_list(
            self.cylinder_checks_2m
        )
        plain_checks_4m = self._plain_python_checks_list(
            self.cylinder_checks_4m
        )
        plain_checks_7m = self._plain_python_checks_list(
            self.cylinder_checks_7m
        )
        errors_2m = await self._get_cylinder_check_validation_errors(
            plain_checks_2m, "2m³"
        )
        all_validation_errors.extend(errors_2m)
        errors_4m = await self._get_cylinder_check_validation_errors(
            plain_checks_4m, "4m³"
        )
        all_validation_errors.extend(errors_4m)
        errors_7m = await self._get_cylinder_check_validation_errors(
            plain_checks_7m, "7m³"
        )
        all_validation_errors.extend(errors_7m)
        if all_validation_errors:
            for error_msg in all_validation_errors:
                yield rx.toast.error(error_msg)
            return
        client = await self._get_db_client()
        if client is None:
            yield rx.toast.error(
                "Database connection error. Please sign in again."
            )
            from app.states.auth_state import AuthState

            auth_s_check = await self.get_state(AuthState)
            if auth_s_check.is_authenticated:
                yield auth_s_check.sign_out()
            return
        try:
            db = client[self._DB_NAME]
            collection = db[self._COLLECTION_NAME]
            from app.states.auth_state import AuthState

            auth_s_submit = await self.get_state(AuthState)
            current_bmt_in_charge = (
                await self.bmt_in_charge_display
            )
            entry_data_to_insert = {
                "facility": self.selected_facility,
                "bmt_in_charge": current_bmt_in_charge,
                "receiving_personnel": (
                    self.receiving_personnel
                    if self.receiving_personnel
                    else None
                ),
                "qty_2m": self.qty_2m,
                "qty_4m": self.qty_4m,
                "qty_7m": self.qty_7m,
                "cylinder_checks_2m": plain_checks_2m,
                "cylinder_checks_4m": plain_checks_4m,
                "cylinder_checks_7m": plain_checks_7m,
                "submitted_by": auth_s_submit.authenticated_username
                or "Unknown",
                "submission_timestamp": datetime.datetime.utcnow().isoformat(),
            }
            collection.insert_one(entry_data_to_insert)
            yield rx.toast.success(
                "Handover entry submitted successfully!"
            )
            self._reset_form_state()
            yield rx.redirect("/handover_entry_p1")
        except errors.OperationFailure as e:
            yield rx.toast.error(
                f"Database operation failed: {str(e)}"
            )
        except Exception as e:
            yield rx.toast.error(
                f"Failed to submit form: {str(e)}"
            )
        finally:
            if client:
                client.close()

    def _reset_form_state(self):
        self.selected_facility = ""
        self.receiving_personnel = ""
        self.qty_2m = 0
        self.qty_4m = 0
        self.qty_7m = 0
        self.cylinder_checks_2m = []
        self.cylinder_checks_4m = []
        self.cylinder_checks_7m = []
        self.current_form_page = 1
        self.submission_to_delete_id = None
        self.show_delete_confirm_dialog = False

    @rx.event
    async def fetch_db_submissions(self):
        self.is_loading_submissions = True
        self.all_submissions = []
        yield
        client = await self._get_db_client()
        if client is None:
            self.is_loading_submissions = False
            yield rx.toast.error(
                "Database connection not available for fetching. Please sign in again."
            )
            from app.states.auth_state import AuthState

            auth_s = await self.get_state(AuthState)
            if auth_s.is_authenticated:
                yield auth_s.sign_out()
            return
        try:
            db = client[self._DB_NAME]
            collection = db[self._COLLECTION_NAME]
            submissions_cursor = collection.find({}).sort(
                "submission_timestamp", -1
            )
            submissions_list: list[HandoverEntry] = []
            for sub_doc in submissions_cursor:
                entry: HandoverEntry = {
                    "_id": str(sub_doc["_id"]),
                    "facility": sub_doc.get("facility", ""),
                    "bmt_in_charge": sub_doc.get(
                        "bmt_in_charge", ""
                    ),
                    "receiving_personnel": sub_doc.get(
                        "receiving_personnel"
                    ),
                    "qty_2m": sub_doc.get("qty_2m", 0),
                    "qty_4m": sub_doc.get("qty_4m", 0),
                    "qty_7m": sub_doc.get("qty_7m", 0),
                    "cylinder_checks_2m": sub_doc.get(
                        "cylinder_checks_2m", []
                    ),
                    "cylinder_checks_4m": sub_doc.get(
                        "cylinder_checks_4m", []
                    ),
                    "cylinder_checks_7m": sub_doc.get(
                        "cylinder_checks_7m", []
                    ),
                    "submitted_by": sub_doc.get(
                        "submitted_by", "Unknown"
                    ),
                    "submission_timestamp": sub_doc.get(
                        "submission_timestamp", ""
                    ),
                }
                submissions_list.append(entry)
            self.all_submissions = submissions_list
            self.is_loading_submissions = False
            yield
            if not submissions_list:
                yield rx.toast.info(
                    "No submissions found in the database."
                )
            else:
                yield rx.toast.success(
                    f"Fetched {len(submissions_list)} submissions."
                )
        except Exception as e:
            self.all_submissions = []
            self.is_loading_submissions = False
            yield rx.toast.error(
                f"Error fetching submissions: {str(e)}"
            )
        finally:
            if client:
                client.close()

    @rx.event
    def clear_form_and_reset_to_p1(self):
        self._reset_form_state()
        return rx.redirect("/handover_entry_p1")

    @rx.event
    def prepare_delete_submission(self, submission_id: str):
        self.submission_to_delete_id = submission_id
        self.show_delete_confirm_dialog = True

    @rx.event
    def cancel_delete_submission(self):
        self.submission_to_delete_id = None
        self.show_delete_confirm_dialog = False

    @rx.event
    async def confirm_delete_submission(self):
        if self.submission_to_delete_id is None:
            yield rx.toast.error(
                "No submission selected for deletion."
            )
            self.show_delete_confirm_dialog = False
            return
        client = await self._get_db_client()
        if client is None:
            yield rx.toast.error(
                "Database connection error. Cannot delete."
            )
            self.show_delete_confirm_dialog = False
            self.submission_to_delete_id = None
            from app.states.auth_state import AuthState

            auth_s = await self.get_state(AuthState)
            if auth_s.is_authenticated:
                yield auth_s.sign_out()
            return
        try:
            db = client[self._DB_NAME]
            collection = db[self._COLLECTION_NAME]
            object_id_to_delete = ObjectId(
                self.submission_to_delete_id
            )
            delete_result = collection.delete_one(
                {"_id": object_id_to_delete}
            )
            if delete_result.deleted_count == 1:
                yield rx.toast.success(
                    "Submission deleted successfully."
                )
                yield CylinderState.fetch_db_submissions
            else:
                yield rx.toast.warning(
                    "Submission not found or already deleted."
                )
        except errors.PyMongoError as e:
            yield rx.toast.error(
                f"Database error during deletion: {str(e)}"
            )
        except Exception as e:
            yield rx.toast.error(
                f"An unexpected error occurred during deletion: {str(e)}"
            )
        finally:
            if client:
                client.close()
            self.show_delete_confirm_dialog = False
            self.submission_to_delete_id = None