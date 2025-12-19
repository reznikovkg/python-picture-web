<template>
  <div class="user-form">
    <ElForm 
      :model="form" 
      :rules="rules" 
      ref="userForm" 
      label-width="120px"
      label-position="left"
      class="user-management-form"
    >
      <ElFormItem label="Логин" prop="login" class="user-form-item">
        <ElInput 
          v-model="form.login" 
          placeholder="Введите логин пользователя"
          :maxlength="32"
          show-word-limit
          class="user-form-input"
        />
      </ElFormItem>

      <ElFormItem 
        label="Пароль" 
        prop="password"
        :required="!isEditing"
        class="user-form-item"
      >
        <ElInput 
          v-model="form.password" 
          type="password"
          :placeholder="isEditing ? 'Оставьте пустым, если не нужно менять' : 'Введите пароль'"
          :maxlength="32"
          show-word-limit
          class="user-form-input"
        />
      </ElFormItem>

      <ElFormItem label="Email" prop="email" class="user-form-item">
        <ElInput 
          v-model="form.email" 
          type="email"
          placeholder="Введите email пользователя"
          :maxlength="254"
          class="user-form-input"
        />
      </ElFormItem>

      <ElFormItem label="Роль" prop="role" class="user-form-item">
        <ElSelect 
          v-model="form.role" 
          placeholder="Выберите роль"
          class="user-form-select"
        >
          <ElOption 
            label="Модератор" 
            value="moderator" 
          />
          <ElOption 
            label="Пользователь" 
            value="regular" 
          />
        </ElSelect>
        <div class="role-description">
          <small v-if="form.role === 'moderator'">
            Модератор видит все анализы, но не может управлять пользователями
          </small>
          <small v-if="form.role === 'regular'">
            Обычный пользователь видит только свои анализы
          </small>
        </div>
      </ElFormItem>

      <ElFormItem label="Статус" class="user-form-item">
        <ElSwitch
          v-model="form.authorization"
          active-text="Активен"
          inactive-text="Заблокирован"
          active-color="#13ce66"
          inactive-color="#ff4949"
          class="user-form-switch"
        />
        <div class="status-description">
          <small>
            {{ form.authorization ? 'Пользователь может войти в систему' : 'Пользователь заблокирован и не может войти' }}
          </small>
        </div>
      </ElFormItem>

      <ElFormItem class="form-actions user-form-actions">
        <ElButton @click="handleCancel" class="user-form-button user-form-button--cancel">
          Отмена
        </ElButton>
        <ElButton 
          type="primary" 
          @click="handleSubmit"
          :loading="loading"
          class="user-form-button user-form-button--submit"
        >
          {{ isEditing ? 'Сохранить' : 'Создать' }}
        </ElButton>
      </ElFormItem>
    </ElForm>
  </div>
</template>

<script>
export default {
  name: 'UserForm',
  props: {
    user: {
      type: Object,
      default: null
    },
    isEditing: {
      type: Boolean,
      default: false
    }
  },
  data() {
    // валидация пароля (обязательна только при создании)
    const validatePassword = (rule, value, callback) => {
      if (!this.isEditing && !value) {
        callback(new Error('Пароль обязателен'))
      } else if (value && value.length < 3) {
        callback(new Error('Пароль должен содержать минимум 3 символа'))
      } else {
        callback()
      }
    }

    // Валидация email
    const validateEmail = (rule, value, callback) => {
      if (value && !/.+@.+\..+/.test(value)) {
        callback(new Error('Введите корректный email адрес'))
      } else {
        callback()
      }
    }

    return {
      loading: false,
      form: {
        login: '',
        password: '',
        email: '',
        role: 'regular',
        authorization: true
      },
      rules: {
        login: [
          { required: true, message: 'Логин обязателен', trigger: 'blur' },
          { min: 3, max: 32, message: 'Длина логина от 3 до 32 символов', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_]+$/, message: 'Логин может содержать только буквы, цифры и подчеркивания', trigger: 'blur' }
        ],
        password: [
          { validator: validatePassword, trigger: 'blur' }
        ],
        email: [
          { validator: validateEmail, trigger: 'blur' }
        ],
        role: [
          { required: true, message: 'Роль обязательна', trigger: 'change' }
        ]
      }
    }
  },
  watch: {
    user: {
      immediate: true,
      handler(newUser) {
        if (newUser) {
          this.form = {
            login: newUser.login || '',
            password: '', // при редактировании пароль не заполняем по умолчанию
            email: newUser.email || '',
            role: newUser.role || 'regular',
            authorization: newUser.authorization !== false // по умолчанию true
          }
        } else {
          // сброс формы для создания
          this.form = {
            login: '',
            password: '',
            email: '',
            role: 'regular',
            authorization: true
          }
        }
      }
    }
  },
  methods: {
    handleSubmit() {
      this.$refs.userForm.validate((valid) => {
        if (valid) {
          this.submitForm()
        } else {
          this.$message.error('Пожалуйста, исправьте ошибки в форме')
          return false
        }
      })
    },

    submitForm() {
      this.loading = true
      
      // подготовка данных для отправки
      const formData = { ...this.form }
      
      // если при редактировании пароль не указан, не отправить его
      if (this.isEditing && !formData.password) {
        delete formData.password
      }

      // эмитация события с данными формы и коллбэком для завершения загрузки
      this.$emit('submit', formData, () => {
        this.loading = false
      })
    },

    handleCancel() {
      this.$refs.userForm.clearValidate()
      this.$emit('cancel')
    },

    // метод для сброса формы извне
    resetForm() {
      this.$refs.userForm.resetFields()
    }
  }
}
</script>


<!-- Глобальные стили для элементов Element UI -->
<style lang="less">
/* Стили для формы управления пользователями */
.user-management-form {
  .user-form-item {
    .el-form-item__label {
      white-space: normal;
      word-break: break-word;
      line-height: 1.4;
      padding-bottom: 8px;
    }
  }
  
  .user-form-input,
  .user-form-select {
    width: 100%;
  }
  
  .user-form-switch {
    margin-right: 10px;
  }
  
  .user-form-actions {
    .user-form-button {
      min-width: 100px;
      
      &--submit {
        &.is-loading {
          opacity: 0.7;
        }
      }
    }
  }
}
</style>

<!-- Попытка избавиться от deep -->
<!-- Scoped стили (только для компонента) -->
<style scoped lang="less">
.user-form {
  padding: 10px 0;
}

.role-description,
.status-description {
  margin-top: 8px;
  
  small {
    color: #909399;
    font-style: italic;
    line-height: 1.4;
  }
}

.form-actions {
  margin-top: 24px;
  text-align: right;
  
  .el-form-item__content {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}
</style>
