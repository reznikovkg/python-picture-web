import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.optimizers import Adamax
from tensorflow.keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array

from PIL import Image
import numpy as np
import scipy
from typing import List, Tuple
import io

from image_classifier.common.base import ImageClassifierBySkinLesion, SkinLesion


class DefaultImageClassifierBySkinLesion(ImageClassifierBySkinLesion):

    def __init__(self, model_paths: List[str], img_size: Tuple[int, int] = (224, 224), learning_rate: float = 0.001):
        self.__setup_gpu()
        self.model_paths = model_paths
        self.img_size = img_size
        self.learning_rate = learning_rate
        self.models = self.__load_and_compile_models()

    def __setup_gpu(self) -> None:
        tf.get_logger().setLevel('ERROR')
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
            except RuntimeError as e:
                print(e)

    def __load_and_compile_models(self) -> List[Model]:
        models = []
        for path in self.model_paths:
            model = self.__compile_model(path)
            models.append(model)
        return models

    def __compile_model(self, model_path: str) -> Model:
        model = load_model(model_path)
        model.compile(optimizer=Adamax(learning_rate=self.learning_rate),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def apply(self, image_data: bytes) -> Tuple[dict, List[SkinLesion], SkinLesion]:

        image = Image.open(io.BytesIO(image_data))
        image = image.resize(self.img_size)
        image_array = img_to_array(image)
        image_array = np.expand_dims(image_array, axis=0)

        params = {
            'optimizer': 'Adamax',
            'learning_rate': self.learning_rate,
            'loss': 'categorical_crossentropy',
            'metrics': 'accuracy'
        }

        tvgen = ImageDataGenerator(preprocessing_function=lambda x: x)
        predict_gen = tvgen.flow(image_array, batch_size=1, shuffle=False)

        print('\nПрогнозирование')
        predictions = [model.predict(predict_gen)[0] for model in self.models]
        individual_lesions = [SkinLesion.value_of(pred) for pred in predictions]

        ensemble_prediction = self.__ensemble_predictions(predictions)
        ensemble_lesion = SkinLesion.value_of(ensemble_prediction)

        return params, individual_lesions, ensemble_lesion

    def __ensemble_predictions(self, predictions_list: List[np.ndarray]) -> np.ndarray:
        pr_sum = np.sum(np.array(predictions_list), axis=0)
        return pr_sum
