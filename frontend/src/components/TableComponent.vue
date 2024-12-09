<template>
  <div class="animated_container" v-loading="loading">
    <div class="animated_container__table-container">
      <div class="table-container__controls">
        <ElButton type="primary" @click="() => loadMore()">Добавить</ElButton>
        <ElButton type="danger" @click="() => deleteAll()">Удалить все</ElButton>
        <ElButton type="danger" @click="() => logout()">Выход</ElButton>
        <ElUpload
            ref="upload"
            class="upload-demo"
            action=""
            :on-change="(file) => handleImageChange(file)"
            :auto-upload="false"
            :show-file-list="false">
        </ElUpload>
      </div>

      <ElTable class="table-container__table" :data="paginatedData" @row-click="(row) => openModal(row)">
        <ElTableColumn label="Изображение" prop="image"/>
        <ElTableColumn label="Дата и время загрузки" prop="date"/>
        <ElTableColumn label="Модель 1 / Модель 2 / Модель 3 (Ансамбль)"
                       :formatter="(row) => formatModelsAndResult(row)"/>
        <ElTableColumn label="Действия">
          <template #default="{ $index }">
            <ElButton
                type="danger"
                size="mini"
                @click.stop="() => deleteItem($index)">
              Удалить
            </ElButton>
          </template>
        </ElTableColumn>
        <template #empty>
          <p>Нет данных для отображения. Таблица пустая.</p>
        </template>
      </ElTable>

      <ElDialog
          :visible.sync="isModalVisible"
          :title="modalTitle"
          width="40%"
          @close="() => closeModal()"
          class="table-container__modal-window--image">
        <div v-if="modalTitle">
          <img :src="modalTitle" alt="Изображение"/>
        </div>
        <div v-else>
          <p>Загрузка изображения...</p>
        </div>
        <div slot="footer" class="el-dialog__footer">
          <ElButton @click="() => closeModal()">Закрыть</ElButton>
        </div>
      </ElDialog>
    </div>
    <div class="animated_container__pagination-container">
      <div class="pagination-container__pagination">
        <ElPagination
            layout="prev, pager, next"
            :current-page="currentPage"
            :page-size="itemsPerPage"
            :total="data.length"
            @current-change="(page)=>changePage(page)">
        </ElPagination>
      </div>
    </div>
  </div>
</template>

<script>
import {mapActions} from 'vuex';
import {MessageBox} from 'element-ui';
import {AUTH_TOKEN} from "@/views/LoginView.vue";
import axiosInstance from "@/axios";
import {ROUTES} from "@/router";
import router from "@/router";

export default {
  props: {
    data: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      currentPage: 1,
      itemsPerPage: 5,
      loading: false,
      isModalVisible: false,
      modalTitle: '',
    };
  },
  computed: {
    paginatedData() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.data.slice(start, end);
    },
    imageUrl() {
      return `${this.axiosInstance.defaults.baseURL}${this.modalTitle}`;
    }
  },
  methods: {
    axiosInstance,
    ...mapActions('table', ['removeData', 'removeAllData', 'predictData', 'fetchData']),

    logout() {
      MessageBox.confirm(
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
    formatModelsAndResult(row) {
      return `${row.model_1} / ${row.model_2} / ${row.model_3} (${row.ensemble})`;
    },
    changePage(page) {
      this.currentPage = page;
    },
    deleteItem(index) {
      MessageBox.confirm(
          'Вы уверены, что хотите удалить этот элемент?',
          'Подтверждение удаления',
          {
            confirmButtonText: 'Да',
            cancelButtonText: 'Нет',
            type: 'warning',
          }
      )
          .then(() => {
            const globalIndex = (this.currentPage - 1) * this.itemsPerPage + index;
            const itemToRemove = this.data[globalIndex];
            // Используем removeData из mapActions
            this.removeData(itemToRemove.id);
          })
          .catch(() => {
            console.log('Удаление отменено.');
          });
    },
    deleteAll() {
      MessageBox.confirm(
          'Вы уверены, что хотите удалить все?',
          'Подтверждение удаления',
          {
            confirmButtonText: 'Да',
            cancelButtonText: 'Нет',
            type: 'warning',
          }
      )
          .then(() => {
            console.log("Удаление подтверждено.");
            // Используем removeAllData из mapActions
            this.removeAllData();
          })
          .catch(() => {
            this.$message.info('Удаление отменено.');
          });
    },
    loadMore() {
      const inputElement = this.$refs.upload.$el.querySelector('input');
      if (inputElement) {
        inputElement.click();
      } else {
        console.error('Не удалось найти input внутри el-upload');
      }
    },
    openModal(row) {
      this.isModalVisible = true;
      this.modalTitle = row.image
    },
    closeModal() {
      this.isModalVisible = false;
    },
    handleImageChange(file) {
      let selectedFile = file.raw;

      if (!selectedFile) {
        this.$message.error('Пожалуйста, выберите изображение.');
        return;
      }

      this.loading = true;

      console.log('Файл для предсказания:', selectedFile);

      // Используем predictData из mapActions
      this.predictData(selectedFile)
          .then(() => {
            this.$message.success('Данные успешно отправлены и обработаны!');
          })
          .catch(error => {
            console.error('Ошибка предсказания:', error);
            this.$message.error('Ошибка при выполнении предсказания.');
          })
          .finally(() => {
            this.loading = false;
          });
    },
  },
};
</script>


<style scoped>
img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.animated_container__pagination-container {

  &__pagination {
    display: flex;
    justify-content: center;
    text-align: center;
    margin-top: 20px;
  }
}

.animated_container__table-container {
  margin: 20px;
  text-align: end;

  &__header {
    display: flex;
    justify-content: center;
    margin-bottom: 10px;
  }

  &__controls {
    display: flex;
    gap: 10px;
    justify-content: center;
    text-align: center;
  }

  &__table {
    width: 100%;
  }

  &__modal-window {
    &--image {
      padding: 10px;
      box-sizing: border-box;
      overflow: hidden;
    }
  }
}
</style>
