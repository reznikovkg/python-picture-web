<template>
  <ElDialog
    :title="title"
    :visible="dialogVisible"
    width="800px"
    :before-close="handleBeforeClose"
    class="image-cropper-modal"
  >
    <div class="cropper-container">
      <div class="cropper-wrapper" v-loading="imageLoading">
        <div class="cropper" ref="cropperContainer">
          <img :src="imageSrc" ref="imageElement" alt="Изображение для обрезки" v-if="imageSrc">
          <div v-else class="no-image">
            <p>Загрузка изображения...</p>
          </div>
        </div>
      </div>
      
      <div class="preview-container">
        <h4>Предпросмотр (1x1):</h4>
        <div class="preview-wrapper">
          <div 
            ref="preview"
            class="preview"
          />
        </div>
        <div class="file-info">
          <p v-if="originalFileInfo">
            <span>Исходный файл:</span>
            <span class="file-name-container">
              <span class="file-name" :title="originalFileInfo.name">
                {{ originalFileInfo.name }}
              </span>
              <span class="file-size">
                ({{ formatFileSize(originalFileInfo.size) }})
              </span>
            </span>
          </p>
          <p v-if="croppedFileInfo">
            После обрезки: {{ formatFileSize(croppedFileInfo.size) }}
          </p>
          <ElAlert
            v-if="showCompressionWarning"
            :title="compressionWarningText"
            type="warning"
            :closable="false"
            show-icon
            class="compression-alert"
          />
        </div>
      </div>
    </div>
    
    <div slot="footer" class="modal-footer">
      <ElButton @click="handleCancel">
        Отмена
      </ElButton>
      <ElButton 
        type="primary" 
        @click="handleConfirm"
        :loading="loading"
        :disabled="!cropperInstance || imageLoading"
      >
        Применить
      </ElButton>
    </div>
  </ElDialog>
</template>

<script>
import Cropper from 'cropperjs';
import 'cropperjs/dist/cropper.css';

export default {
  name: 'ImageCropperModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    imageFile: {
      type: File,
      default: null
    },
    title: {
      type: String,
      default: 'Обрезка изображения'
    }
  },
  data() {
    return {
      loading: false,
      imageLoading: false,
      imageSrc: '',
      originalFileInfo: null,
      croppedFileInfo: null,
      showCompressionWarning: false,
      compressionWarningText: '',
      dialogVisible: false,
      cropperInstance: null
    }
  },
  watch: {
    visible: {
      immediate: true,
      handler(newVal) {
        this.dialogVisible = newVal
        if (newVal && this.imageFile) {
          this.$nextTick(() => {
            this.loadImage()
          })
        } else {
          this.reset()
        }
      }
    },
    imageFile: {
      immediate: true,
      handler(newFile) {
        if (newFile && this.visible) {
          this.$nextTick(() => {
            this.loadImage()
          })
        }
      }
    }
  },
  mounted() {
    // Инициализация кроппера
    this.initCropper();
  },
  beforeDestroy() {
    // Уничтожение кроппера при удалении компонента
    this.destroyCropper();
  },
  methods: {
    initCropper() {
      if (this.cropperInstance) {
        this.cropperInstance.destroy();
      }
      
      if (this.$refs.imageElement && this.imageSrc) {
        this.cropperInstance = new Cropper(this.$refs.imageElement, {
          aspectRatio: 1,
          viewMode: 2,
          autoCropArea: 1,
          guides: true,
          background: false,
          rotatable: false,
          ready: () => {
            this.imageLoading = false;
            this.updatePreview();
          },
          crop: () => {
            this.updatePreview();
          }
        });
      }
    },
    
    destroyCropper() {
      if (this.cropperInstance) {
        this.cropperInstance.destroy();
        this.cropperInstance = null;
      }
    },
    
    loadImage() {
      if (!this.imageFile) {
        this.imageSrc = ''
        return
      }

      this.originalFileInfo = {
        name: this.imageFile.name,
        size: this.imageFile.size
      }

      this.imageLoading = true;
      const reader = new FileReader()

      reader.onload = (e) => {
        this.imageSrc = e.target.result
        // сброс информации о обрезанном файле при загрузке нового
        this.croppedFileInfo = null
        this.showCompressionWarning = false
        
        // Переинициализация кроппера с новым изображением
        this.$nextTick(() => {
          this.initCropper();
        });
      }

      reader.onerror = () => {
        this.imageLoading = false;
        this.$message.error('Ошибка загрузки изображения');
      }

      reader.readAsDataURL(this.imageFile)
    },

    updatePreview() {
      if (!this.cropperInstance) return;

      // получение данных обрезки для предпросмотра
      const canvas = this.cropperInstance.getCroppedCanvas({
        width: 200,
        height: 200
      })

      if (!canvas) return

      // очистка предпросмотра
      const preview = this.$refs.preview
      if (preview) {
        preview.innerHTML = ''
        preview.appendChild(canvas)
      }
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },

    compressImage(blob, quality = 0.8, maxSizeMB = 1) {
      return new Promise((resolve, reject) => {
        const maxSize = maxSizeMB * 1024 * 1024 // 1 MB в байтах
        
        // если изображение уже меньше maxSize, возвращаем его
        if (blob.size <= maxSize) {
          resolve(blob)
          return
        }

        const img = new Image()
        const url = URL.createObjectURL(blob)
        
        img.onload = () => {
          URL.revokeObjectURL(url)
          
          const canvas = document.createElement('canvas')
          const ctx = canvas.getContext('2d')
          
          // установка размеров canvas
          canvas.width = img.width
          canvas.height = img.height
          
          // отрисовка изображения на canvas
          ctx.drawImage(img, 0, 0)
          
          // сжатие изображения
          canvas.toBlob((compressedBlob) => {
            if (compressedBlob.size <= maxSize) {
              resolve(compressedBlob)
            } else {
              // рекурсивное сжатие с уменьшением качества
              if (quality > 0.1) {
                const newQuality = quality - 0.1
                this.compressImage(blob, newQuality, maxSizeMB)
                  .then(resolve)
                  .catch(reject)
              } else {
                reject(new Error('Не удалось сжать изображение до требуемого размера'))
              }
            }
          }, 'image/jpeg', quality)
        }
        
        img.onerror = () => {
          URL.revokeObjectURL(url)
          reject(new Error('Ошибка загрузки изображения для сжатия'))
        }
        
        img.src = url
      })
    },

    getCroppedImage() {
      return new Promise((resolve, reject) => {
        if (!this.cropperInstance) {
          reject(new Error('Кроппер не инициализирован'))
          return
        }

        // получение обрезанного canvas
        const canvas = this.cropperInstance.getCroppedCanvas({
          width: 500,
          height: 500
        })

        if (!canvas) {
          reject(new Error('Не удалось получить обрезанное изображение'))
          return
        }

        // конвертация canvas в blob
        canvas.toBlob((blob) => {
          if (!blob) {
            reject(new Error('Не удалось создать изображение'))
            return
          }

          // обновление информации о размере после обрезки
          this.croppedFileInfo = {
            size: blob.size
          }

          // проверка необходимости сжатия (больше 1 МБ)
          if (blob.size > 1024 * 1024) {
            this.showCompressionWarning = true
            this.compressionWarningText = 'Изображение больше 1 МБ. Выполняется сжатие...'
            
            this.compressImage(blob, 0.8, 1)
              .then((compressedBlob) => {
                this.croppedFileInfo.size = compressedBlob.size
                this.compressionWarningText = 'Изображение сжато до ' + this.formatFileSize(compressedBlob.size)
                resolve(compressedBlob)
              })
              .catch((error) => {
                console.warn('Не удалось сжать изображение:', error)
                // если не удалось сжать, возвращаем исходное обрезанное изображение
                resolve(blob)
              })
          } else {
            this.showCompressionWarning = false
            resolve(blob)
          }
        }, 'image/jpeg', 0.95) // начальное качество 95%
      })
    },

    handleConfirm() {
      if (!this.cropperInstance) {
        this.$message.error('Изображение еще не загружено для обрезки');
        return;
      }
      
      this.loading = true
      
      this.getCroppedImage()
        .then((blob) => {
          // создание нового File объекта из blob
          const croppedFile = new File(
            [blob],
            this.generateCroppedFileName(this.imageFile.name),
            { type: 'image/jpeg' }
          )
          
          this.$emit('confirm', croppedFile)
          this.closeDialog()
        })
        .catch((error) => {
          console.error('Ошибка при обрезке изображения:', error)
          this.$message.error('Ошибка при обрезке изображения: ' + error.message)
          this.loading = false
        })
    },

    generateCroppedFileName(originalName) {
      const nameWithoutExt = originalName.replace(/\.[^/.]+$/, "")
      const timestamp = new Date().getTime()
      return `${nameWithoutExt}_cropped_${timestamp}.jpg`
    },

    handleCancel() {
      this.closeDialog()
    },

    handleBeforeClose(done) {
      if (this.loading) {
        return // не закрывается если идет загрузка
      }
      this.closeDialog()
      if (done) {
        done()
      }
    },

    closeDialog() {
      this.$emit('update:visible', false)
      this.$emit('cancel')
      this.reset()
    },

    reset() {
      this.loading = false
      this.imageLoading = false
      this.imageSrc = ''
      this.originalFileInfo = null
      this.croppedFileInfo = null
      this.showCompressionWarning = false
      this.compressionWarningText = ''
      this.dialogVisible = false
      this.destroyCropper()
    }
  }
}
</script>

<style lang="less" scoped>
.cropper-container {
  display: flex;
  gap: 20px;
  min-height: 500px;
  
  .cropper-wrapper {
    flex: 1;
    min-height: 500px;
    
    .cropper {
      width: 100%;
      height: 500px;
      max-height: 500px;
      position: relative;
      
      img {
        max-width: 100%;
        max-height: 100%;
        display: block;
      }
      
      .no-image {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #909399;
      }
    }
  }
  
  .preview-container {
    width: 250px;
    display: flex;
    flex-direction: column;
    
    h4 {
      margin: 0 0 10px 0;
      color: #303133;
    }
    
    .preview-wrapper {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #f5f7fa;
      border-radius: 4px;
      padding: 10px;
      margin-bottom: 15px;
      
      .preview {
        width: 200px;
        height: 200px;
        overflow: hidden;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        
        canvas {
          max-width: 100%;
          max-height: 100%;
        }
      }
    }
    
    .file-info {
      p {
        margin: 5px 0;
        font-size: 12px;
        color: #606266;
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        
        &:last-child {
          margin-bottom: 0;
        }
      }
      
      .file-name-container {
        flex: 1;
        display: flex;
        min-width: 0;
      }
      
      .file-name {
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 200px;
      }
      
      .file-size {
        flex-shrink: 0;
        margin-left: 4px;
      }
    }
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

</style>

<style lang="less">
.image-cropper-modal {
  .el-dialog {
    max-width: 900px;
    
    &__body {
      padding: 20px;
    }
  }
}
</style>
