<template>
  <ElDialog
    :title="title"
    :visible="visible"
    width="800px"
    :before-close="handleClose"
    class="image-cropper-modal"
  >
    <div class="cropper-container">
      <div v-if="!imageSrc" class="no-image">
        <i class="el-icon-picture-outline"></i>
        <p>Изображение не загружено</p>
      </div>
      
      <div v-else class="cropper-wrapper">
        <vue-cropper
          ref="cropper"
          :src="imageSrc"
          :aspect-ratio="1"
          :view-mode="2"
          :background="false"
          :auto-crop-area="0.8"
          :min-container-width="500"
          :min-container-height="400"
          :min-crop-box-width="100"
          :min-crop-box-height="100"
          :guides="true"
          :drag-mode="'move'"
          :crop-box-movable="true"
          :crop-box-resizable="true"
          :toggle-drag-mode-on-dblclick="true"
          class="cropper"
        />
        
        <div class="controls">
          <div class="control-group">
            <ElButton 
              icon="el-icon-refresh-left" 
              @click="rotate(-90)"
              title="Повернуть налево"
            />
            <ElButton 
              icon="el-icon-refresh-right" 
              @click="rotate(90)"
              title="Повернуть направо"
            />
            <ElButton 
              icon="el-icon-zoom-in" 
              @click="zoom(0.1)"
              title="Увеличить"
            />
            <ElButton 
              icon="el-icon-zoom-out" 
              @click="zoom(-0.1)"
              title="Уменьшить"
            />
            <ElButton 
              icon="el-icon-crop" 
              @click="resetCrop"
              title="Сбросить обрезку"
            />
          </div>
          
          <div class="preview">
            <div class="preview-label">Предпросмотр (1:1):</div>
            <div class="preview-container">
              <div 
                class="preview-image"
                :style="{
                  width: '150px',
                  height: '150px',
                  overflow: 'hidden',
                  borderRadius: '4px'
                }"
              >
                <img 
                  v-if="previewUrl" 
                  :src="previewUrl" 
                  alt="Предпросмотр"
                  style="width: 100%; height: 100%; object-fit: contain"
                />
              </div>
            </div>
          </div>
        </div>
        
        <div class="info">
          <ElAlert
            :title="sizeInfo"
            type="info"
            :closable="false"
            show-icon
            class="size-alert"
          />
          <div v-if="compressionMessage" class="compression-info">
            <ElAlert
              :title="compressionMessage"
              type="warning"
              :closable="false"
              show-icon
            />
          </div>
        </div>
      </div>
    </div>
    
    <div slot="footer" class="modal-footer">
      <ElButton 
        @click="handleCancel"
        :disabled="loading"
      >
        Отмена
      </ElButton>
      <ElButton 
        type="primary" 
        @click="handleConfirm"
        :loading="loading"
        :disabled="!imageSrc"
      >
        {{ confirmButtonText }}
      </ElButton>
    </div>
  </ElDialog>
</template>

<script>
import VueCropper from 'vue-cropperjs'
import 'cropperjs/dist/cropper.css'

export default {
  name: 'ImageCropperModal',
  components: {
    VueCropper
  },
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
    },
    confirmButtonText: {
      type: String,
      default: 'Применить обрезку'
    },
    maxSizeMB: {
      type: Number,
      default: 1
    }
  },
  data() {
    return {
      imageSrc: null,
      previewUrl: null,
      loading: false,
      originalSize: 0,
      compressed: false
    }
  },
  computed: {
    sizeInfo() {
      if (!this.imageFile) return ''
      const sizeMB = (this.originalSize / (1024 * 1024)).toFixed(2)
      return `Исходный размер: ${sizeMB} MB. Обрезанное изображение будет квадратным (1:1)`
    },
    
    compressionMessage() {
      if (!this.compressed) return ''
      return `Изображение было сжато с ${(this.originalSize / (1024 * 1024)).toFixed(2)} MB до 1 MB`
    }
  },
  watch: {
    visible(newVal) {
      if (newVal && this.imageFile) {
        this.loadImage()
      } else {
        this.cleanup()
      }
    },
    
    imageFile(newFile) {
      if (newFile && this.visible) {
        this.loadImage()
      }
    }
  },
  methods: {
    loadImage() {
      this.cleanup()
      
      if (!this.imageFile) {
        this.imageSrc = null
        return
      }
      
      this.originalSize = this.imageFile.size
      this.compressed = false
      
      const reader = new FileReader()
      reader.onload = (e) => {
        this.imageSrc = e.target.result
        
        // Если файл больше 1MB, сразу сжимаем
        if (this.imageFile.size > this.maxSizeMB * 1024 * 1024) {
          this.compressImage().then(compressedSrc => {
            this.imageSrc = compressedSrc
            this.compressed = true
            this.updatePreview()
          })
        } else {
          this.$nextTick(() => {
            this.updatePreview()
          })
        }
      }
      reader.readAsDataURL(this.imageFile)
    },
    
    compressImage() {
      return new Promise((resolve) => {
        const img = new Image()
        img.onload = () => {
          const canvas = document.createElement('canvas')
          const ctx = canvas.getContext('2d')
          
          // Рассчитываем новые размеры с сохранением пропорций
          let width = img.width
          let height = img.height
          const maxDimension = 1200 // Максимальный размер по большей стороне
          
          if (width > height && width > maxDimension) {
            height = Math.round((height * maxDimension) / width)
            width = maxDimension
          } else if (height > maxDimension) {
            width = Math.round((width * maxDimension) / height)
            height = maxDimension
          }
          
          canvas.width = width
          canvas.height = height
          
          ctx.drawImage(img, 0, 0, width, height)
          
          // Сжимаем с качеством 0.8
          const compressedDataUrl = canvas.toDataURL('image/jpeg', 0.8)
          resolve(compressedDataUrl)
        }
        img.src = this.imageSrc
      })
    },
    
    updatePreview() {
      if (!this.$refs.cropper) return
      
      const cropper = this.$refs.cropper
      const canvas = cropper.getCroppedCanvas({
        width: 150,
        height: 150,
        imageSmoothingEnabled: true,
        imageSmoothingQuality: 'high'
      })
      
      if (canvas) {
        this.previewUrl = canvas.toDataURL('image/jpeg', 0.9)
      }
    },
    
    rotate(degrees) {
      if (this.$refs.cropper) {
        this.$refs.cropper.rotate(degrees)
        this.updatePreview()
      }
    },
    
    zoom(ratio) {
      if (this.$refs.cropper) {
        this.$refs.cropper.relativeZoom(ratio)
        this.updatePreview()
      }
    },
    
    resetCrop() {
      if (this.$refs.cropper) {
        this.$refs.cropper.reset()
        this.updatePreview()
      }
    },
    
    async getCroppedImage() {
      if (!this.$refs.cropper) {
        throw new Error('Cropper не инициализирован')
      }
      
      return new Promise((resolve, reject) => {
        const cropper = this.$refs.cropper
        
        // Получаем обрезанное изображение
        const canvas = cropper.getCroppedCanvas({
          width: 512,
          height: 512,
          imageSmoothingEnabled: true,
          imageSmoothingQuality: 'high'
        })
        
        if (!canvas) {
          reject(new Error('Не удалось получить обрезанное изображение'))
          return
        }
        
        // Конвертируем canvas в blob
        canvas.toBlob(async (blob) => {
          if (!blob) {
            reject(new Error('Не удалось создать blob'))
            return
          }
          
          // Дополнительное сжатие если размер > 1MB
          let finalBlob = blob
          if (blob.size > this.maxSizeMB * 1024 * 1024) {
            finalBlob = await this.compressBlob(blob)
            this.compressed = true
          }
          
          // Создаем новый файл с префиксом
          const fileName = `cropped_${this.imageFile.name}`
          const croppedFile = new File([finalBlob], fileName, {
            type: 'image/jpeg',
            lastModified: Date.now()
          })
          
          resolve(croppedFile)
        }, 'image/jpeg', 0.9)
      })
    },
    
    compressBlob(blob) {
      return new Promise((resolve) => {
        const img = new Image()
        const url = URL.createObjectURL(blob)
        
        img.onload = () => {
          const canvas = document.createElement('canvas')
          const ctx = canvas.getContext('2d')
          
          // Уменьшаем размер для достижения ~1MB
          let quality = 0.8
          let width = img.width
          let height = img.height
          
          // Рекурсивно сжимаем пока размер > 1MB
          const compress = () => {
            canvas.width = width
            canvas.height = height
            ctx.drawImage(img, 0, 0, width, height)
            
            canvas.toBlob((compressedBlob) => {
              if (compressedBlob.size <= this.maxSizeMB * 1024 * 1024 || quality <= 0.1) {
                URL.revokeObjectURL(url)
                resolve(compressedBlob)
              } else {
                // Уменьшаем качество и размер
                quality *= 0.9
                width = Math.floor(width * 0.9)
                height = Math.floor(height * 0.9)
                compress()
              }
            }, 'image/jpeg', quality)
          }
          
          compress()
        }
        
        img.src = url
      })
    },
    
    handleConfirm() {
      this.loading = true
      
      this.getCroppedImage()
        .then((croppedFile) => {
          this.$emit('confirm', croppedFile)
          this.loading = false
        })
        .catch((error) => {
          console.error('Ошибка обрезки:', error)
          this.$message.error('Ошибка при обрезке изображения')
          this.loading = false
        })
    },
    
    handleCancel() {
      this.$emit('cancel')
    },
    
    handleClose(done) {
      if (this.loading) return
      this.$emit('cancel')
      if (done) done()
    },
    
    cleanup() {
      if (this.imageSrc && this.imageSrc.startsWith('data:')) {
        // Освобождаем ресурсы
        URL.revokeObjectURL(this.imageSrc)
      }
      this.imageSrc = null
      this.previewUrl = null
      this.compressed = false
    }
  },
  
  beforeDestroy() {
    this.cleanup()
  }
}
</script>

<style scoped lang="less">
.cropper-container {
  min-height: 500px;
  display: flex;
  flex-direction: column;
  
  .no-image {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    color: #909399;
    
    i {
      font-size: 64px;
      margin-bottom: 20px;
    }
    
    p {
      font-size: 16px;
    }
  }
  
  .cropper-wrapper {
    display: flex;
    flex-direction: column;
    gap: 20px;
    
    .cropper {
      width: 100%;
      height: 400px;
      background: #f5f7fa;
      border-radius: 4px;
      overflow: hidden;
    }
    
    .controls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px;
      background: #f9f9f9;
      border-radius: 4px;
      
      .control-group {
        display: flex;
        gap: 10px;
        
        .el-button {
          width: 40px;
          height: 40px;
          padding: 0;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
      
      .preview {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        
        .preview-label {
          font-size: 12px;
          color: #606266;
        }
        
        .preview-container {
          border: 2px dashed #dcdfe6;
          border-radius: 6px;
          padding: 4px;
          background: white;
        }
      }
    }
    
    .info {
      margin-top: 10px;
      
      .size-alert {
        margin-bottom: 10px;
      }
    }
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #eaeaea;
}
</style>