<template>
  <div class="list">
    <h1>Анализ</h1>
    <TableComponent :data="tableStub"/>
  </div>
</template>

<script>
import TableComponent from '@/components/TableComponent.vue';
import { mapGetters } from 'vuex';

export default {
  name: 'ListVue',
  components: {
    TableComponent,
  },
  computed: {
    ...mapGetters('table', ['getTableData']),
    tableStub() {
      return this.getTableData;
    },
  },
};
</script>