<template>
  <div class="table-container">
    <div class="table-container__controls">
      <ElButton type="primary" @click="() => loadMore()">Добавить</ElButton>
      <ElButton type="danger" @click="() => deleteAll()">Удалить все</ElButton>
    </div>
    <ElTable class="table-container__table" :data="paginatedData">
      <ElTableColumn label="Изображение" prop="image"/>
      <ElTableColumn label="Дата и время загрузки" prop="uploadTime"/>
      <ElTableColumn label="Модель 1 / Модель 2 / Модель 3 (Ансамбль)" :formatter="formatModelsAndResult"/>
      <ElTableColumn label="Действия">
        <template #default="{ $index }">
          <ElButton
              type="danger"
              size="mini"
              @click="() => deleteItem($index)">
            Удалить
          </ElButton>
        </template>
      </ElTableColumn>
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
  </div>
</template>

<script>
import {mapActions} from 'vuex';
import {ROUTES} from "@/router";
import {MessageBox} from 'element-ui';

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
    };
  },
  computed: {
    paginatedData() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      const end = start + this.itemsPerPage;
      return this.data.slice(start, end);
    },
  },
  methods: {
    ...mapActions('table', ['removeData']),
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
          this.removeData(itemToRemove.id);

          if (this.data.length === 0) {
            this.$router.push({ name: ROUTES.HOME });
          }
        })
        .catch(() => {
          this.$message.info('Удаление отменено.');
        });
    },
    deleteAll() {
      console.log('Удалить все нажато!');
    },
    loadMore() {
      this.$router.push({name: ROUTES.HOME});
    }
  },
};
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