<template>
  <ElDialog
    :title="getTitle"
    :visible="visible"
    width="500px"
    :before-close="handleClose"
  >
    <div class="delete-confirmation-modal">
      <div class="modal-content">
        <div class="warning-icon">
          <i class="el-icon-warning"></i>
        </div>
        
        <div class="message">
          <p class="confirmation-text">{{ getMessage }}</p>
          
          <!-- Дополнительная информация для администраторов/модераторов -->
          <div v-if="showAdvancedOptions" class="advanced-info">
            <ElAlert
              v-if="item && item.is_deleted"
              title="Этот анализ уже помечен как удаленный"
              type="warning"
              :closable="false"
              show-icon
            />
            
            <div class="file-info" v-if="item && item.image">
              <strong>Файл изображения:</strong> 
              <span class="file-name">{{ getFileName(item.image) }}</span>
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
        
        <!-- Для обычных пользователей - одна кнопка удаления -->
        <ElButton 
          v-if="!showAdvancedOptions"
          type="danger" 
          @click="handleConfirm('soft')"
          :loading="loading"
        >
          Да, удалить
        </ElButton>
        
        <!-- Для администраторов/модераторов - две кнопки удаления -->
        <div v-else class="admin-buttons">
          <div class="button-with-hint">
            <ElButton 
              type="warning" 
              @click="handleConfirm('soft')"
              :loading="loading && deleteType === 'soft'"
              :disabled="loading && deleteType !== 'soft'"
              class="delete-button"
            >
              Удалить
            </ElButton>
            <div class="button-hint">
              Анализ будет скрыт,<br>
              но останется в базе
            </div>
          </div>
          
          <div class="button-with-hint">
            <ElButton 
              type="danger" 
              @click="handleConfirm('permanent')"
              :loading="loading && deleteType === 'permanent'"
              :disabled="loading && deleteType !== 'permanent'"
              class="delete-permanent-button"
            >
              Удалить навсегда
            </ElButton>
            <div class="button-hint">
              Анализ и изображение<br>
              будут полностью удалены
            </div>
          </div>
        </div>
      </div>
    </div>
  </ElDialog>
</template>

<script>
export default {
  name: 'DeleteConfirmationModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    item: {
      type: Object,
      default: null
    },
    userRole: {
      type: String,
      default: 'regular'
    },
    loading: {
      type: Boolean,
      default: false
    },
    // Для массового удаления
    isBulkDelete: {
      type: Boolean,
      default: false
    },
    deleteCount: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      deleteType: 'soft' // 'soft' или 'permanent'
    }
  },
  computed: {
    showAdvancedOptions() {
      return this.userRole === 'admin' || this.userRole === 'moderator'
    },
    
    getTitle() {
      if (this.isBulkDelete) {
        return `Удаление анализов (${this.deleteCount})`
      }
      
      if (this.item && this.item.is_deleted && this.showAdvancedOptions) {
        return 'Удаление анализа'
      }
      
      return this.showAdvancedOptions ? 'Удаление анализа' : 'Подтверждение удаления'
    },
    
    getMessage() {
      if (this.isBulkDelete) {
        return `Вы уверены, что хотите удалить ${this.deleteCount} анализов?`
      }
      
      if (this.item) {
        const baseMessage = `Вы уверены, что хотите удалить анализ пациента "${this.item.patient}"?`
        
        if (this.item.is_deleted && this.showAdvancedOptions) {
          return `${baseMessage} Этот анализ уже помечен как удаленный.`
        }
        
        return baseMessage
      }
      
      return 'Вы уверены, что хотите удалить этот элемент?'
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        // сброс состояния при открытии
        this.deleteType = 'soft'
      }
    }
  },
  methods: {
    getFileName(imageUrl) {
      if (!imageUrl) return 'Неизвестно'
      return imageUrl.split('/').pop() || 'Изображение'
    },
    
    handleConfirm(type) {
      const finalType = type || this.deleteType
      this.$emit('confirm', {
        type: finalType,
        item: this.item,
        isBulk: this.isBulkDelete
      })
    },
    
    handleCancel() {
      this.$emit('cancel')
    },
    
    handleClose(done) {
      if (this.loading) {
        return // не закрывается если идет загрузка
      }
      this.$emit('cancel')
      if (done) {
        done() // конец диалога
      }
    }
  }
}
</script>

<style lang="less" scoped>
.delete-confirmation-modal {
  .modal-content {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    
    .warning-icon {
      font-size: 48px;
      color: #e6a23c;
      line-height: 1;
      flex-shrink: 0;
    }
    
    .message {
      flex: 1;
      word-wrap: break-word;
      word-break: normal;
      overflow-wrap: break-word;
      
      .confirmation-text {
        margin: 0 0 12px 0;
        font-size: 14px;
        line-height: 1.5;
        color: #606266;
        white-space: normal;
      }
      
      .advanced-info {
        margin-top: 12px;
        
        .file-info {
          margin-top: 8px;
          padding: 8px 12px;
          background: #f5f7fa;
          border-radius: 4px;
          font-size: 13px;
          line-height: 1.4;
          white-space: normal;
          
          strong {
            color: #909399;
            margin-right: 5px;
          }
          
          .file-name {
            word-break: break-all;
            white-space: normal;
          }
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
    
    .el-button {
      min-width: 100px;
    }
    
    .admin-buttons {
      display: flex;
      gap: 12px;
      
      .button-with-hint {
        display: flex;
        flex-direction: column;
        align-items: center;
        
        .delete-button,
        .delete-permanent-button {
          min-width: 140px;
        }
        
        .button-hint {
          margin-top: 4px;
          font-size: 11px;
          color: #909399;
          text-align: center;
          max-width: 140px;
          line-height: 1.2;
          white-space: normal;
        }
      }
    }
  }
}

// стили для состояний загрузки
:deep(.el-button) {
  &.is-loading {
    opacity: 0.7;
  }
}
</style>