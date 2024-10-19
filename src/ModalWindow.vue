<template>
  <div>
    <button @click="showModal = true">Открыть модальное окно</button>

    <div v-if="showModal" class="modal-overlay">
      <div class="modal">
        <h2>Загрузить файл</h2>
        <form @submit.prevent="submitForm">
          <div>
            <label for="requestName">Название запроса:</label>
            <input
                type="text"
                v-model="requestName"
                id="requestName"
                placeholder="Введите название"
                required
            />
          </div>

          <div>
            <label for="file">Загрузить файл:</label>
            <input type="file" @change="handleFileUpload" id="file" required />
          </div>

          <div class="modal-buttons">
            <button type="submit">Отправить</button>
            <button type="button" @click="showModal = false">Отмена</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
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

      fetch("/upload", {
        method: "POST",
        body: formData,
      })
          .then((response) => {
            if (response.ok) {
              alert("Файл успешно отправлен");
            } else {
              alert("Ошибка при отправке файла");
            }
          })
          .catch((error) => {
            console.error("Ошибка:", error);
          });

      this.showModal = false;
    },
  },
};
</script>

<style scoped>
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
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.modal-buttons {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
}

button {
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}

button:hover {
  background-color: #359c74;
}
</style>
