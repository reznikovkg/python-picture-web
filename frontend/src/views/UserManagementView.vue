<template>
  <div class="user-management">
    <div class="header">
      <div class="header-left">
        <ElButton 
          icon="el-icon-back" 
          @click="goBack"
          class="back-button"
          style="margin-right: 20px;"
        >
          Назад
        </ElButton>
        <h1>Управление пользователями</h1>
      </div>
      
      <div class="user-info" v-if="currentUser">
        Текущий пользователь: <strong>{{ currentUser.login }}</strong> 
        ({{ currentUser.role }})
      </div>
    </div>

    <div class="controls">
      <ElButton 
        type="primary" 
        @click="openCreateModal"
        :disabled="loading"
      >
        Добавить пользователя
      </ElButton>
      <ElButton 
        @click="refreshUsers"
        :disabled="loading"
      >
        Обновить
      </ElButton>
    </div>

    <div v-loading="loading" class="table-container">
      <ElTable 
        :data="users" 
        class="users-table"
        empty-text="Нет пользователей для отображения"
      >
        <ElTableColumn label="ID" prop="id" width="80" />
        <ElTableColumn label="Логин" prop="login" />
        <ElTableColumn label="Email" prop="email">
          <template #default="{ row }">
            {{ row.email || '-' }}
          </template>
        </ElTableColumn>
        <ElTableColumn label="Роль" prop="role">
          <template #default="{ row }">
            <ElTag 
              :type="getRoleTagType(row.role)"
              effect="dark"
            >
              {{ getRoleLabel(row.role) }}
            </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn label="Статус" prop="authorization" width="120">
          <template #default="{ row }">
            <ElTag 
              :type="row.authorization ? 'success' : 'danger'"
              effect="light"
            >
              {{ row.authorization ? 'Активен' : 'Заблокирован' }}
            </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn label="Действия" width="120" header-align="center">
          <template #default="{ row }">
            <div class="action-buttons">
              <ElButton 
                size="mini" 
                type="primary"
                @click="openEditModal(row)"
                :disabled="row.id === currentUser?.id"
                class="action-button edit-button"
              >
                Редактировать
              </ElButton>
              <ElButton 
                size="mini" 
                type="danger"
                @click="deleteUser(row)"
                :disabled="row.id === currentUser?.id"
                class="action-button delete-button"
              >
                Удалить
              </ElButton>
            </div>
          </template>
        </ElTableColumn>
      </ElTable>
    </div>

    <!-- Модальное окно создания/редактирования пользователя -->
    <ElDialog
      :title="isEditing ? 'Редактирование пользователя' : 'Создание пользователя'"
      :visible.sync="userModalVisible"
      width="500px"
      @close="closeUserModal"
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
    ...mapGetters('auth', ['getUserRole', 'getUserToken', 'isAdmin']),
    ...mapState('auth', ['userLogin']),
    
    currentUser() {
      return {
        login: this.userLogin,
        role: this.getUserRole,
        id: null
      }
    }
  },
  mounted() {
    // Проверяем права доступа
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

    refreshUsers() {
      this.loading = true
      
      this.$store.dispatch('users/fetchUsers')
        .then(() => {
          this.$message.success('Список пользователей обновлен')
        })
        .catch(error => {
          console.error('Error refreshing users:', error)
          this.$message.error(error.message || 'Ошибка при обновлении пользователей')
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

    getRoleTagType(role) {
      const types = {
        'admin': 'danger',
        'moderator': 'warning',
        'regular': 'info'
      }
      return types[role] || 'info'
    }
  }
}
</script>

<style lang="less" scoped>
.user-management {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eaeaea;

  .header-left {
    display: flex;
    align-items: center;
    
    h1 {
      margin: 0;
      color: #303133;
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

.table-container {
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.users-table {
  width: 100%;

  .el-table__header-wrapper,
  .el-table__body-wrapper {
    border-radius: 4px;
  }
}

.no-access {
  text-align: center;
  padding: 40px;
  color: #909399;

  .no-access-icon {
    font-size: 48px;
    margin-bottom: 16px;
    color: #c0c4cc;
  }

  h2 {
    margin: 0 0 8px 0;
    color: #606266;
  }

  p {
    margin: 0;
    color: #909399;
  }
}

.action-buttons {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 5px;
  width: 100px;
  margin: 0 auto;
}

// жесткое переопределение стилей Element UI, иначе некорректно отображаются
:deep(.action-buttons .el-button) {
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
  float: none !important;
  clear: both !important;
}

// ликвидация всех возможных отступов и выравниваний
:deep(.el-table__body-wrapper .el-table__row .el-table_1_column_6 .cell) {
  padding: 8px 0 !important;
  text-align: center !important;
}
</style>