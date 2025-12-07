<template>
  <ElDialog
    :title="getTitle"
    :visible="visible"
    width="500px"
    :before-close="handleClose"
    class="delete-confirmation-dialog"
  >
    <div class="delete-confirmation-modal">
      <div class="modal-content">
        <div class="warning-icon">
          <i class="el-icon-warning"></i>
        </div>
        
        <div class="message">
          <p class="confirmation-text">{{ getMessage }}</p>
          
          <!-- Информация о типе удаления для администраторов/модераторов -->
          <div v-if="isBulkDelete && showAdvancedOptions" class="delete-type-info">
            <div v-if="showFilter === 'all'" class="filter-description">
              <ElAlert
                :title="getAllFilterDescription"
                type="info"
                :closable="false"
                show-icon
                class="delete-confirmation-alert"
              />
            </div>
            <div v-else-if="showFilter === 'active'" class="filter-description">
              <ElAlert
                title="Будут удалены все активные записи"
                type="info"
                :closable="false"
                show-icon
                class="delete-confirmation-alert"
              />
            </div>
            <div v-else-if="showFilter === 'deleted'" class="filter-description">
              <ElAlert
                title="Будут удалены все записи, помеченные как удалённые"
                type="warning"
                :closable="false"
                show-icon
                class="delete-confirmation-alert"
              />
            </div>
          </div>
          
          <!-- Дополнительная информация для администраторов/модераторов при удалении одной записи -->
          <div v-if="!isBulkDelete && showAdvancedOptions" class="advanced-info">
            <ElAlert
              v-if="item && item.is_deleted"
              title="Этот анализ уже помечен как удаленный"
              type="warning"
              :closable="false"
              show-icon
              class="delete-confirmation-alert"
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
          class="delete-confirmation-button delete-confirmation-button--cancel"
        >
          Отмена
        </ElButton>
        
        <!-- Кнопки для обычных пользователей -->
        <template v-if="!showAdvancedOptions">
          <ElButton 
            type="danger" 
            @click="handleConfirm('soft')"
            :loading="loading"
            class="delete-confirmation-button delete-confirmation-button--delete"
          >
            Да, удалить
          </ElButton>
        </template>
        
        <!-- Кнопки для администраторов/модераторов -->
        <template v-else>
          <!-- Массовое удаление -->
          <div v-if="isBulkDelete" class="bulk-delete-buttons">
            <!-- Для фильтра 'deleted' только одна кнопка - полное удаление -->
            <div v-if="showFilter === 'deleted'" class="button-with-hint">
              <ElButton 
                type="danger" 
                @click="handleConfirm('permanent')"
                :loading="loading && deleteType === 'permanent'"
                :disabled="loading && deleteType !== 'permanent'"
                class="delete-confirmation-button delete-confirmation-button--permanent"
              >
                Удалить навсегда
              </ElButton>
              <div class="button-hint">
                Удалённые записи будут<br>
                полностью удалены из базы
              </div>
            </div>
            
            <!-- Для фильтров 'all' и 'active' две кнопки -->
            <template v-else>
              <div class="button-with-hint">
                <ElButton 
                  type="warning" 
                  @click="handleConfirm('soft')"
                  :loading="loading && deleteType === 'soft'"
                  :disabled="loading && deleteType !== 'soft'"
                  class="delete-confirmation-button delete-confirmation-button--soft"
                >
                  Удалить
                </ElButton>
                <div class="button-hint">
                  Активные записи будут<br>
                  скрыты и останутся в базе
                </div>
              </div>
              
              <div class="button-with-hint">
                <ElButton 
                  type="danger" 
                  @click="handleConfirm('permanent')"
                  :loading="loading && deleteType === 'permanent'"
                  :disabled="loading && deleteType !== 'permanent'"
                  class="delete-confirmation-button delete-confirmation-button--permanent"
                >
                  Удалить навсегда
                </ElButton>
                <div class="button-hint">
                  <template v-if="showFilter === 'all'">
                    Все записи будут<br>
                    полностью удалены
                  </template>
                  <template v-else>
                    Активные записи будут<br>
                    полностью удалены
                  </template>
                </div>
              </div>
            </template>
          </div>
          
          <!-- Удаление одной записи -->
          <div v-else class="single-delete-buttons">
            <div class="button-with-hint">
              <ElButton 
                type="warning" 
                @click="handleConfirm('soft')"
                :loading="loading && deleteType === 'soft'"
                :disabled="loading && deleteType !== 'soft'"
                class="delete-confirmation-button delete-confirmation-button--soft"
              >
                Удалить
              </ElButton>
              <div class="button-hint">
                Запись будет скрыта,<br>
                но останется в базе
              </div>
            </div>
            
            <div class="button-with-hint">
              <ElButton 
                type="danger" 
                @click="handleConfirm('permanent')"
                :loading="loading && deleteType === 'permanent'"
                :disabled="loading && deleteType !== 'permanent'"
                class="delete-confirmation-button delete-confirmation-button--permanent"
              >
                Удалить навсегда
              </ElButton>
              <div class="button-hint">
                Запись и изображение<br>
                будут полностью удалены
              </div>
            </div>
          </div>
        </template>
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
    },
    // Фильтр для массового удаления
    showFilter: {
      type: String,
      default: 'active' // all, active, deleted
    }
  },
  data() {
    return {
      deleteType: 'soft' // 'soft' или 'permanent'
    }
  },
  computed: {
    showAdvancedOptions() {
      // Для массового удаления показываем расширенные опции только админам/модераторам
      if (this.isBulkDelete) {
        return this.userRole === 'admin' || this.userRole === 'moderator'
      }
      
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
        const filterLabels = {
          'all': 'все записи',
          'active': 'все активные записи',
          'deleted': 'все удалённые записи'
        }
        
        const filterLabel = filterLabels[this.showFilter] || 'записи'
        
        if (this.userRole === 'regular') {
          return `Вы уверены, что хотите удалить все ваши активные записи (${this.deleteCount} шт.)?`
        }
        
        return `Вы уверены, что хотите удалить ${filterLabel} (${this.deleteCount} шт.)?`
      }
      
      if (this.item) {
        const baseMessage = `Вы уверены, что хотите удалить анализ пациента "${this.item.patient}"?`
        
        if (this.item.is_deleted && this.showAdvancedOptions) {
          return `${baseMessage} Этот анализ уже помечен как удаленный.`
        }
        
        return baseMessage
      }
      
      return 'Вы уверены, что хотите удалить этот элемент?'
    },
    
    getAllFilterDescription() {
      if (this.deleteType === 'soft') {
        return 'Будут удалены (скрыты) только активные записи. Уже удалённые записи останутся в базе.'
      } else {
        return 'Будут полностью удалены все записи: активные и удалённые.'
      }
    }
  },
  watch: {
    visible(newVal) {
      if (newVal) {
        // сброс состояния при открытии
        this.deleteType = 'soft'
      }
    },
    
    showFilter(newFilter) {
      // При изменении фильтра сбрасываем тип удаления
      if (newFilter === 'deleted') {
        this.deleteType = 'permanent'
      } else {
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
      
      // Для массового удаления с фильтром 'deleted' всегда использется permanent
      if (this.isBulkDelete && this.showFilter === 'deleted') {
        this.$emit('confirm', {
          type: 'permanent',
          item: this.item,
          isBulk: this.isBulkDelete
        })
      } else {
        this.$emit('confirm', {
          type: finalType,
          item: this.item,
          isBulk: this.isBulkDelete
        })
      }
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

<!-- Попытка избавиться от deep -->
<!-- Глобальные стили для элементов Element UI -->
<style lang="less">
/* Стили для кнопок в диалоге подтверждения удаления */
.delete-confirmation-button {
  min-width: 100px;
  
  &.is-loading {
    opacity: 0.7;
  }
  
  &--cancel {
    /* Дополнительные стили для кнопки отмены */
  }
  
  &--delete {
    /* Дополнительные стили для кнопки удаления */
  }
  
  &--soft {
    min-width: 140px;
  }
  
  &--permanent {
    min-width: 140px;
  }
}

/* Стили для уведомлений в диалоге подтверждения удаления */
.delete-confirmation-alert {
  margin-bottom: 8px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .el-alert__title {
    font-size: 13px;
    line-height: 1.3;
  }
}
</style>

<!-- Scoped стили (только для компонента) -->
<style scoped lang="less">
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
      
      .delete-type-info {
        margin-top: 12px;
        
        .filter-description {
          margin-bottom: 8px;
          
          &:last-child {
            margin-bottom: 0;
          }
        }
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
    
    .bulk-delete-buttons,
    .single-delete-buttons {
      display: flex;
      gap: 12px;
      
      .button-with-hint {
        display: flex;
        flex-direction: column;
        align-items: center;
        
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
</style>
