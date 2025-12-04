<template>
  <div class="animated-container" v-loading="loading">
    <div class="table-container">
      <div class="table-container__controls">
        <ElButton type="primary" @click="() => openLoad()">Добавить</ElButton>
        <ElButton type="primary" @click="() => openMoreLoad()">Массовая загрузка</ElButton>
        <ElButton type="danger" @click="() => handleDeleteAll()">Удалить все</ElButton>
        <ElButton type="danger" @click="() => logout()">Выход</ElButton>

        <ElDialog
          :visible.sync="isDownloadModalVisible"
          title="Добавить данные"
          class="controls-container__modal-window"
          @close="closeDownloadModal"
        >
          <ElForm>
            <ElFormItem label="Пациент">
              <ElInput v-model="formData.patient" placeholder="Введите фио пациента"></ElInput>
            </ElFormItem>
            <ElFormItem label="Описание">
              <ElInput v-model="formData.description" type="textarea" placeholder="Введите описание"></ElInput>
            </ElFormItem>
            <ElFormItem>
              <vue-dropzone
                ref="myDropzone"
                id="dropzone"
                :options="dropzoneImageOptions"
                @vdropzone-file-added="handleFileAdded"
                class="controls-container__modal-window--dropzone">
              </vue-dropzone>
            </ElFormItem>
          </ElForm>
          <span slot="footer" class="controls-container__dialog-footer">
          <ElButton @click="closeDownloadModal">Отмена</ElButton>
          <ElButton type="primary" @click="handleSubmit">Сохранить</ElButton>
        </span>
        </ElDialog>

        <ElDialog
          :visible.sync="isDownloadImagesModalVisible"
          title="Добавить данные"
          @close="closeDownloadModal"
          class="controls-container__modal-window">
          <ElForm>
            <ElFormItem>
              <vue-dropzone
                ref="myDropzone"
                id="dropzone"
                :options="dropzoneImagesOptions"
                @vdropzone-file-added="handleFileAdded"
                class="controls-container__modal-window--dropzone">
              </vue-dropzone>
            </ElFormItem>
          </ElForm>
          <span slot="footer" class="controls-container__dialog-footer">
          <ElButton @click="closeDownloadModal">Отмена</ElButton>
          <ElButton type="primary" @click="handleSubmits">Сохранить</ElButton>
        </span>
        </ElDialog>
      </div>

      <ElTable 
        class="table-container__table" 
        :data="data" 
        :row-class-name="getRowClassName"
        @row-click="(row) => openModal(row)"
      >
        <!-- Колонка автора для админов и модераторов -->
        <ElTableColumn 
          v-if="userRole === 'admin' || userRole === 'moderator'"
          label="Автор" 
          prop="author"
          width="150"
          align="center"
        >
          <template #default="{ row }">
            <span v-if="row.author">{{ row.author }}</span>
            <span v-else class="unknown-author">Неизвестно</span>
          </template>
        </ElTableColumn>

        <ElTableColumn label="Пациент" prop="patient">
          <template #default="{ row }">
            <div class="patient-cell">
              <span :class="{ 'deleted-patient': row.is_deleted }">
                {{ row.patient }}
              </span>
              <ElTag v-if="row.is_deleted" type="danger" size="mini" class="deleted-tag">
                Удалено
              </ElTag>
            </div>
          </template>
        </ElTableColumn>
        
        <ElTableColumn label="Изображение" width="140" align="center">
          <template #default="{ row }">
            <div class="image-cell">
              <img
                class="table-container__table--preview-image"
                :class="{ 'deleted-image': row.is_deleted }"
                :src="row.image"
                alt="Предпросмотр"
              />
              <div v-if="row.is_deleted" class="image-overlay">
                <i class="el-icon-delete"></i>
              </div>
            </div>
          </template>
        </ElTableColumn>
        
        <ElTableColumn label="Дата и время загрузки" prop="date" width="220" align="center"/>
        
        <ElTableColumn label="Модель 1 / Модель 2 / Модель 3 (Ансамбль)">
          <template #default="{ row }">
            <span :class="{ 'deleted-text': row.is_deleted }">
              {{ formatModelsAndResult(row) }}
            </span>
            <i v-if="row.ensemble === row.diagnosis && !row.is_deleted" class="table-container__result-check el-icon-check"></i>
          </template>
        </ElTableColumn>
        
        <ElTableColumn label="Действия" class="table-container__actions" width="180">
          <template #default="{ row }">
            <div class="action-buttons">
              <ElButton
                type="danger"
                size="mini"
                @click.stop="() => handleDeleteItem(row)"
                :disabled="row.is_deleted && userRole === 'regular'"
              >
                {{ getDeleteButtonText(row) }}
              </ElButton>
            </div>
          </template>
        </ElTableColumn>
        
        <template #empty>
          <div class="empty-table">
            <p>Нет данных для отображения.</p>
            <p v-if="showFilter === 'deleted'" class="empty-hint">
              Нет удаленных записей
            </p>
            <p v-else class="empty-hint">
              Таблица пустая. Добавьте новые анализы.
            </p>
          </div>
        </template>
      </ElTable>

      <ElDialog
        v-if="selectedRow"
        :visible.sync="isSelected"
        title="Результат"
        width="40%"
        class="table-container__modal-window--image"
        @close="() => closeModal()"
      >
        <div v-if="selectedRow.image">
          <img :src="selectedRow.image" alt="Изображение"/>
          <div class="modal-probabilities">
            <div class="field">
              <span class="field-label">Вероятность 1 модели:</span>
              <span
                class="field-value">{{ listObj[selectedRow.model_1] }} -
                {{ (parseFloat(selectedRow.model_1_probability) * 100).toFixed(2) }}%</span>
            </div>
            <div class="field">
              <span class="field-label">Вероятность 2 модели:</span>
              <span
                class="field-value">{{ listObj[selectedRow.model_2] }} -
                {{ (parseFloat(selectedRow.model_2_probability) * 100).toFixed(2) }}%</span>
            </div>
            <div class="field">
              <span class="field-label">Вероятность 3 модели:</span>
              <span
                class="field-value">{{ listObj[selectedRow.model_3] }} -
                {{ (parseFloat(selectedRow.model_3_probability) * 100).toFixed(2) }}%</span>
            </div>
            <div class="field">
              <span class="field-label">Вероятность ансамбля:</span>
              <span class="field-value">
                {{ listObj[selectedRow.ensemble] }} -
                {{ (parseFloat(selectedRow.ensemble_probability) / 3 * 100).toFixed(2) }}%
              </span>
            </div>
          </div>
        </div>
        <div v-else>
          <p>Загрузка изображения...</p>
        </div>
        <div class="modal-fields">
          <!-- Информация об авторе для админов и модераторов -->
          <div v-if="(userRole === 'admin' || userRole === 'moderator') && selectedRow.author" class="field">
            <span class="field-label">Автор:</span>
            <span class="field-value">{{ selectedRow.author }}</span>
          </div>

          <div class="field">
            <span class="field-label">Пациент:</span>
            <span class="field-value">{{ selectedRow.patient }}</span>
          </div>

          <div class="field">
            <span class="field-label">Описание:</span>
            <span class="field-value">{{ selectedRow.description }}</span>
          </div>

          <div class="field">
            <span class="field-label">Диагноз:</span>
            <span class="field-value">{{ getDiagnosisLabel(selectedRow.diagnosis) }}</span>

            <i v-if="selectedRow.diagnosis === selectedRow.ensemble && !selectedRow.is_deleted" class="table-container__result-check el-icon-check"></i>
          </div>

          <!-- Статус удаления -->
          <div v-if="selectedRow.is_deleted" class="field">
            <span class="field-label">Статус:</span>
            <ElTag type="danger" size="small">Удалено</ElTag>
          </div>
        </div>
        <div slot="footer">
          <ElButton @click="() => openEditModal()" :disabled="selectedRow.is_deleted">Редактировать</ElButton>
          <ElButton @click="() => closeModal()">Закрыть</ElButton>
        </div>
      </ElDialog>
      
      <ElDialog
        :visible.sync="isEditModalVisible"
        title="Редактирование записи"
        width="40%"
        class="table-container__edit-modal"
        @close="() => closeEditModal()"
      >
        <ElForm>
          <ElFormItem label="Описание">
            <ElInput v-model="editForm.description" type="textarea" placeholder="Введите новое описание"></ElInput>
          </ElFormItem>
          <ElFormItem label="Диагноз">
            <ElSelect v-model="editForm.diagnosis" placeholder="Выберите диагноз">
              <ElOption
                v-for="option in diagnosisOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
              <ElOption label="Другое" value="other"/>
            </ElSelect>
          </ElFormItem>
        </ElForm>
        <span slot="footer" class="dialog-footer">
          <ElButton @click="() => closeEditModal()">Отмена</ElButton>
          <ElButton type="primary" @click="() => submitEdit()">Сохранить!</ElButton>
        </span>
      </ElDialog>
    </div>
  </div>
</template>

<script>
import VueDropzone from 'vue2-dropzone';
import { mapActions } from 'vuex';
import { AUTH_TOKEN } from "@/views/LoginView.vue";
import axiosInstance from "@/axios";
import { ROUTES } from "@/router";
import router from "@/router";

const list = {
  AK: 'Актинический кератоз (AK)',
  BCC: 'Базальноклеточная карцинома (BCC)',
  BKL: 'Доброкачественный кератоз (BKL)',
  DF: 'Дерматофиброма (DF)',
  MEL: 'Меланома (MEL)',
  NV: 'Меланоцитарный невус (NV)',
  SCC: 'Плоскоклеточный рак (SCC)',
  VASC: 'Сосудистое поражение (VASC)'
}

export default {
  components: {
    VueDropzone,
  },
  props: {
    data: {
      type: Array,
      required: true,
    },
    userRole: {
      type: String,
      default: 'regular'
    },
    showFilter: {
      type: String,
      default: 'active'
    }
  },
  data () {
    return {
      selectedRow: null,
      description: '',

      dropzoneImageOptions: {
        url: '/upload',
        autoProcessQueue: false,
        addRemoveLinks: false,
        maxFiles: 1,
        acceptedFiles: '.jpg, .jpeg',
        dictDefaultMessage: 'Перетащите файл сюда или нажмите для выбора'
      },
      dropzoneImagesOptions: {
        url: '/upload',
        autoProcessQueue: false,
        addRemoveLinks: false,
        previewsContainer: false,
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
      loading: false,
      uploadedFiles: [],
      isEditModalVisible: false,
      editForm: {
        id: null,
        description: '',
        diagnosis: '',
      },
    };
  },
  computed: {
    isSelected () {
      return !!this.selectedRow
    },
    listObj () {
      return list
    },
    diagnosisOptions () {
      return [
        { label: 'Актинический кератоз (AK)', value: 'AK' },
        { label: 'Базальноклеточная карцинома (BCC)', value: 'BCC' },
        { label: 'Доброкачественный кератоз (BKL)', value: 'BKL' },
        { label: 'Дерматофиброма (DF)', value: 'DF' },
        { label: 'Меланома (MEL)', value: 'MEL' },
        { label: 'Меланоцитарный невус (NV)', value: 'NV' },
        { label: 'Плоскоклеточный рак (SCC)', value: 'SCC' },
        { label: 'Сосудистое поражение (VASC)', value: 'VASC' },
      ]
    },
    diagnosisLabels () {
      const t = {
        'undefined': '-'
      }
      this.diagnosisOptions.forEach(i => {
        t[i.value] = i.label
      })
      return t
    }
  },
  methods: {
    axiosInstance,
    ...mapActions('table', [
      'removeData',
      'removeAllData',
      'predictData',
      'predictListData',
      'fetchData',
      'updateRecord'
    ]),

    getRowClassName({ row }) {
      if (row.is_deleted) {
        return 'deleted-row';
      }
      return '';
    },

    getDeleteButtonText(row) {
      if (row.is_deleted) {
        return 'Удалить навсегда';
      }
      return 'Удалить';
    },

    handleDeleteItem(row) {
      this.$emit('delete-item', row);
    },

    handleDeleteAll() {
      this.$emit('delete-all');
    },

    logout () {
      this.$confirm(
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
    
    formatModelsAndResult (row) {
      return `${ row.model_1 } / ${ row.model_2 } / ${ row.model_3 } (${ this.diagnosisLabels[row.ensemble] })`;
    },
    
    openLoad () {
      this.isDownloadModalVisible = true;
    },
    
    openMoreLoad () {
      this.isDownloadImagesModalVisible = true;
    },
    
    handleFileAdded: function (file) {
      console.log('Файл добавлен:', file);

      this.uploadedFiles.push(file);

      if (this.uploadedFiles.length > 1) {
        const dropzoneElement = this.$refs.myDropzone.$el;
        const messageElement = dropzoneElement.querySelector('.dz-message');
        if (messageElement) {
          messageElement.innerText = `Количество загруженных файлов: ${ this.uploadedFiles.length }`;
        }
      }

      if (this.uploadedFiles.length === 1) {
        const dropzoneElement = this.$refs.myDropzone.$el;
        const messageElement = dropzoneElement.querySelector('.dz-message');
        if (messageElement) {
          messageElement.innerText = '';
        }
      }

      setTimeout(() => {
        const successMarks = document.querySelectorAll('.dz-success-mark');
        const errorMarks = document.querySelectorAll('.dz-error-mark');
        successMarks.forEach(mark => mark.remove());
        errorMarks.forEach(mark => mark.remove());
      }, 0);
    },
    
    handleSubmits () {
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
        this.$emit('refresh');
      })
        .catch(error => {
          console.error('Ошибка предсказания:', error);
          this.$message.error('Ошибка при выполнении предсказания.');
        })
        .finally(() => {
          this.loading = false;
        });

      this.isDownloadImagesModalVisible = false;
      if (this.uploadedFiles.length > 1) {
        const dropzoneElement = this.$refs.myDropzone.$el;
        const messageElement = dropzoneElement.querySelector('.dz-message');
        if (messageElement) {
          messageElement.innerText = 'Перетащите файлы сюда или нажмите для выбора';
        }
      }
      this.uploadedFiles = [];
      this.formData = [];
      this.$refs.myDropzone.removeAllFiles();
    },
    
    handleSubmit () {
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
          this.$emit('refresh');
        })
        .catch(error => {
          console.error('Ошибка предсказания:', error);
          this.$message.error('Ошибка при выполнении предсказания.');
        })
        .finally(() => {
          this.loading = false;
        });

      this.isDownloadModalVisible = false;
      if (this.uploadedFiles.length === 1) {
        const dropzoneElement = this.$refs.myDropzone.$el;
        const messageElement = dropzoneElement.querySelector('.dz-message');
        if (messageElement) {
          messageElement.innerText = 'Перетащите файл сюда или нажмите для выбора';
        }
      }
      this.uploadedFiles = [];
      this.formData = [];
      this.$refs.myDropzone.removeAllFiles();
    },
    
    closeDownloadModal () {
      this.isDownloadModalVisible = false;
      this.isDownloadImagesModalVisible = false;
      this.uploadedFiles = [];
      this.formData = [];
      this.$refs.myDropzone.removeAllFiles();
    },
    
    openModal (row) {
      this.selectedRow = {
        ...row,
      }
    },
    
    closeModal () {
      this.selectedRow = null;
    },
    
    openEditModal () {
      this.isEditModalVisible = true;
      this.editForm.id = this.selectedRow.id;
      this.editForm.description = this.selectedRow.description;
      this.editForm.diagnosis = this.selectedRow.diagnosis

      this.closeModal();
    },
    
    closeEditModal () {
      this.isEditModalVisible = false;
    },
    
    submitEdit () {
      if (!this.editForm.description || !this.editForm.diagnosis) {
        this.$message.error('Пожалуйста, заполните все поля.');
        return;
      }

      this.updateRecord(this.editForm)
        .then(() => {
          this.$message.success('Запись успешно обновлена!');
          this.$emit('refresh');

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
    
    getDiagnosisLabel (value) {
      const option = this.diagnosisOptions.find(option => option.value === value);
      return option ? option.label : value;
    }
  },
};
</script>

<style lang="less">
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
      min-width: 120px;
    }

    .field-value {
      color: #666;
    }
  }
}

.controls-container__modal-window--dropzone {
  background-color: #f5f5f5;
  border: transparent;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #f0f0f0;
  }
}

img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.table-container {
  margin: 20px;

  &__header {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
  }

  &__controls {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-bottom: 20px;
  }

  &__table {
    width: 100%;

    // Стили для удаленных строк
    .deleted-row {
      background-color: #fafafa !important;
      
      td {
        color: #999 !important;
      }
      
      &:hover > td {
        background-color: #f5f5f5 !important;
      }
    }

    &--preview-image {
      width: 50px;
      height: 50px;
      object-fit: cover;
      border: 1px solid #ddd;
      padding: 2px;
      border-radius: 4px;
      
      &.deleted-image {
        opacity: 0.6;
        filter: grayscale(50%);
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

  .el-dialog {
    &__header {
      text-align: center;
      font-size: 18px;
      font-weight: bold;
    }
  }
}

.modal-probabilities {
  margin-top: 20px;

  .field {
    margin-bottom: 10px;
    font-size: 14px;

    .field-label {
      font-weight: bold;
      margin-right: 5px;
    }

    .field-value {
      color: #666;
    }
  }
}

// Стили для ячеек с удаленными записями
.patient-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .deleted-patient {
    color: #999;
    text-decoration: line-through;
  }
  
  .deleted-tag {
    margin-left: 4px;
  }
}

.image-cell {
  position: relative;
  display: inline-block;
  
  .image-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 4px;
    
    i {
      color: white;
      font-size: 20px;
    }
  }
}

.deleted-text {
  color: #999;
}

.unknown-author {
  color: #999;
  font-style: italic;
}

.action-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.empty-table {
  text-align: center;
  padding: 40px 0;
  
  .empty-hint {
    color: #909399;
    font-size: 14px;
    margin-top: 8px;
  }
}
</style>