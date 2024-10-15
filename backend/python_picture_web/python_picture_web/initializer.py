import logging

logger = logging.getLogger(__name__)


class Initializer:
    def execute(self):
        module_name = "python_picture_web.settings"
        try:
            from image_classifier.main.run import MainImageClassifierBySkinLesion
            MainImageClassifierBySkinLesion().prepare()
        except Exception as exc:
            logger.error(f"[{self.__class__.__name__}] -> execute error, exception: {exc}")
        logger.info(f"[{self.__class__.__name__}] -> execute with {module_name=}")
