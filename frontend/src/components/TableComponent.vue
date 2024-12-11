<template>
  <div class="animated_container" v-loading="loading">
    <div class="animated_container__table-container">
      <div class="table-container__controls">
        <ElButton type="primary" @click="() => openDownloadModal()">Добавить</ElButton>
        <ElButton type="danger" @click="() => deleteAll()">Удалить все</ElButton>
        <ElButton type="danger" @click="() => logout()">Выход</ElButton>
        <!--        <ElUpload-->
        <!--            ref="upload"-->
        <!--            class="upload-demo"-->
        <!--            action=""-->
        <!--            :on-change="(file) => handleImageChange(file)"-->
        <!--            :auto-upload="false"-->
        <!--            :show-file-list="false">-->
        <!--        </ElUpload>-->
        <ElDialog
            :visible.sync="isDownloadModalVisible"
            title="Добавить данные"
            width="40%"
            @close="closeDownloadModal"
            class="table-container__controls-window--download">
          <p>Загруженные файлы: {{ uploadedFiles }}</p>
          <ElForm>
            <ElFormItem label="Пациент">
              <ElInput v-model="formData.patient" placeholder="Введите фио пациента"></ElInput>
            </ElFormItem>
            <ElFormItem label="Описание">
              <ElInput v-model="formData.description" type="textarea" placeholder="Введите описание"></ElInput>
            </ElFormItem>
            <ElFormItem label="Загрузка изображения">
              <vue-dropzone
                  ref="myDropzone"
                  id="dropzone"
                  :options="dropzoneOptions"
                  @vdropzone-file-added="handleFileAdded"
                  class="dropzone"
              ></vue-dropzone>
            </ElFormItem>
          </ElForm>
          <span slot="footer" class="dialog-footer">
          <ElButton @click="closeDownloadModal">Отмена</ElButton>
          <ElButton type="primary" @click="handleSubmit">Сохранить</ElButton>
        </span>
        </ElDialog>
      </div>

      <ElTable class="table-container__table" :data="paginatedData" @row-click="(row) => openModal(row)">
        <ElTableColumn label="Пациент" :formatter="(row) => formatModelsAndResult(row)"/>
        <ElTableColumn label="Изображение" prop="image"/>
        <ElTableColumn label="Дата и время загрузки" prop="date"/>
        <ElTableColumn label="Модель 1 / Модель 2 / Модель 3 (Ансамбль)"
                       :formatter="(row) => formatModelsAndResult(row)"/>
        <ElTableColumn label="Действия">
          <template #default="{ $index }">
            <ElButton
                type="danger"
                size="mini"
                @click.stop="() => deleteItem($index)">
              Удалить
            </ElButton>
          </template>
        </ElTableColumn>
        <template #empty>
          <p>Нет данных для отображения. Таблица пустая.</p>
        </template>
      </ElTable>

      <ElDialog
          :visible.sync="isModalVisible"
          :title="modalTitle"
          width="40%"
          @close="() => closeModal()"
          class="table-container__modal-window--image">
        <div v-if="modalTitle">
          <img :src="modalTitle" alt="Изображение"/>
        </div>
        <div v-else>
          <p>Загрузка изображения...</p>
        </div>
        <div class="modal-fields">
          <div class="field">
            <span class="field-label">Пациент:</span>
            <span class="field-value">{{ patientName }}</span>
          </div>

          <div class="field">
            <span class="field-label">Описание:</span>
            <span class="field-value">{{ description }}</span>
          </div>
        </div>
        <div slot="footer" class="el-dialog__footer">
          <ElButton @click="() => closeModal()">Закрыть</ElButton>
        </div>
      </ElDialog>
    </div>
    <div class="animated_container__pagination-container">
      <div class="pagination-container__pagination">
        <ElPagination
            layout="prev, pager, next"
            :current-page="currentPage"
            :page-size="itemsPerPage"
            :total="data.length"
            @current-change="(page)=>changePage(page)">
        </ElPagination>
      </div>
    </div>
  </div>
</template>

<script>
import VueDropzone from 'vue2-dropzone';
import {mapActions} from 'vuex';
import {MessageBox} from 'element-ui';
import {AUTH_TOKEN} from "@/views/LoginView.vue";
import axiosInstance from "@/axios";
import {ROUTES} from "@/router";
import router from "@/router";

export default {
  components: {
    VueDropzone,
  },
  props: {
    data: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: 5,
      loading: false,
      patientName: "Иван Иванов",
      description: "Пациент поступил на обследование с подозрением на кожное заболевание.",
      isModalVisible: false,
      modalTitle: '',
      isDownloadModalVisible: false,
      formData: {
        patient: '',
        description: '',
      },
      dropzoneOptions: {
        url: '/upload',
        autoProcessQueue: false,
        addRemoveLinks: false,
        maxFiles: 1,
        acceptedFiles: '.jpg, .jpeg',
        dictDefaultMessage: 'Перетащите файл сюда или нажмите для выбора.'
      },
      uploadedFiles: [],
    };
  },
  computed: {
    paginatedData() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.data.slice(start, end);
    },
    imageUrl() {
      return `${this.axiosInstance.defaults.baseURL}${this.modalTitle}`;
    }
  },
  methods: {
    axiosInstance,
    ...mapActions('table', ['removeData', 'removeAllData', 'predictData', 'fetchData']),

    logout() {
      MessageBox.confirm(
          'Вы уверены, что хотите выйти?',
          'Подтверждение выхода',
          {
            confirmButtonText: 'Да',
            cancelButtonText: 'Нет',
            type: 'warning',
          }
      )
          .then(() => {
            localStorage.removeItem(AUTH_TOKEN)
            router.push(ROUTES.LOGIN)
          })
          .catch(() => {
            console.log("Выход отменён")
          });
    },
    formatModelsAndResult(row) {
      return `${row.model_1} / ${row.model_2} / ${row.model_3} (${row.ensemble})`;
    },
    changePage(page) {
      this.currentPage = page;
    },
    deleteItem(index) {
      MessageBox.confirm(
          'Вы уверены, что хотите удалить этот элемент?',
          'Подтверждение удаления',
          {
            confirmButtonText: 'Да',
            cancelButtonText: 'Нет',
            type: 'warning',
          }
      )
          .then(() => {
            const globalIndex = (this.currentPage - 1) * this.itemsPerPage + index;
            const itemToRemove = this.data[globalIndex];
            this.removeData(itemToRemove.id);
          })
          .catch(() => {
            console.log('Удаление отменено.');
          });
    },
    deleteAll() {
      MessageBox.confirm(
          'Вы уверены, что хотите удалить все?',
          'Подтверждение удаления',
          {
            confirmButtonText: 'Да',
            cancelButtonText: 'Нет',
            type: 'warning',
          }
      )
          .then(() => {
            console.log("Удаление подтверждено.");
            this.removeAllData();
          })
          .catch(() => {
            this.$message.info('Удаление отменено.');
          });
    },
    loadMore() {
      const inputElement = this.$refs.upload.$el.querySelector('input');
      if (inputElement) {
        inputElement.click();
      } else {
        console.error('Не удалось найти input внутри el-upload');
      }
    },
    openDownloadModal() {
      this.isDownloadModalVisible = true;
    },
    handleFileAdded(file) {
      console.log('Файл добавлен:', file);
      this.uploadedFiles = [file];
    },
    handleSubmit() {
      if (this.uploadedFiles.length === 0) {
        this.$message.error('Пожалуйста, загрузите изображение.');
        return;
      }

      if (!this.formData.patient || !this.formData.description) {
        this.$message.error('Пожалуйста, заполните все поля.');
        return;
      }

      const formData = new FormData();
      formData.append('patient', this.formData.patient);
      formData.append('description', this.formData.description);
      formData.append('image', this.uploadedFiles[0]);

      axiosInstance.post('http://localhost:8000/back/classification-image/6281', formData)
          .then((response) => {
            this.$message.success('Данные успешно отправлены!');
            console.log('Ответ сервера:', response.data);
            this.closeDownloadModal();
          })
          .catch((error) => {
            this.$message.error('Ошибка при отправке данных.');
            console.error('Ошибка:', error);
          });
    },
    closeDownloadModal() {
      this.isDownloadModalVisible = false;
      this.uploadedFiles = [];
      this.$refs.myDropzone.removeAllFiles();
    },
    openModal(row) {
      this.isModalVisible = true;
      this.modalTitle = row.image
    },
    closeModal() {
      this.isModalVisible = false;
    },
    handleImageChange(file) {
      let selectedFile = file.raw;

      if (!selectedFile) {
        this.$message.error('Пожалуйста, выберите изображение.');
        return;
      }

      this.loading = true;

      console.log('Файл для предсказания:', selectedFile);

      this.predictData(selectedFile)
          .then(() => {
            this.$message.success('Данные успешно отправлены и обработаны!');
          })
          .catch(error => {
            console.error('Ошибка предсказания:', error);
            this.$message.error('Ошибка при выполнении предсказания.');
          })
          .finally(() => {
            this.loading = false;
          });
    },
  },
};
</script>


<style scoped>
.modal-fields {
  margin-top: 20px;

  .field {
    margin-bottom: 10px;
    font-size: 14px;
    color: #333;

    .field-label {
      font-weight: bold;
      margin-right: 5px;
      display: inline-block;
    }

    .field-value {
      color: #666;
    }
  }
}
.dropzone {
  background-color: rgba(128, 128, 128, 0.8);
  border: 2px dashed #ccc;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: rgba(128, 128, 128, 1);
  }

  .dz-remove {
    background-color: #ff4d4f;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 5px;
    text-decoration: none;
    font-size: 14px;
    cursor: pointer;
    transition: background-color 0.3s ease;

    &:hover {
      background-color: #d9363e;
    }
  }
}

img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.animated_container__pagination-container {

  &__pagination {
    display: flex;
    justify-content: center;
    text-align: center;
    margin-top: 20px;
  }
}

.animated_container__table-container {
  margin: 20px;
  text-align: end;

  &__header {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
  }

  &__controls {
    display: flex;
    gap: 10px;
    justify-content: center;
    text-align: center;
  }

  &__table {
    width: 100%;
  }

  &__modal-window {
    &--image {
      padding: 10px;
      box-sizing: border-box;
      overflow: hidden;
    }
  }
}
</style>