<template>
  <div class="table-container">
    <div class="table-container__header">
      <button class="table-container__analyze-button">Провести анализ</button>
    </div>

    <table class="table-container__data-table">
      <thead>
      <tr>
        <th>Изображение</th>
        <th>Модель 1</th>
        <th>Модель 2</th>
        <th>Модель 3</th>
        <th>Результат</th>
        <th>Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(item, index) in paginatedData" :key="index">
        <td>{{ item.image }}</td>
        <td>{{ item.firstModelResult }}</td>
        <td>{{ item.secondModelResult }}</td>
        <td>{{ item.thirdModelResult }}</td>
        <td>{{ item.ensembleModelsResult }}</td>
        <td>
          <button @click="deleteItem(index)" class="table-container__delete-button">Удалить</button>
        </td>
      </tr>
      </tbody>
    </table>

    <div class="table-container__pagination">
      <button
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
          class="table-container__pagination-button"
      >
        Предыдущая
      </button>
      <span>Страница {{ currentPage }} из {{ totalPages }}</span>
      <button
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
          class="table-container__pagination-button"
      >
        Следующая
      </button>
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
    totalPages() {
      return Math.ceil(this.data.length / this.itemsPerPage);
    },
  },
  methods: {
    changePage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
      }
    },
    deleteItem(index) {
      const globalIndex = (this.currentPage - 1) * this.itemsPerPage + index;
      this.$emit('delete-item', globalIndex);
    },
  },
};
</script>

<style lang="less" scoped>
.table-container {
  margin: 20px;

  &__header {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
  }

  &__analyze-button {
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;

    &:hover {
      background-color: #45a049;
    }
  }

  &__data-table {
    width: 100%;
    border-collapse: collapse;

    th, td {
      padding: 10px;
      border: 1px solid #ddd;
      text-align: left;
    }

    tbody tr:nth-child(even) {
      background-color: #f2f2f2;
    }
  }

  &__delete-button {
    padding: 5px 10px;
    background-color: #f44336;
    color: white;
    border: none;
    cursor: pointer;

    &:hover {
      background-color: #e53935;
    }
  }

  &__pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 10px;

    &--button {
      padding: 5px 10px;
      margin: 0 5px;
    }
  }
}
</style>