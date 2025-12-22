<template>
  <div class="animated-container table-container" v-loading="loading">
    <div class="table-container__content">
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
              <!-- Дропзон для одиночной загрузки - показывается только если нет обрезанного изображения -->
              <vue-dropzone
                ref="singleDropzone"
                id="dropzone-single"
                :options="dropzoneImageOptions"
                @vdropzone-file-added="handleSingleFileAdded"
                @vdropzone-click="handleSingleDropzoneClick"
                class="controls-container__modal-window--dropzone"
                v-if="!croppedImageUrl"
              >
              </vue-dropzone>
              
              <!-- Превью обрезанного изображения -->
              <div v-else class="cropped-image-preview" @click="handlePreviewClick">
                <div class="preview-header">
                  <span>Обрезанное изображение</span>
                  <ElButton 
                    type="text" 
                    icon="el-icon-refresh" 
                    @click.stop="replaceCroppedImage" 
                    title="Заменить изображение"
                  >
                  </ElButton>
                </div>
                <img :src="croppedImageUrl" alt="Обрезанное изображение" class="cropped-preview-img" />
                <div class="preview-footer">
                  <span class="file-info">{{ croppedFileName }}</span>
                  <ElButton 
                    type="text" 
                    icon="el-icon-delete" 
                    @click.stop="removeCroppedImage" 
                    title="Удалить изображение"
                  >
                  </ElButton>
                </div>
              </div>
            </ElFormItem>
          </ElForm>
          <span slot="footer" class="controls-container__dialog-footer">
            <ElButton @click="closeDownloadModal">
              Отмена
            </ElButton>
            <ElButton
              type="primary"
              @click="handleSubmit"
              :loading="loading" 
              :disabled="uploadedFiles.length === 0"
            >
              Сохранить
            </ElButton>
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
                ref="multipleDropzone"
                id="dropzone-multiple"
                :options="dropzoneImagesOptions"
                @vdropzone-file-added="handleMultipleFileAdded"
                class="controls-container__modal-window--dropzone">
              </vue-dropzone>
            </ElFormItem>
          </ElForm>
          <span slot="footer" class="controls-container__dialog-footer">
            <ElButton @click="closeDownloadModal">
              Отмена
            </ElButton>
            <ElButton
              type="primary"
              @click="handleSubmits"
              :loading="loading" 
              :disabled="uploadedFiles.length === 0"
            >
              Сохранить
            </ElButton>
          </span>
        </ElDialog>

        <!-- Модальное окно для обрезки изображения -->

        <ImageCropperModal
          :visible.sync="cropperModalVisible"
          :image-file="imageForCropping"
          title="Обрезка изображения (требуется формат 1:1)"
          @confirm="handleCroppedImage"
          @cancel="handleCropCancel"
        />
      </div>

      <!-- Таблица с классом для глобальных стилей -->
      <ElTable 
        class="table-container__table analysis-table analysis-table--wide"
        :data="data" 
        :row-class-name="getRowClassName"
        @row-click="(row) => openModal(row)"
      >
        <!-- Колонка автора для админов и модераторов -->
        <ElTableColumn 
          v-if="userRole === 'admin' || userRole === 'moderator'"
          label="Автор" 
          prop="author"
          align="center"
          class-name="analysis-table__column analysis-table__column--author"
        >
          <template #default="{ row }">
            <span v-if="row.author">{{ row.author }}</span>
            <span v-else class="unknown-author">Неизвестно</span>
          </template>
        </ElTableColumn>

        <ElTableColumn 
          label="Пациент" 
          prop="patient"
          class-name="analysis-table__column analysis-table__column--patient"
        >
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
        
        <ElTableColumn 
          label="Изображение" 
          align="center"
          class-name="analysis-table__column analysis-table__column--image"
        >
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
        
        <ElTableColumn 
          label="Дата и время загрузки" 
          prop="date" 
          align="center"
          class-name="analysis-table__column analysis-table__column--date"
        />
        
        <ElTableColumn 
          label="Модель 1 / Модель 2 / Модель 3 (Ансамбль)"
          class-name="analysis-table__column analysis-table__column--models"
        >
          <template #default="{ row }">
            <span :class="{ 'deleted-text': row.is_deleted }">
              {{ formatModelsAndResult(row) }}
            </span>
            <i v-if="row.ensemble === row.diagnosis && !row.is_deleted" class="table-container__result-check el-icon-check"></i>
          </template>
        </ElTableColumn>
        
        <ElTableColumn 
          label="Действия" 
          class="table-container__actions" 
          class-name="analysis-table__column analysis-table__column--actions"
        >
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
        <div class="modal-content">
          <div v-if="selectedRow.image" class="modal-content__container">
            <div class="modal-image-section">
              <img :src="selectedRow.image" alt="Изображение" class="modal-image"/>
            </div>
            <div class="modal-text-section">
              <div class="modal-probabilities">
                <div class="field">
                  <span class="field-label">Вероятность 1 модели:</span>
                  <span class="field-value">{{ listObj[selectedRow.model_1] }} - {{ (parseFloat(selectedRow.model_1_probability) * 100).toFixed(2) }}%</span>
                </div>
                <div class="field">
                  <span class="field-label">Вероятность 2 модели:</span>
                  <span class="field-value">{{ listObj[selectedRow.model_2] }} - {{ (parseFloat(selectedRow.model_2_probability) * 100).toFixed(2) }}%</span>
                </div>
                <div class="field">
                  <span class="field-label">Вероятность 3 модели:</span>
                  <span class="field-value">{{ listObj[selectedRow.model_3] }} - {{ (parseFloat(selectedRow.model_3_probability) * 100).toFixed(2) }}%</span>
                </div>
                <div class="field">
                  <span class="field-label">Вероятность ансамбля:</span>
                  <span class="field-value">
                    {{ listObj[selectedRow.ensemble] }} - {{ (parseFloat(selectedRow.ensemble_probability) / 3 * 100).toFixed(2) }}%
                  </span>
                </div>
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
                  <span class="field-value description-text">{{ selectedRow.description }}</span>
                </div>

                <div class="field">
                  <span class="field-label">Диагноз:</span>
                  <span class="field-value">{{ getDiagnosisLabel(selectedRow.diagnosis) }}</span>
                  <i v-if="selectedRow.diagnosis === selectedRow.ensemble && !selectedRow.is_deleted" class="table-container__result-check el-icon-check"></i>
                </div>

                <!-- Статус удаления -->
                <div v-if="selectedRow.is_deleted" class="field">
                  <span class="field-label">Статус:</span>
                  <ElTag type="danger" size="small">
                    Удалено
                  </ElTag>
                </div>
              </div>
            </div>
          </div>
          <div v-else>
            <p>Загрузка изображения...</p>
          </div>
        </div>
        
        <div slot="footer">
          <ElButton 
            @click="() => openEditModal()" 
            :disabled="selectedRow.is_deleted"
          >
            Редактировать
          </ElButton>
          <ElButton @click="() => closeModal()">
            Закрыть
          </ElButton>
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
          <ElButton @click="() => closeEditModal()">
            Отмена
          </ElButton>
          <ElButton 
            type="primary" 
            @click="() => submitEdit()"
          >
            Сохранить!
          </ElButton>
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
import ImageCropperModal from '@/components/ImageCropperModal.vue';

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
    ImageCropperModal
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
        addRemoveLinks: true,
        maxFiles: 1,
        acceptedFiles: '.jpg, .jpeg, .png, .bmp',
        dictDefaultMessage: 'Перетащите файл сюда или нажмите для выбора',
        dictRemoveFile: 'Удалить',
        dictCancelUpload: 'Отмена'
      },
      dropzoneImagesOptions: {
        url: '/upload',
        autoProcessQueue: false,
        addRemoveLinks: false,
        previewsContainer: false,
        maxFiles: 500,
        acceptedFiles: '.jpg, .jpeg, .png, .bmp',
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
      
      // Данные для обрезки изображений
      cropperModalVisible: false,
      imageForCropping: null,
      currentDropzoneType: 'single', // 'single' или 'multiple'
      
      // Данные для отображения обрезанного изображения
      croppedImageUrl: null,
      croppedFileName: '',
    };
  },
  computed: {
    isSelected () {
      return !!this.selectedRow;
    },
    listObj () {
      return list;
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
      ];
    },
    diagnosisLabels () {
      const t = {
        'undefined': '-'
      };
      this.diagnosisOptions.forEach(i => {
        t[i.value] = i.label;
      });
      return t;
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
      if (this.userRole === 'regular') {
        // подтверждение на мягкое удаление всех активных записей (пользователи)
        this.$confirm(
          `Вы уверены, что хотите удалить все ваши активные записи (${this.data.length} шт.)?`,
          'Подтверждение удаления',
          {
            confirmButtonText: 'Да, удалить',
            cancelButtonText: 'Отмена',
            type: 'warning',
          }
        )
          .then(() => {
            this.$emit('delete-all', {
              permanent: false,
              show: 'active',
              isRegularUser: true,
              count: this.data.length
            });
          })
          .catch(() => {
            console.log("Удаление отменено");
          });
      } else {
        // для администраторов и модераторов данные для модального окна с выбором
        const filterLabels = {
          'all': 'все записи',
          'active': 'все активные записи',
          'deleted': 'все удалённые записи'
        };
        
        const filterLabel = filterLabels[this.showFilter] || 'записи';
        
        this.$emit('delete-all', {
          showFilter: this.showFilter,
          count: this.data.length,
          filterLabel: filterLabel
        });
      }
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
          localStorage.removeItem(AUTH_TOKEN);
          router.push(ROUTES.LOGIN);
        })
        .catch(() => {
          console.log("Выход отменён");
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
    
    handleSingleFileAdded (file) {
      console.log('Файл добавлен для одиночной загрузки:', file);

      // сохранение файла для обрезки и отображение модального окна
      this.imageForCropping = file;
      this.currentDropzoneType = 'single';
      this.cropperModalVisible = true;
      
      // удаление файла из дропзона, так как будет использоваться обрезанный
      this.$refs.singleDropzone.removeFile(file);
    },
    
    handleSingleDropzoneClick(file) {
      // при клике на уже загруженный файл в дропзоне
      if (file && this.uploadedFiles.length > 0) {
        this.$confirm('Хотите заменить изображение?', 'Замена изображения', {
          confirmButtonText: 'Да',
          cancelButtonText: 'Нет',
          type: 'warning'
        }).then(() => {
          this.removeCroppedImage();
        }).catch(() => {});
      }
    },
    
    handlePreviewClick() {
      // при клике на превью открываем окно обрезки с текущим файлом
      if (this.uploadedFiles.length > 0 && this.uploadedFiles[0]) {
        this.imageForCropping = this.uploadedFiles[0];
        this.currentDropzoneType = 'single';
        this.cropperModalVisible = true;
      }
    },
    
    replaceCroppedImage() {
      this.removeCroppedImage();
      // дропзонка для выбора нового файла
      setTimeout(() => {
        if (this.$refs.singleDropzone && this.$refs.singleDropzone.$el) {
          const messageElement = this.$refs.singleDropzone.$el.querySelector('.dz-message');
          if (messageElement) {
            messageElement.click();
          }
        }
      }, 100);
    },
    
    removeCroppedImage() {
      this.croppedImageUrl = null;
      this.croppedFileName = '';
      this.uploadedFiles = [];
      if (this.$refs.singleDropzone) {
        this.$refs.singleDropzone.removeAllFiles();
      }
    },
    
    handleMultipleFileAdded (file) {
      console.log('Файл добавлен для массовой загрузки:', file);
      
      // Для массовой загрузки сразу добавляем файл в uploadedFiles
      this.uploadedFiles.push(file);

      // Обновляем сообщение в дропзоне
      if (this.uploadedFiles.length > 1) {
        const dropzoneElement = this.$refs.multipleDropzone.$el;
        const messageElement = dropzoneElement.querySelector('.dz-message');
        if (messageElement) {
          messageElement.innerText = `Количество загруженных файлов: ${ this.uploadedFiles.length }`;
        }
      }

      if (this.uploadedFiles.length === 1) {
        const dropzoneElement = this.$refs.multipleDropzone.$el;
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
    
    handleCroppedImage(croppedFile) {
      if (!croppedFile) {
        this.$message.error('Не удалось обрезать изображение');
        return;
      }
      
      console.log('Обрезанный файл получен:', croppedFile);
      
      // Создаем URL для превью
      this.croppedImageUrl = URL.createObjectURL(croppedFile);
      this.croppedFileName = croppedFile.name;
      
      // Добавляем обрезанный файл в uploadedFiles
      this.uploadedFiles = [croppedFile];
      
      this.cropperModalVisible = false;
      this.imageForCropping = null;
    },
    
    handleCropCancel() {
      console.log('Обрезка отменена');
      this.cropperModalVisible = false;
      this.imageForCropping = null;
      
      // Если отменили обрезку и нет обрезанного изображения, показываем дропзон
      if (!this.croppedImageUrl && this.$refs.singleDropzone) {
        const dropzoneElement = this.$refs.singleDropzone.$el;
        const messageElement = dropzoneElement.querySelector('.dz-message');
        if (messageElement) {
          messageElement.innerText = 'Перетащите файл сюда или нажмите для выбора';
        }
      }
    },
    
    compressImageForBatch(file, quality = 0.8, maxSizeMB = 1) {
      return new Promise((resolve, reject) => {
        const maxSize = maxSizeMB * 1024 * 1024; // 1 MB в байтах
        
        // Если файл не изображение или уже меньше maxSize, возвращаем его
        if (!file.type.startsWith('image/') || file.size <= maxSize) {
          resolve(file);
          return;
        }
        
        const img = new Image();
        const url = URL.createObjectURL(file);
        
        img.onload = () => {
          URL.revokeObjectURL(url);
          
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');
          
          // Сохраняем оригинальные пропорции
          const originalWidth = img.width;
          const originalHeight = img.height;
          
          // Вычисляем новые размеры, сохраняя пропорции
          let newWidth = originalWidth;
          let newHeight = originalHeight;
          
          // Если изображение слишком большое, уменьшаем его
          const maxDimension = 2000; // Максимальный размер стороны
          if (originalWidth > maxDimension || originalHeight > maxDimension) {
            const ratio = Math.min(maxDimension / originalWidth, maxDimension / originalHeight);
            newWidth = Math.floor(originalWidth * ratio);
            newHeight = Math.floor(originalHeight * ratio);
          }
          
          canvas.width = newWidth;
          canvas.height = newHeight;
          
          // Отрисовка изображения на canvas
          ctx.drawImage(img, 0, 0, newWidth, newHeight);
          
          // Сжатие изображения
          canvas.toBlob((compressedBlob) => {
            if (compressedBlob.size <= maxSize) {
              const compressedFile = new File(
                [compressedBlob],
                file.name,
                { type: 'image/jpeg' }
              );
              resolve(compressedFile);
            } else {
              // Рекурсивное сжатие с уменьшением качества
              if (quality > 0.1) {
                const newQuality = quality - 0.1;
                this.compressImageForBatch(file, newQuality, maxSizeMB)
                  .then(resolve)
                  .catch(reject);
              } else {
                // Если не удалось сжать до нужного размера, возвращаем максимально сжатое
                const compressedFile = new File(
                  [compressedBlob],
                  file.name,
                  { type: 'image/jpeg' }
                );
                resolve(compressedFile);
              }
            }
          }, 'image/jpeg', quality);
        };
        
        img.onerror = () => {
          URL.revokeObjectURL(url);
          console.warn('Ошибка загрузки изображения для сжатия, возвращаем исходный файл');
          resolve(file); // В случае ошибки возвращаем исходный файл
        };
        
        img.src = url;
      });
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
      
      // Сжимаем файлы, если они больше 1 МБ
      const compressionPromises = this.uploadedFiles.map(file => {
        return this.compressImageForBatch(file, 0.8, 1);
      });
      
      Promise.all(compressionPromises)
        .then((compressedFiles) => {
          console.log('Файлы сжаты:', compressedFiles);
          
          return this.predictListData({
            selectedFiles: compressedFiles,
            patient: this.formData.patient,
            description: this.formData.description
          });
        })
        .then(() => {
          this.$message.success('Данные успешно отправлены и обработаны!');
          this.$emit('refresh');
          this.closeDownloadModal(); // Закрываем после успешной отправки
        })
        .catch(error => {
          console.error('Ошибка предсказания:', error);
          this.$message.error('Ошибка при выполнении предсказания: ' + (error.message || ''));
          this.loading = false;
        })
        .finally(() => {
          this.loading = false;
        });
        
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
          this.closeDownloadModal(); // Закрываем после успешной отправки
        })
        .catch(error => {
          console.error('Ошибка предсказания:', error);
          this.$message.error('Ошибка при выполнении предсказания: ' + (error.message || ''));
          this.loading = false; // Сбрасываем loading, но не закрываем модальное окно
        })
         .finally(() => {
          this.loading = false;
        });
    },
    
    closeDownloadModal () {
      this.isDownloadModalVisible = false;
      this.isDownloadImagesModalVisible = false;
      this.uploadedFiles = [];
      this.formData = {
        patient: '',
        description: '',
      };
      // Сбрасываем также обрезанное изображение
      this.croppedImageUrl = null;
      this.croppedFileName = '';
      
      if (this.$refs.singleDropzone) {
        this.$refs.singleDropzone.removeAllFiles();
      }
      if (this.$refs.multipleDropzone) {
        this.$refs.multipleDropzone.removeAllFiles();
      }
    },
    
    openModal (row) {
      this.selectedRow = {
        ...row,
      };
    },
    
    closeModal () {
      this.selectedRow = null;
    },
    
    openEditModal () {
      this.isEditModalVisible = true;
      this.editForm.id = this.selectedRow.id;
      this.editForm.description = this.selectedRow.description;
      this.editForm.diagnosis = this.selectedRow.diagnosis;

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

<!-- Глобальные стили для таблицы (без scoped) -->
<style lang="less">
/* Глобальные стили для таблицы анализа */
.analysis-table {
  width: 100% !important;
  
  &--wide {
    min-width: 1200px;
    
    .el-table__header-wrapper,
    .el-table__body-wrapper {
      table {
        width: 100% !important;
      }
    }
  }
  
  /* Увеличение шрифта заголовков */
  .el-table__header {
    th {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      padding: 16px 10px;
      background-color: #f5f7fa;
      
      .cell {
        line-height: 1.4;
        white-space: normal;
        word-break: break-word;
      }
    }
  }
  
  /* Стили для ячеек */
  .el-table__body {
    td {
      padding: 12px 10px;
      
      .cell {
        line-height: 1.4;
      }
    }
  }
  
  /* Фиксированные ширины колонок */
  &__column {
    &--author,
    &--patient {
      min-width: 150px !important;
      max-width: 200px !important;
    }
    
    &--image {
      width: 140px !important;
      min-width: 140px !important;
      max-width: 140px !important;
    }
    
    &--date {
      width: 220px !important;
      min-width: 220px !important;
      max-width: 220px !important;
    }
    
    &--actions {
      width: 180px !important;
      min-width: 180px !important;
      max-width: 180px !important;
    }
  }
  
  /* Стили для состояния "нет данных" */
  .el-table__empty-block {
    width: 100% !important;
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* Стили для удаленных строк (глобальные, так как используются классы из Element UI) */
.deleted-row {
  background-color: #fafafa !important;
  
  td {
    color: #999 !important;
  }
  
  &:hover > td {
    background-color: #f5f5f5 !important;
  }
}

/* Стили для превью изображений в таблице */
.table-container__table--preview-image {
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
</style>

<!-- Scoped стили только для компонента -->
<style scoped lang="less">
.modal-content {
  &__container {
    display: flex;
    flex-direction: column;
    max-height: 70vh;
    overflow: hidden;
  }
}

.modal-image-section {
  flex-shrink: 0;
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 20px;
  
  .modal-image {
    max-width: 100%;
    max-height: 40vh;
    object-fit: contain;
    border-radius: 4px;
    border: 1px solid #dcdfe6;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }
}

.modal-text-section {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
  padding-right: 5px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #c0c4cc;
    border-radius: 3px;
    
    &:hover {
      background: #909399;
    }
  }
}

// Стили для полей внутри модального окна
.modal-probabilities,
.modal-fields {
  width: 100%;
}

.modal-probabilities {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

// Улучшенные стили для полей
.field {
  margin-bottom: 12px;
  font-size: 14px;
  color: #333;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  line-height: 1.4;
  
  .field-label {
    font-weight: 600;
    margin-right: 8px;
    display: inline-block;
    min-width: 160px;
    color: #606266;
    flex-shrink: 0;
  }
  
  .field-value {
    color: #303133;
    flex: 1;
    word-break: break-word;
    overflow-wrap: break-word;
    
    &.description-text {
      max-height: 100px;
      overflow-y: auto;
      padding: 8px;
      background-color: #f8f9fa;
      border-radius: 4px;
      border: 1px solid #e9ecef;
    }
  }
  
  &:last-child {
    margin-bottom: 0;
  }
}

.table-container__result-check {
  color: #67c23a;
  font-size: 16px;
  margin-left: 8px;
  vertical-align: middle;
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
  margin: 0;
  width: 100%;
  overflow-x: auto;

  &__content {
    padding: 0;
  }

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
    padding: 20px 20px 0;
    flex-wrap: wrap;
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
  width: 100%;
  
  .empty-hint {
    color: #909399;
    font-size: 14px;
    margin-top: 8px;
  }
}

// Стили для превью обрезанного изображения
.cropped-image-preview {
  border: 2px dashed #409eff;
  border-radius: 8px;
  padding: 10px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
  
  &:hover {
    border-color: #66b1ff;
  }
  
  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px solid #ebeef5;
    
    span {
      font-weight: 500;
      color: #409eff;
    }
    
    .el-button {
      padding: 5px;
    }
  }
  
  .cropped-preview-img {
    max-width: 100%;
    max-height: 200px;
    object-fit: contain;
    border-radius: 4px;
    border: 1px solid #dcdfe6;
  }
  
  .preview-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    padding-top: 5px;
    border-top: 1px solid #ebeef5;
    
    .file-info {
      font-size: 12px;
      color: #909399;
      max-width: 70%;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .el-button {
      padding: 5px;
    }
  }
}
</style>
