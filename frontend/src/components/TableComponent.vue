<template>
  <div class="table-container">
    <div class="table-container__header">
      <ElButton type="primary" @click="() => analyze()">Провести анализ</ElButton>
    </div>

    <ElTable class="table-container__table" :data="paginatedData">
      <ElTableColumn label="Изображение" prop="image"/>
      <ElTableColumn label="Модель 1" prop="firstModelResult"/>
      <ElTableColumn label="Модель 2" prop="secondModelResult"/>
      <ElTableColumn label="Модель 3" prop="thirdModelResult"/>
      <ElTableColumn label="Результат" prop="ensembleModelsResult"/>
      <ElTableColumn label="Действия">
        <ElButton
            type="danger"
            size="mini"
            @click="() => deleteItem(scope.$index)">
          Удалить
        </ElButton>
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
    changePage(page) {
      this.currentPage = page;
    },
    deleteItem(index) {
      const globalIndex = (this.currentPage - 1) * this.itemsPerPage + index;
      this.$emit('delete-item', globalIndex);
    },
    analyze() {
      this.$emit('analyze');
    },
  },
};
</script>

<style scoped>
.table-container {
  margin: 20px;

  &__header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
  }

  &__table {
    width: 100%;
  }

  &__pagination {
    margin-top: 10px;
    display: flex;
    justify-content: center;
  }
}
</style>