<template>
  <div class="list">
    <RouterLink to="/" tag="div">
    <div class="header">
      <img :src="require('./../assets/mini.png')" alt="" style="width: 60px">

      Система распознавания кожных заболеваний

      <img :src="require('./../assets/mini.png')" alt="" style="width: 60px">
    </div>
    </RouterLink>
    <TableComponent :data="tableData"/>
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
    tableData() {
      return this.getTableData.results || [];
    },
  },
  created() {
    this.$store.dispatch('table/fetchData');
  },
};
</script>

<style scoped lang="less">
.header {
  font-size: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 30px;
  font-weight: 700;
  margin-top: 30px;
}
</style>
