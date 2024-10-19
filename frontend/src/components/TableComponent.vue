<template>
  <div class="table-container">
    <div class="table-container__header">
      <el-button type="primary" @click="analyze">Провести анализ</el-button>
    </div>

    <el-table :data="paginatedData" style="width: 100%">
      <el-table-column label="Изображение" prop="image"></el-table-column>
      <el-table-column label="Модель 1" prop="firstModelResult"></el-table-column>
      <el-table-column label="Модель 2" prop="secondModelResult"></el-table-column>
      <el-table-column label="Модель 3" prop="thirdModelResult"></el-table-column>
      <el-table-column label="Результат" prop="ensembleModelsResult"></el-table-column>
      <el-table-column label="Действия">
        <el-button
            type="danger"
            size="mini"
            @click="deleteItem(scope.$index)">
          Удалить
        </el-button>
      </el-table-column>
    </el-table>

    <div class="table-container__pagination">
      <el-pagination
          layout="prev, pager, next"
          :current-page="currentPage"
          :page-size="itemsPerPage"
          :total="data.length"
          @current-change="changePage"
      >
      </el-pagination>
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

  &__pagination {
    margin-top: 10px;
    display: flex;
    justify-content: center;
  }
}
</style>