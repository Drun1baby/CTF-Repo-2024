import time
from collections.abc import Callable
from logging import getLogger
from pathlib import Path
from typing import ClassVar, Self

import numpy
import torch
from PIL.Image import Image

from .model import DeepDanbooruModel

logger = getLogger(__name__)


class ModelLoader:
    current_active: ClassVar[Self | None] = None
    pts_path = Path("./checkpoints").absolute()

    compiled_model: Callable[[torch.Tensor], torch.Tensor] | None = None

    @classmethod
    def available_pts(cls):
        return {path.stem: path for path in cls.pts_path.glob("*.pt")}

    @classmethod
    def delete_model(cls, name: str):
        if cls.current_active is not None and cls.current_active.name == name:
            cls.current_active = None
        if (path := ModelLoader.available_pts().get(name)) is None:
            raise ValueError(f"Model {name} not found")
        path.unlink()

    def __init__(self, name: str):
        self.name = name
        self.checkpoint_path = self.available_pts()[name]
        self.tags: list[str] = []

    def load(self):
        logger.debug(f"Loading model from {self.checkpoint_path} ...")
        weights = torch.load(self.checkpoint_path)

        model = DeepDanbooruModel()
        model.load_state_dict(weights)
        model.eval()

        type(self).current_active = self
        self.tags = model.tags

        logger.debug("Model loaded, test predicting ...")
        test_tensor = torch.rand(1, 512, 512, 3)
        self.compiled_model = torch.jit.script(model, example_inputs=[(test_tensor,)])  # type: ignore
        self._predict(test_tensor)
        logger.debug("Model test passed")

    def _predict(self, x: torch.Tensor):
        assert x.shape == (1, 512, 512, 3), "Input shape must be (1, 512, 512, 3)"
        assert self.compiled_model is not None, "Model not loaded yet"

        logger.debug("Predicting input image ...")
        start_time = time.time()
        try:
            predicted = self.compiled_model(x)
        except Exception as e:
            logger.exception(e)
            raise e
        time_delta = (time.time() - start_time) * 1000
        logger.debug(f"Predicted result in {time_delta:.2f}ms")
        return predicted

    @classmethod
    def predict(cls, image: Image, prob_threshold: float = 0.5):
        assert (loaded := cls.current_active) is not None, "Model not loaded yet"

        image = image.convert("RGB").resize((512, 512))
        tensor = torch.from_numpy(
            numpy.expand_dims(
                numpy.array(image, dtype=numpy.float32),
                0,
            )
            / 255
        )

        with torch.no_grad():
            result, *_ = loaded._predict(tensor)
            tag_prob = result.detach().numpy()
        return {
            tag: float(prob)
            for tag, prob in zip(loaded.tags, tag_prob, strict=False)
            if prob >= prob_threshold
        }
