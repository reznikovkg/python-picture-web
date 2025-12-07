<template>
  <div class="user-management">
    <div class="header">
      <div class="header-left">
        <ElButton 
          icon="el-icon-back" 
          @click="goBack"
          class="back-button user-management-button"
        >
          Назад
        </ElButton>
        <h1>Управление пользователями</h1>
      </div>
      
      <div class="user-info" v-if="currentUser">
        Текущий пользователь: <strong>{{ currentUser.login }}</strong> 
        ({{ getUserRoleLabel(currentUser.role) }})
      </div>
    </div>

    <div class="controls">
      <ElButton 
        type="primary" 
        @click="openCreateModal"
        :disabled="loading"
        class="user-management-button user-management-button--create"
      >
        Добавить пользователя
      </ElButton>
    </div>

    <div class="table-wrapper">
      <div v-loading="loading" class="table-container">
        <ElTable 
          :data="users" 
          class="table-container__table analysis-table analysis-table--wide user-management-table"
          empty-text="Нет пользователей для отображения"
          :row-class-name="getRowClassName"
        >
          <ElTableColumn 
            label="ID" 
            prop="id" 
            width="80"
            class-name="analysis-table__column analysis-table__column--id"
          />
          <ElTableColumn 
            label="Логин" 
            prop="login"
            class-name="analysis-table__column analysis-table__column--login"
          >
            <template #default="{ row }">
              <div class="login-cell">
                <span>{{ row.login }}</span>
                <ElTag 
                  v-if="row.id === currentUserId" 
                  type="info" 
                  size="mini"
                  class="current-user-tag"
                >
                  Вы
                </ElTag>
              </div>
            </template>
          </ElTableColumn>
          <ElTableColumn 
            label="Email" 
            prop="email"
            class-name="analysis-table__column analysis-table__column--email"
          >
            <template #default="{ row }">
              {{ row.email || '-' }}
            </template>
          </ElTableColumn>
          <ElTableColumn 
            label="Роль" 
            prop="role"
            class-name="analysis-table__column analysis-table__column--role"
          >
            <template #default="{ row }">
              <ElTag 
                :type="getRoleTagType(row.role)"
                effect="dark"
                class="role-tag"
              >
                {{ getRoleLabel(row.role) }}
              </ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn 
            label="Статус" 
            prop="authorization"
            width="120"
            class-name="analysis-table__column analysis-table__column--status"
          >
            <template #default="{ row }">
              <ElTag 
                :type="row.authorization ? 'success' : 'danger'"
                effect="light"
                class="status-tag"
              >
                {{ row.authorization ? 'Активен' : 'Заблокирован' }}
              </ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn 
            label="Действия" 
            width="150"
            header-align="center"
            class-name="analysis-table__column analysis-table__column--actions user-management-actions-column"
          >
            <template #default="{ row }">
              <div class="action-buttons user-management-action-buttons">
                <ElButton 
                  size="mini" 
                  type="primary"
                  @click="openEditModal(row)"
                  :disabled="row.id === currentUserId"
                  class="action-button edit-button user-management-action-button"
                >
                  Редактировать
                </ElButton>
                <ElButton 
                  size="mini" 
                  type="danger"
                  @click="deleteUser(row)"
                  :disabled="row.id === currentUserId"
                  class="action-button delete-button user-management-action-button"
                >
                  Удалить
                </ElButton>
              </div>
            </template>
          </ElTableColumn>
          
          <template #empty>
            <div class="empty-table">
              <p>Нет данных для отображения.</p>
              <p class="empty-hint">
                Таблица пустая. Добавьте новых пользователей.
              </p>
            </div>
          </template>
        </ElTable>
      </div>
    </div>

    <ElDialog
      :title="isEditing ? 'Редактирование пользователя' : 'Создание пользователя'"
      :visible.sync="userModalVisible"
      width="500px"
      @close="closeUserModal"
      class="user-management-dialog"
    >
      <UserForm
        v-if="userModalVisible"
        :user="editingUser"
        :is-editing="isEditing"
        @submit="handleUserSubmit"
        @cancel="closeUserModal"
      />
    </ElDialog>
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex'
import UserForm from '@/components/UserForm.vue'
import { MessageBox } from 'element-ui'
import { ROUTES } from "@/router";

export default {
  name: 'UserManagementView',
  components: {
    UserForm
  },
  data() {
    return {
      loading: false,
      users: [],
      userModalVisible: false,
      editingUser: null,
      isEditing: false
    }
  },
  computed: {
    ...mapGetters('auth', ['getUserRole', 'getUserToken', 'isAdmin', 'getUserId']),
    ...mapState('auth', ['userLogin']),
    
    currentUser() {
      return {
        login: this.userLogin,
        role: this.getUserRole,
        id: this.getUserId
      };
    },
    
    currentUserId() {
      return this.getUserId;
    }
  },
  mounted() {
    // проверка прав доступа
    if (!this.isAdmin) {
      this.$message.error('Доступ запрещен. Требуются права администратора.')
      this.$router.push(ROUTES.LIST)
      return
    }
    
    this.loadUsers()
  },
  methods: {
    goBack() {
      this.$router.push({ name: ROUTES.LIST });
    },

    loadUsers() {
      this.loading = true
      
      this.$store.dispatch('users/fetchUsers')
        .then(response => {
          if (response.success) {
            this.users = response.users
          } else {
            this.$message.error('Ошибка при загрузке пользователей')
          }
        })
        .catch(error => {
          console.error('Error loading users:', error)
          this.$message.error(error.message || 'Ошибка при загрузке пользователей')
        })
        .finally(() => {
          this.loading = false
        })
    },

    openCreateModal() {
      this.editingUser = null
      this.isEditing = false
      this.userModalVisible = true
    },

    openEditModal(user) {
      this.editingUser = { ...user }
      this.isEditing = true
      this.userModalVisible = true
    },

    closeUserModal() {
      this.userModalVisible = false
      this.editingUser = null
      this.isEditing = false
    },

    handleUserSubmit(userData) {
      if (this.isEditing) {
        this.$store.dispatch('users/updateUser', {
          id: this.editingUser.id,
          ...userData
        })
          .then(() => {
            this.$message.success('Пользователь успешно обновлен')
            this.closeUserModal()
            this.loadUsers()
          })
          .catch(error => {
            console.error('Error saving user:', error)
            this.$message.error(error.message || 'Ошибка при сохранении пользователя')
          })
      } else {
        this.$store.dispatch('users/createUser', userData)
          .then(() => {
            this.$message.success('Пользователь успешно создан')
            this.closeUserModal()
            this.loadUsers()
          })
          .catch(error => {
            console.error('Error creating user:', error)
            this.$message.error(error.message || 'Ошибка при создании пользователя')
          })
      }
    },

    deleteUser(user) {
      MessageBox.confirm(
        `Вы уверены, что хотите удалить пользователя "${user.login}"?`,
        'Подтверждение удаления',
        {
          confirmButtonText: 'Удалить',
          cancelButtonText: 'Отмена',
          type: 'warning'
        }
      )
        .then(() => {
          return this.$store.dispatch('users/deleteUser', user.id)
        })
        .then(() => {
          this.$message.success('Пользователь успешно удален')
          this.loadUsers()
        })
        .catch(error => {
          if (error !== 'cancel') {
            console.error('Error deleting user:', error)
            this.$message.error(error.message || 'Ошибка при удалении пользователя')
          }
        })
    },

    getRoleLabel(role) {
      const roles = {
        'admin': 'Администратор',
        'moderator': 'Модератор',
        'regular': 'Пользователь'
      }
      return roles[role] || role
    },
    
    getUserRoleLabel(role) {
      return this.getRoleLabel(role);
    },

    getRoleTagType(role) {
      const types = {
        'admin': 'danger',
        'moderator': 'warning',
        'regular': 'info'
      }
      return types[role] || 'info'
    },
    
    getRowClassName({ row }) {
      if (row.id === this.currentUserId) {
        return 'current-user-row';
      }
      return '';
    }
  }
}
</script>

<!-- Глобальные стили для таблицы (без scoped) -->
<style lang="less">
  
.user-management-table {
  width: 100% !important;
  
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
  
  .el-table__body {
    td {
      padding: 12px 10px;
      
      .cell {
        line-height: 1.4;
      }
    }
  }

  .analysis-table__column {
    &--id {
      width: 80px !important;
      min-width: 80px !important;
      max-width: 80px !important;
    }
    
    &--login {
      min-width: 150px !important;
      max-width: 200px !important;
    }
    
    &--email {
      min-width: 200px !important;
      max-width: 300px !important;
    }
    
    &--role {
      width: 150px !important;
      min-width: 150px !important;
      max-width: 150px !important;
    }
    
    &--status {
      width: 120px !important;
      min-width: 120px !important;
      max-width: 120px !important;
    }
    
    &--actions {
      width: 150px !important;
      min-width: 150px !important;
      max-width: 150px !important;
    }
  }
  
  .user-management-actions-column {
    .cell {
      padding: 8px 0 !important;
      text-align: center !important;
    }
  }
  
  .el-table__empty-block {
    width: 100% !important;
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.current-user-row {
  background-color: #f0f9ff !important;
  
  &:hover > td {
    background-color: #e6f7ff !important;
  }
}

.role-tag,
.status-tag {
  margin: 2px;
}

.current-user-tag {
  margin-left: 8px;
}

.user-management-action-buttons {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 5px;
  
  .user-management-action-button {
    width: 100% !important;
    min-width: 0 !important;
    margin: 0 !important;
    padding: 8px 5px !important;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    box-sizing: border-box;
    display: block;
  }
}
</style>

<!-- Попытка избавиться от deep -->
<!-- Scoped стили (только для компонента) -->
<style scoped lang="less">
.user-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  width: 100%;
  box-sizing: border-box;

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;

    h1 {
      margin: 0;
      color: #303133;
      font-size: 24px;
      font-weight: 600;
      white-space: nowrap;
    }
  }

  .user-info {
    color: #606266;
    font-size: 14px;
  }
}

.controls {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.table-wrapper {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.table-container {
  width: 100%;
  overflow-x: auto;
  
  &__content {
    padding: 0;
  }
}

.login-cell {
  display: flex;
  align-items: center;
  gap: 8px;
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
</style>
