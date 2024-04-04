import hashlib
import re
from logging import getLogger
from os import environ
from secrets import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from nicegui import app, events, ui

from ..loader import ModelLoader

logger = getLogger(__name__)

PASSWORD_SALT = "subscribe_taffy_thanks_meow!"
SALTED_PASSWORD = environ.get("SALTED_PASSWORD", "")


CredentialsDep = Annotated[
    HTTPBasicCredentials | None,
    Depends(HTTPBasic(auto_error=False)),
]


def authorization_middleware(credentials: CredentialsDep):
    if not SALTED_PASSWORD:
        logger.warning(
            "SALTED_PASSWORD not set, you will not be able to access admin page"
        )

    if credentials is not None and (
        compare_digest(credentials.username, "admin")
        and compare_digest(
            hashlib.sha256(
                f"{PASSWORD_SALT}{credentials.password}{PASSWORD_SALT}".encode()
            ).hexdigest(),
            SALTED_PASSWORD,
        )
    ):
        app.storage.browser["is_admin"] = True
    is_admin = app.storage.browser.get("is_admin", False)
    if not is_admin:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    return is_admin


AuthorizationMiddlewareDep = Annotated[
    bool,
    Depends(authorization_middleware),
]


@ui.page("/admin")
def admin_page(is_admin: AuthorizationMiddlewareDep):
    def handle_upload(e: events.UploadEventArguments):
        name = str.strip(model_name_input.value)
        if not name:
            ui.notify("Please input a valid model name", color="negative")
            return
        with open(ModelLoader.pts_path / f"{name}.pt", "wb") as f:
            total = 0
            for chunk in e.content:
                total += f.write(chunk)
        logger.debug(f"New model {name=} uploaded, {total} bytes")
        ui.open(admin_page)

    with ui.dialog() as upload_dialog, ui.card():
        with ui.card_section():
            ui.label("Upload Model").classes("text-h6")

        with ui.card_section(), ui.column().classes("items-stretch"):
            model_name_input = ui.input(
                "Model Name",
                validation={
                    "Please input a valid filename.": lambda value: re.fullmatch(
                        r"^[a-zA-Z0-9_\-]+$", value
                    )
                    is not None
                },
            )
            ui.upload(label="Model File", auto_upload=True, on_upload=handle_upload)
            ui.button("Cancel", on_click=upload_dialog.close).props("flat")

    with ui.row().classes(
        "w-full absolute-center justify-center items-center"
    ), ui.card().classes("col-12 col-md-10 col-xl-8"):
        with ui.card_section(), ui.row():
            ui.label("Welcome, Admin!").classes("text-h5")

        with ui.card_section(), ui.column().classes("items-stretch"):
            for index, (model_name, _) in enumerate(
                ModelLoader.available_pts().items()
            ):
                splitter = ui.splitter(horizontal=True)
                with splitter.before, ui.row().classes(
                    "items-center justify-between q-mb-md"
                ):
                    ui.label(f"{index+1}. Model:").classes("text-body1")
                    ui.label(model_name).classes("text-body2 font-mono")
                    ui.button(
                        "Delete",
                        icon="delete",
                        color="negative",
                        on_click=lambda e: (
                            ModelLoader.delete_model(model_name),  # noqa: B023
                            ui.open(admin_page),
                        ),
                    ).props("flat")

        with ui.card_actions():
            ui.button("Upload Model", icon="upload", on_click=upload_dialog.open)
            ui.button("Refresh", icon="refresh", on_click=lambda e: ui.open(admin_page))
