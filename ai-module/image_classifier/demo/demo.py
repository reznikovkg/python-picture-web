import logging
import os
from pathlib import Path

from PIL import Image
import io

from image_classifier.main.run import Initializer, MainImageClassifierBySkinLesion


def image_to_bytes(image_path: str) -> bytes:
    with Image.open(image_path) as image:
        byte_array = io.BytesIO()
        image.save(byte_array, format='PNG')
        return byte_array.getvalue()


if __name__ == '__main__':

    image_path = '../../predict/ISIC_0000146_downsampled.jpg'
    image_data = image_to_bytes(image_path)

    log_file_path = "../../logs/log.log"
    logging.basicConfig(format='%(asctime)s [%(name)s] [%(levelname)s]: %(message)s',
                        datefmt="%d-%m-%y %H:%M:%S",
                        level=logging.INFO,
                        handlers=[logging.FileHandler(filename=log_file_path, encoding='utf-8'),
                                  logging.StreamHandler()])

    env_path = os.path.join(Path(__file__).resolve().parent.parent.parent, ".env.dev")

    Initializer().apply(env_path)
    MainImageClassifierBySkinLesion().prepare()
    result = MainImageClassifierBySkinLesion().apply(image_data)
    print(result)
