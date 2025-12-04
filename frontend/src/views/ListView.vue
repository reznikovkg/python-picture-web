<template>
  <div class="list">
    <div class="header">
      <div class="header-left">
        <RouterLink to="/" tag="div" class="logo-link">
          <img :src="require('./../assets/mini.png')" alt="" style="width: 60px">
        </RouterLink>
        <h1>Система распознавания кожных заболеваний</h1>
      </div>
      
      <div class="header-right">
        <div class="user-info">
          <ElTag :type="getUserRoleTagType" effect="dark">
            {{ currentUser.login }} ({{ getUserRoleLabel }})
          </ElTag>
          <ElButton 
            v-if="isAdmin" 
            type="primary" 
            size="mini" 
            @click="goToUserManagement"
            class="user-management-btn"
          >
            Управление пользователями
          </ElButton>
        </div>
      </div>
    </div>

    <!-- Фильтры для админов и модераторов -->
    <div v-if="isAdmin || isModerator" class="filters">
      <div class="filter-group">
        <label>Показывать:</label>
        <ElSelect 
          v-model="showFilter" 
          placeholder="Выберите тип записей"
          @change="handleFilterChange"
          style="width: 200px; margin-left: 10px;"
        >
          <ElOption label="Все записи" value="all" />
          <ElOption label="Активные" value="active" />
          <ElOption label="Удаленные" value="deleted" />
        </ElSelect>
        
        <ElButton 
          type="primary" 
          @click="refreshData"
          :loading="loading"
          style="margin-left: 10px;"
        >
          Обновить
        </ElButton>
      </div>
      
      <div class="filter-stats" v-if="pagination">
        <span class="stats-text">
          Записей: {{ pagination.total_count }} | 
          Страница: {{ pagination.current_page }} из {{ pagination.total_pages }}
        </span>
      </div>
    </div>

    <TableComponent 
      :data="tableData"
      :user-role="userRole"
      :show-filter="showFilter"
      @delete-item="handleDeleteItem"
      @delete-all="handleDeleteAll"
      @refresh="refreshData"
    />

    <!-- Модальное окно подтверждения удаления -->
    <DeleteConfirmationModal
      :visible="deleteModalVisible"
      :item="selectedItem"
      :user-role="userRole"
      :loading="deleteLoading"
      :is-bulk-delete="isBulkDelete"
      :delete-count="deleteCount"
      @confirm="handleDeleteConfirm"
      @cancel="closeDeleteModal"
    />

    <div class="user-role-message">
      <div v-if="userRole === 'regular'" class="no-access-message">
        Вы видите только свои записи. Администратор видит все записи. Текущая роль: <strong>{{ getUserRoleLabel }}</strong>.
      </div>
      <div v-else class="admin-moderator-message">
        Вы видите все записи системы. Текущая роль: <strong>{{ getUserRoleLabel }}</strong>.
        <span v-if="showFilter === 'deleted'"> | Показаны удаленные записи</span>
        <span v-else-if="showFilter === 'active'"> | Показаны активные записи</span>
        <span v-else> | Показаны все записи</span>
      </div>
    </div>
  </div>
</template>

<script>
import TableComponent from '@/components/TableComponent.vue';
import DeleteConfirmationModal from '@/components/DeleteConfirmationModal.vue';
import { mapGetters, mapState } from 'vuex';
import { ROUTES } from "@/router";

export default {
  name: 'ListView',
  components: {
    TableComponent,
    DeleteConfirmationModal
  },
  data() {
    return {
      loading: false,
      showFilter: 'active', // all, active, deleted
      deleteModalVisible: false,
      selectedItem: null,
      deleteLoading: false,
      isBulkDelete: false,
      deleteCount: 0,
      currentPage: 1,
      pageSize: 10
    }
  },
  computed: {
    ...mapGetters('auth', ['getUserRole', 'getUserToken', 'isAdmin']),
    ...mapState('auth', ['userLogin']),
    ...mapGetters('table', ['getTableData']),
    
    userRole() {
      return this.getUserRole;
    },
    
    isModerator() {
      return this.userRole === 'moderator';
    },
    
    currentUser() {
      return {
        login: this.userLogin,
        role: this.userRole
      };
    },
    
    tableData() {
      return this.getTableData.results || [];
    },
    
    pagination() {
      return this.getTableData.pagination;
    },
    
    getUserRoleLabel() {
      const roles = {
        'admin': 'Администратор',
        'moderator': 'Модератор',
        'regular': 'Пользователь'
      };
      return roles[this.userRole] || this.userRole;
    },
    
    getUserRoleTagType() {
      const types = {
        'admin': 'danger',
        'moderator': 'warning',
        'regular': 'info'
      };
      return types[this.userRole] || 'info';
    }
  },
  created() {
    this.loadData();
  },
  methods: {
    loadData() {
      this.loading = true;
      
      this.$store.dispatch('table/fetchData', {
        page: this.currentPage,
        page_size: this.pageSize,
        show: this.showFilter
      })
      .then(() => {
        // Успешная загрузка
      })
      .catch(error => {
        console.error('Error loading data:', error);
        this.$message.error('Ошибка при загрузке данных');
      })
      .finally(() => {
        this.loading = false;
      });
    },

    refreshData() {
      this.loading = true;
      
      this.$store.dispatch('table/fetchData', {
        page: this.currentPage,
        page_size: this.pageSize,
        show: this.showFilter
      })
      .then(() => {
        this.$message.success('Данные обновлены');
      })
      .catch(error => {
        console.error('Error loading data:', error);
        this.$message.error('Ошибка при загрузке данных');
      })
      .finally(() => {
        this.loading = false;
      });
    },

    handleFilterChange() {
      this.currentPage = 1; // Сбрасываем на первую страницу при изменении фильтра
      this.loadData();
    },

    handleDeleteItem(item) {
      this.selectedItem = item;
      this.isBulkDelete = false;
      this.deleteModalVisible = true;
    },

    handleDeleteAll() {
      this.selectedItem = null;
      this.isBulkDelete = true;
      this.deleteCount = this.tableData.length;
      this.deleteModalVisible = true;
    },

    handleDeleteConfirm({ type, item, isBulk }) {
      this.deleteLoading = true;
      
      if (isBulk) {
        // Массовое удаление
        this.$store.dispatch('table/removeAllData', {
          permanent: type === 'permanent'
        })
        .then(() => {
          this.$message.success('Все записи успешно удалены');
          this.closeDeleteModal();
          return this.loadData();
        })
        .catch(error => {
          console.error('Error deleting:', error);
          this.$message.error('Ошибка при удалении');
        })
        .finally(() => {
          this.deleteLoading = false;
        });
      } else {
        // Удаление одной записи
        this.$store.dispatch('table/removeData', {
          id: item.id,
          permanent: type === 'permanent'
        })
        .then(() => {
          this.$message.success('Запись успешно удалена');
          this.closeDeleteModal();
          return this.loadData();
        })
        .catch(error => {
          console.error('Error deleting:', error);
          this.$message.error('Ошибка при удалении');
        })
        .finally(() => {
          this.deleteLoading = false;
        });
      }
    },

    closeDeleteModal() {
      this.deleteModalVisible = false;
      this.selectedItem = null;
      this.isBulkDelete = false;
      this.deleteCount = 0;
    },

    goToUserManagement() {
      this.$router.push({ name: ROUTES.USER_MANAGEMENT });
    },

    handlePageChange(page) {
      this.currentPage = page;
      this.loadData();
    }
  }
}
</script>

<style scoped lang="less">
.list {
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

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;

    .logo-link {
      cursor: pointer;
      transition: opacity 0.3s;

      &:hover {
        opacity: 0.8;
      }
    }

    h1 {
      margin: 0;
      color: #303133;
      font-size: 24px;
      font-weight: 600;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .user-management-btn {
        margin-left: 8px;
      }
    }
  }
}

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);

  .filter-group {
    display: flex;
    align-items: center;

    label {
      font-weight: 500;
      color: #606266;
      white-space: nowrap;
    }
  }

  .filter-stats {
    .stats-text {
      color: #909399;
      font-size: 14px;
    }
  }
}

.user-role-message {
  margin-top: 20px;
  text-align: center;

  .no-access-message, 
  .admin-moderator-message {
    padding: 12px 20px;
    border-radius: 4px;
    font-size: 14px;
  }

  .no-access-message {
    background-color: #f0f9ff;
    border: 1px solid #91d5ff;
    color: #096dd9;
  }

  .admin-moderator-message {
    background-color: #f6ffed;
    border: 1px solid #b7eb8f;
    color: #389e0d;
  }
}

</style>