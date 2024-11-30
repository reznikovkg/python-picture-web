<template>
  <div class="table-container" v-loading="loading">
    <div class="table-container__controls">
      <ElButton type="primary" @click="() => loadMore()">Добавить</ElButton>
      <ElButton type="danger" @click="() => deleteAll()">Удалить все</ElButton>
      <el-upload
          ref="upload"
          class="upload-demo"
          action=""
          :on-change="() => handleImageChange"
          :auto-upload="false"
          :show-file-list="false"
          style="display: none;"
      >
      </el-upload>
    </div>

    <ElTable class="table-container__table" :data="paginatedData" @row-click="(row) => openModal(row)">
      <ElTableColumn label="Изображение" prop="image"/>
      <ElTableColumn label="Дата и время загрузки" prop="date"/>
      <ElTableColumn label="Модель 1 / Модель 2 / Модель 3 (Ансамбль)" :formatter="(row) => formatModelsAndResult(row)"/>
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
        <p>Нет данных для отображения. Таблица пустая.</p> <!-- Ваше сообщение о том, что данных нет -->
      </template>
    </ElTable>

    <div class="table-container__pagination">
      <ElPagination
          layout="prev, pager, next"
          :current-page="currentPage"
          :page-size="itemsPerPage"
          :total="data.length"
          @current-change="(page)=>changePage(page)">
      </ElPagination>
    </div>

    <el-dialog
        :visible.sync="isModalVisible"
        :title="modalTitle"
        width="40%"
        @close="() => closeModal"
    >
      <div v-if="modalTitle">
        <img :src='modalTitle' alt="Изображение"
             style="width: 100%; max-height: 400px; object-fit: contain;"/>
      </div>
      <div v-else>
        <p>Загрузка изображения...</p>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="() => closeModal">Закрыть</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import {mapActions} from 'vuex';
import {MessageBox} from 'element-ui';
import axiosInstance from "@/axios";

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
    ...mapActions('table', ['removeData', 'removeAllData', 'predictData', 'addData']),
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
            const itemToRemove = this.data[globalIndex];+
            this.removeData(itemToRemove.id).then(() => {
              this.$store.dispatch('table/fetchData');
            });
          })
          .catch(() => {
            this.$message.info('Удаление отменено.');
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
            this.removeAllData()
                .then(() => {
                  this.$store.commit('table/SET_TABLE_DATA', []);
                })
                .catch(error => {
                  console.error('Ошибка в removeAllData:', error);
                  this.$message.error('Ошибка при удалении всех данных.');
                });
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

      this.predictData(selectedFile)
          .then(response => {

            const predictions = response.data.individual_predictions.map(prediction => String(prediction[0]));
            const ensemble = String(response.data.ensemble_prediction[0]);

            this.addData(
                {
                  imageFile: selectedFile,
                  model1: predictions[0],
                  model2: predictions[1],
                  model3: predictions[2],
                  ensemble: ensemble,
                })
                .then(() => {
                  this.$store.dispatch('table/fetchData');
                })
          })
          .finally(() => {
            this.loading = false;
          })
    },
  },
}
</script>

<style scoped>
.table-container {
  margin: 20px;
}

.table-container__header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.table-container__controls {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.table-container__table {
  width: 100%;
}

.table-container__pagination {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}
</style>