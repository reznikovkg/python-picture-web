import logging
import os
import time
from typing import List, Tuple

from dotenv import load_dotenv

from image_classifier.common.base import ImageClassifierBySkinLesion, Applier, SkinLesion
from image_classifier.main.classify import DefaultImageClassifierBySkinLesion

logger = logging.getLogger(__name__)


class Initializer(Applier):

    def apply(self, env_file_path_in: str) -> None:
        if os.path.exists(env_file_path_in):
            load_dotenv(env_file_path_in)


class MainImageClassifierBySkinLesion(ImageClassifierBySkinLesion):
    __classifier = None

    @classmethod
    def prepare(cls):
        model1_path = os.environ.get("MODEL1_DIR", None)
        model2_path = os.environ.get("MODEL2_DIR", None)
        model3_path = os.environ.get("MODEL3_DIR", None)

        if not model1_path or not model2_path or not model3_path:
            raise ValueError("One or more model paths are not defined in environment variables.")

        if not (os.path.exists(model1_path) and os.path.exists(model2_path) and os.path.exists(model3_path)):
            raise FileNotFoundError("One or more model files do not exist at specified paths.")

        model_paths = [model1_path, model2_path, model3_path]
        cls.__classifier = DefaultImageClassifierBySkinLesion(model_paths=model_paths)

    def apply(self, image_data: bytes) -> Tuple[dict, List[SkinLesion], SkinLesion]:
        logger.info(f"[{self.__class__.__name__}] -> apply start:")
        start_time = time.time()

        if self.__classifier is None:
            self.prepare()

        params, individual_lesions, ensemble_lesion = self.__classifier.apply(image_data)

        finish_time = time.time() - start_time
        logger.info(f"[{self.__class__.__name__}] -> apply finished with {finish_time} sec")

        return params, individual_lesions, ensemble_lesion
