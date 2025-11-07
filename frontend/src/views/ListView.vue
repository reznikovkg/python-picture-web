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
    <div v-if="userRole !== 'admin'" class="no-access-message">
      
      Вы видите только свои записи. Администратор видит все записи. Текущая роль: <strong>{{ userRole }}</strong>.

    </div>
    <div v-if="userRole === 'admin'" class="admin-message">
      
      Вы видите все записи системы. Текущая роль: <strong>{{ userRole }}</strong>.
    
    </div>
  </div>
</template>

<script>
import TableComponent from '@/components/TableComponent.vue';
import { mapGetters } from 'vuex';
import { mapState } from 'vuex';

export default {
  name: 'ListVue',
  components: {
    TableComponent,
  },
  computed: {
    ...mapState('auth', ['userRole']),  // получение роли пользователя из Vuex
    ...mapGetters('table', ['getTableData']),
    tableData() {
      return this.getTableData.results || [];
    },
  },
  created() {
    this.$store.dispatch('table/fetchData'); // загрузка данных при открытии страницы (пометка для себя)
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
.no-access-message,
.admin-message {
  margin-top: 20px;
  padding: 10px;
  background-color: #fafafa;
  border: 1px solid #ddd;
  border-radius: 5px;
  text-align: center;
}
</style>
