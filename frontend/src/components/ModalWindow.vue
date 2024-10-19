<template>
  <div class="image_form">
    <button @click="showModal = true" class="open-modal-button">Загрузка изображения</button>

    <div v-if="showModal" class="modal-overlay">
      <div class="modal">
        <h2>Загрузка изображения</h2>
        <form @submit.prevent="submitForm">
          <div class="modal__form-group">
            <label for="requestName">Создать запрос:</label>
            <input
                type="text"
                v-model="requestName"
                id="requestName"
                class="modal__input"
                placeholder="Введите запрос"
                required
            />
          </div>

          <div class="modal__form-group">
            <label for="file">Загрузить файл:</label>
            <input type="file" @change="handleFileUpload" id="file" class="modal__input" required />
          </div>

          <div class="modal-buttons">
            <button type="submit" class="modal__button modal__button--large">Отправить</button>
            <button type="button" @click="showModal = false" class="modal__button modal__button--cancel">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "ModalView",
  data() {
    return {
      showModal: false,
      requestName: "",
      file: null,
    };
  },
  methods: {
    handleFileUpload(event) {
      this.file = event.target.files[0];
    },
    submitForm() {
      const formData = new FormData();
      formData.append("requestName", this.requestName);
      formData.append("file", this.file);

      axios.post("/upload", formData)
          .then(() => {
            alert("Файл успешно отправлен");
          })
          .catch((error) => {
            console.error("Ошибка:", error);
            alert("Ошибка при отправке файла");
          });

      this.showModal = false;
    },
  },
};
</script>

<style scoped lang="less">
/* Основные стили для списка и заголовков */
h3 {
  margin: 40px 0 0;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}

/* Модальное окно и кнопки */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  width: 100%;
}

.modal__form-group {
  margin-bottom: 15px;
}

.modal__input,
.modal__button {
  width: calc(100% - 20px);
  padding: 10px;
  margin: 5px 10px;
  border-radius: 5px;
  box-sizing: border-box;
}

.modal__input {
  border: 1px solid #ccc;
}

.modal__button {
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;

  &:hover {
    background-color: #0056b3;
  }

  &--large {
    padding: 15px;
  }

  &--cancel {
    background-color: #ccc;
    margin-left: 10px;

    &:hover {
      background-color: #999;
    }
  }
}

.open-modal-button {
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;

  &:hover {
    background-color: #359c74;
  }
}
</style>
