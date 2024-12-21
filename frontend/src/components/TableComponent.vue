<template>
  <div v-loading="loading" class="animated-container">
    <div class="table-container">
      <div class="table-container__controls">
        <ElButton @click="() => openLoad()" type="primary">Добавить</ElButton>
        <ElButton @click="() => openMoreLoad()" type="primary">Массовая загрузка</ElButton>
        <ElButton @click="() => deleteAll()" type="danger">Удалить все</ElButton>
        <ElButton @click="() => logout()" type="danger">Выход</ElButton>
        <ElDialog
            :visible.sync="isDownloadModalVisible"
            @close="() => closeDownloadModal()"
            title="Добавить данные"
            width="30%"
            class="controls-container__modal-window">
          <ElForm>
            <ElFormItem label="Пациент">
              <ElInput v-model="formData.patient" placeholder="Введите фио пациента"/>
            </ElFormItem>
            <ElFormItem label="Описание">
              <ElInput v-model="formData.description" type="textarea" placeholder="Введите описание"/>
            </ElFormItem>
            <ElFormItem>
              <vue-dropzone
                  :options="dropzoneImageOptions"
                  @vdropzone-file-added="handleFileAdded"
                  ref="myDropzone"
                  class="controls-container__modal-window--dropzone">
              </vue-dropzone>
            </ElFormItem>
          </ElForm>
          <span slot="footer" class="controls-container__dialog-footer">
            <ElButton @click="() => closeDownloadModal()">Отмена</ElButton>
            <ElButton @click="() => handleSubmit()" type="primary">Сохранить</ElButton>
          </span>
        </ElDialog>
        <ElDialog
            :visible.sync="isDownloadImagesModalVisible"
            @close="() => closeDownloadModal()"
            title="Добавить данные"
            width="30%"
            class="controls-container__modal-window">
          <ElForm>
            <ElFormItem>
              <vue-dropzone
                  :options="dropzoneImagesOptions"
                  @vdropzone-file-added="handleFileAdded"
                  ref="myDropzone"
                  class="controls-container__modal-window--dropzone">
              </vue-dropzone>
            </ElFormItem>
          </ElForm>
          <span slot="footer" class="controls-container__dialog-footer">
            <ElButton @click="() => closeDownloadModal()">Отмена</ElButton>
            <ElButton @click="() => handleSubmits()" type="primary">Сохранить</ElButton>
          </span>
        </ElDialog>
      </div>
      <ElTable
          :data="paginatedData"
          @row-click="(row) => openModal(row, paginatedData)"
          class="table-container__table" >
        <ElTableColumn label="Пациент" prop="patient"/>
        <ElTableColumn label="Изображение">
          <template #default="{ row }">
            <img :src="row.image" class="table-container__table--preview-image" alt="Предпросмотр"/>
          </template>
        </ElTableColumn>
        <ElTableColumn label="Дата и время загрузки" prop="date"/>
        <ElTableColumn label="Модель 1 / Модель 2 / Модель 3 (Ансамбль)">
          <template #default="scope">
            <span>{{ formatModelsAndResult(scope.row) }}</span>
            <i v-if="isResultMatch(scope.row)" class="table-container__result-check el-icon-check"/>
          </template>
        </ElTableColumn>
        <ElTableColumn label="Действия" class="table-container__actions" header-align="right">
          <template #default="{ $index }">
            <ElButton @click.stop="() => deleteItem($index)" size="mini" type="danger">Удалить</ElButton>
          </template>
        </ElTableColumn>
        <template #empty>
          <p>Нет данных для отображения. Таблица пустая.</p>
        </template>
      </ElTable>
      <ElDialog
          :visible.sync="isModalVisible"
          @close="() => closeModal()"
          title="Результат"
          width="40%"
          class="table-container__modal-window--image">
        <div v-if="modalTitle">
          <img :src="modalTitle" alt="Изображение"/>
          <div class="table-container__modal-probabilities">
            <div class="table-container__modal-probabilities--field">
              <span class="table-container__modal-probabilities--field--field-label">Вероятность 1 модели:</span>
              <span class="table-container__modal-probabilities--field--field-value">
                {{ formatModelProbability(selectedRow.model_1, selectedRow.model_1_probability) }}
              </span>
            </div>
            <div class="table-container__modal-probabilities--field">
              <span class="table-container__modal-probabilities--field--field-label">Вероятность 2 модели:</span>
              <span class="table-container__modal-probabilities--field--field-value">
                {{ formatModelProbability(selectedRow.model_2, selectedRow.model_2_probability) }}
              </span>
            </div>
            <div class="table-container__modal-probabilities--field">
              <span class="table-container__modal-probabilities--field--field-label">Вероятность 3 модели:</span>
              <span class="table-container__modal-probabilities--field--field-value">
                {{ formatModelProbability(selectedRow.model_3, selectedRow.model_3_probability) }}
              </span>
            </div>
            <div class="table-container__modal-probabilities--field">
              <span class="table-container__modal-probabilities--field--field-label">Вероятность ансамбля:</span>
              <span class="table-container__modal-probabilities--field--field-value">
                {{ selectedRow.ensemble }} - {{ (parseFloat(selectedRow.ensemble_probability) / 3 * 100).toFixed(2) }}%
              </span>
            </div>
          </div>
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
          <div class="field">
            <span class="field-label">Диагноз:</span>
            <span class="field-value">{{ getDiagnosisLabel(diagnosis) }}</span>
          </div>
        </div>
        <div class="el-dialog__footer" slot="footer">
          <ElButton @click="() => openEditModal()">Редактировать</ElButton>
          <ElButton @click="() => closeModal()">Закрыть</ElButton>
        </div>
      </ElDialog>
      <ElDialog
          :visible.sync="isEditModalVisible"
          @close="() => closeEditModal()"
          title="Редактирование записи"
          width="40%"
          class="table-container__edit-modal">
        <ElForm>
          <ElFormItem label="Описание">
            <ElInput v-model="editForm.description" type="textarea" placeholder="Введите новое описание"/>
          </ElFormItem>
          <ElFormItem label="Диагноз">
            <ElSelect v-model="editForm.diagnosis" placeholder="Выберите диагноз">
              <ElOption
                  v-for="option in diagnosisOptions"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"/>
              <ElOption label="Другое" value="other"/>
            </ElSelect>
          </ElFormItem>
        </ElForm>
        <span slot="footer" class="dialog-footer">
          <ElButton @click="() => closeEditModal()">Отмена</ElButton>
          <ElButton @click="() => submitEdit()" type="primary">Сохранить</ElButton>
        </span>
      </ElDialog>
    </div>
    <div class="animated-container__pagination-container">
      <div class="pagination-container__pagination">
        <ElPagination
            :current-page="currentPage"
            :page-size="itemsPerPage"
            :total="data.length"
            @current-change="(page)=>changePage(page)"
            layout="prev, pager, next">
        </ElPagination>
      </div>
    </div>
  </div>
</template>

<script>
import VueDropzone from 'vue2-dropzone';
import "dropzone/dist/dropzone.css";
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
      description: '',
      dropzoneImageOptions: {
        url: 'https://httpbin.org/post',
        addRemoveLinks: false,
        maxFiles: 1,
        acceptedFiles: '.jpg, .jpeg',
        dictDefaultMessage: 'Перетащите файл сюда или нажмите для выбора'
      },
      dropzoneImagesOptions: {
        url: 'https://httpbin.org/post',
        addRemoveLinks: false,
        maxFiles: 500,
        acceptedFiles: '.jpg, .jpeg',
        dictDefaultMessage: 'Перетащите файлы сюда или нажмите для выбора'
      },
      formData: {
        patient: '',
        description: '',
      },
      isDownloadModalVisible: false,
      isDownloadImagesModalVisible: false,
      isModalVisible: false,
      itemsPerPage: 5,
      loading: false,
      modalTitle: '',
      patientName: '',
      uploadedFiles: [],
      isEditModalVisible: false,
      editForm: {
        id: null,
        description: '',
        diagnosis: '',
      },
      diagnosisOptions: [
        {label: 'Актинический кератоз (AK)', value: 'AK'},
        {label: 'Базальноклеточная карцинома (BCC)', value: 'BCC'},
        {label: 'Доброкачественный кератоз (BKL)', value: 'BKL'},
        {label: 'Дерматофиброма (DF)', value: 'DF'},
        {label: 'Меланома (MEL)', value: 'MEL'},
        {label: 'Меланоцитарный невус (NV)', value: 'NV'},
        {label: 'Плоскоклеточный рак (SCC)', value: 'SCC'},
        {label: 'Сосудистое поражение (VASC)', value: 'VASC'},
      ],
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
    ...mapActions('table', ['removeData', 'removeAllData', 'predictData', 'predictListData', 'fetchData', 'updateRecord']),

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
    openLoad() {
      this.isDownloadModalVisible = true;
    },
    openMoreLoad() {
      this.isDownloadImagesModalVisible = true;
    },
    handleFileAdded: function (file) {
      console.log('Файл добавлен:', file);
      this.uploadedFiles.push(file);
    },
    handleSubmits() {
      if (this.uploadedFiles.length === 0) {
        this.$message.error('Пожалуйста, загрузите изображения.');
        return;
      }

      if (!this.formData.patient || !this.formData.description) {
        this.formData.patient = '-';
        this.formData.description = '-';
      }

      this.loading = true;

      this.predictListData({
        selectedFiles: this.uploadedFiles,
        patient: this.formData.patient,
        description: this.formData.description
      }).then(() => {
        this.$message.success('Данные успешно отправлены и обработаны!');
      })
          .catch(error => {
            console.error('Ошибка предсказания:', error);
            this.$message.error('Ошибка при выполнении предсказания.');
          })
          .finally(() => {
            this.loading = false;
          });


      this.isDownloadImagesModalVisible = false;
      this.uploadedFiles = [];
      this.formData = [];
      this.$refs.myDropzone.removeAllFiles();
    },
    handleSubmit() {
      console.log('Данные, полученные из формы:');
      console.log('Файл:', this.uploadedFiles[0]);
      console.log('Пациент:', this.formData.patient);
      console.log('Описание:', this.formData.description);

      if (this.uploadedFiles.length === 0) {
        this.$message.error('Пожалуйста, загрузите изображение.');
        return;
      }

      if (!this.formData.patient || !this.formData.description) {
        this.$message.error('Пожалуйста, заполните все поля.');
        return;
      }

      this.loading = true;

      this.predictData({
        selectedFile: this.uploadedFiles[0],
        patient: this.formData.patient,
        description: this.formData.description
      })
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

      this.isDownloadModalVisible = false;
      this.uploadedFiles = [];
      this.formData = [];
      this.$refs.myDropzone.removeAllFiles();
    },
    closeDownloadModal() {
      this.isDownloadModalVisible = false;
      this.isDownloadImagesModalVisible = false;
      this.uploadedFiles = [];
      this.formData = [];
      this.$refs.myDropzone.removeAllFiles();
    },
    openModal(row) {
      this.isModalVisible = true;
      this.modalTitle = row.image;
      this.patientName = row.patient;
      this.description = row.description;
      this.diagnosis = row.diagnosis;
      this.selectedRow = {
        ...row,
        model_1: row.model_1 || "Нет данных",
        model_2: row.model_2 || "Нет данных",
        model_3: row.model_3 || "Нет данных",
        ensemble: row.ensemble || "Нет данных",
        model_1_probability: row.model_1_probability || 0,
        model_2_probability: row.model_2_probability || 0,
        model_3_probability: row.model_3_probability || 0,
        ensemble_probability: row.ensemble_probability || 0
      };
    },
    closeModal() {
      this.isModalVisible = false;
    },
    formatModelProbability(modelName, probability) {
      const probabilityPercentage = (parseFloat(probability) * 100).toFixed(2);
      return `${modelName} - ${probabilityPercentage}%`;
    },
    openEditModal() {
      this.closeModal();
      this.isEditModalVisible = true;
      this.editForm.id = this.selectedRow.id;
      this.editForm.description = this.selectedRow.description;
      this.editForm.diagnosis = this.selectedRow.diagnosis;
    },
    closeEditModal() {
      this.isEditModalVisible = false;
      this.isModalVisible = true;
    },
    submitEdit() {
      if (!this.editForm.description || !this.editForm.diagnosis) {
        this.$message.error('Пожалуйста, заполните все поля.');
        return;
      }

      this.updateRecord(this.editForm)
          .then(() => {
            this.$message.success('Запись успешно обновлена!');

            this.description = this.editForm.description;
            this.diagnosis = this.editForm.diagnosis;

            if (this.selectedRow && this.selectedRow.id === this.editForm.id) {
              this.selectedRow.description = this.editForm.description;
              this.selectedRow.diagnosis = this.editForm.diagnosis;
            }

            this.closeEditModal();
          })
          .catch((error) => {
            console.error('Ошибка при обновлении записи:', error);
            this.$message.error('Ошибка при обновлении записи.');
          });
    },
    getDiagnosisLabel(value) {
      const option = this.diagnosisOptions.find(option => option.value === value);
      return option ? option.label : value;
    },
    isResultMatch(row) {
      return row.ensemble === row.diagnosis;
    },
  },
};
</script>


<style lang="less">

.modal-fields {
  margin-top: 20px;

  &__field {
    margin-bottom: 10px;
    font-size: 14px;
    color: #333;

    &__field-label {
      font-weight: bold;
      margin-right: 5px;
      display: inline-block;
    }

    &__field-value {
      color: #666;
    }
  }
}

.controls-container__modal-window--dropzone {
  background-color: rgba(192, 192, 192, 0.7);
  border: #ccc;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: rgba(192, 192, 192, 1);
  }
}

img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.dz-preview {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #d3d3d3;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.animated-container__pagination-container {

  &__pagination {
    display: flex;
    justify-content: center;
    text-align: center;
    margin-top: 20px;
  }
}

.table-container {
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
    justify-content: flex-end;
    text-align: center;
  }

  &__table {
    width: 100%;

    &--preview-image {
      width: 50px;
      height: 50px;
      object-fit: cover;
      border: 1px solid #ddd;
      padding: 2px;
      border-radius: 4px;
    }

    .el-table__row {
      .el-table__cell:last-child {
        text-align: right;
      }
    }
  }

  &__result-check {
    color: green;
    font-size: 20px;
    margin-left: 8px;
    vertical-align: middle;
  }

  &__modal-window {
    &--image {
      &__header {
        text-align: center;
      }
      padding: 10px;
      box-sizing: border-box;
      overflow: hidden;
    }

  }

  &__el-dialog {
    &__header{
      text-align: center;
      font-size: 18px;
      font-weight: bold;
    }
  }

  &__modal-probabilities {
    margin-top: 20px;

    &__field {
      margin-bottom: 10px;
      font-size: 14px;

      &__field-label {
        font-weight: bold;
        margin-right: 5px;
      }

      &__field-value {
        color: #666;
      }
    }
  }
}
</style>