from logging import getLogger
from mimetypes import guess_extension
from tempfile import mktemp

from nicegui import events, ui
from PIL import Image

from ..loader import ModelLoader
from .static import STATIC_PATH

logger = getLogger(__name__)


@ui.page("/")
def index_page():
    available_models = [*ModelLoader.available_pts().keys()]

    image_file_path: str | None = None

    def handle_upload(e: events.UploadEventArguments):
        if not e.type.startswith("image/") or (ext := guess_extension(e.type)) is None:
            ui.notify("Please upload an image with valid MIME type", color="negative")
            return

        with open(file_path := mktemp(suffix=ext), "wb") as f:
            total = 0
            for chunk in e.content:
                total += f.write(chunk)

        logger.debug(f"Uploaded file to {file_path} ({total} bytes)")
        nonlocal image_file_path
        image_file_path = file_path

    def predict(e: events.ClickEventArguments):
        if image_file_path is None:
            ui.notify("Please upload an image first", color="negative")
            return

        logger.debug(f"Predicting image {image_file_path} ...")
        upload_button.disable()
        spinner.set_visibility(True)

        image = Image.open(image_file_path)

        if ModelLoader.current_active is None:
            ui.notify("Please select a model first", color="negative")
            return

        result = ModelLoader.predict(image, prob_threshold.value)
        tag_chart.options["series"] = [
            {"name": tag, "data": [prob * 100]} for tag, prob in result.items()
        ]
        tag_chart.update()

        upload_button.enable()
        spinner.set_visibility(False)

    def update_model(e: events.ValueChangeEventArguments):
        logger.info(f"Loading model {e.value!r} ...")
        model_selector.disable()
        spinner.set_visibility(True)
        try:
            ModelLoader(e.value).load()
        except Exception as err:
            ui.notify(f"Failed to load model {e.value!r}: {err}", color="negative")
            logger.exception(err)
        spinner.set_visibility(False)
        model_selector.enable()

    with ui.carousel(animated=True, navigation=True).props("autoplay").classes(
        "z-0 fullscreen"
    ):
        for image in STATIC_PATH.glob("background*"):
            with ui.carousel_slide().classes("p-0"):
                ui.image(f"/static/{image.name}").classes("h-full").props("fit=cover")

    with ui.row().classes(
        "justify-center items-center w-full absolute-center z-10"
    ), ui.card().classes("col-12 col-md-10 col-xl-8 bg-white/70 backdrop-blur-sm"):
        with ui.card_section(), ui.row():
            ui.label("Welcome to VulnTagger!").classes("text-h4")
            spinner = ui.spinner(size="lg")
            spinner.set_visibility(False)

        with ui.card_section(), ui.row():
            with ui.column().classes("col-6 items-stretch justify-center"):
                model_selector = ui.select(
                    available_models,
                    label="Available checkpoints",
                    value=ModelLoader.current_active.name
                    if ModelLoader.current_active
                    else None,
                    on_change=update_model,
                )
                ui.upload(
                    label="Upload image", on_upload=handle_upload, auto_upload=True
                )
                with ui.row():
                    ui.label("Probability threshold")
                    prob_threshold = ui.slider(min=0, max=1, value=0.5, step=0.001)
                upload_button = ui.button(
                    "Predict Now", icon="play_circle_filled", on_click=predict
                ).props("outline rounded")

            with ui.card_section().classes("col-6"):
                tag_chart = ui.highchart(
                    {
                        "title": "Tag Probabilities",
                        "chart": {
                            "type": "packedbubble",
                            "backgroundColor": None,
                        },
                        "tooltip": {
                            "useHTML": True,
                            "pointFormat": "{point.value:.3f}%",
                        },
                        "plotOptions": {
                            "packedbubble": {
                                "minSize": "20%",
                                "maxSize": "100%",
                                "zMin": 0,
                                "zMax": 100,
                                "layoutAlgorithm": {
                                    "splitSeries": False,
                                    "gravitationalConstant": 0.02,
                                },
                            },
                        },
                        "series": [],
                    }
                )
