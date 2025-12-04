<template>
  <div>
     <!-- Временная отладка -->
    <div v-if="true" style="position: fixed; top: 10px; right: 10px; background: yellow; padding: 10px; z-index: 1000;">
      Debug: {{ userRole }} | {{ userToken }}
    </div>
    <RouterView />
  </div>
</template>

<script>
import { ROUTES } from '@/router'
import { mapGetters, mapActions } from 'vuex'

export default {
  computed: {
    ROUTES (){
      return ROUTES
    },
    ...mapGetters('auth', ['getUserRole', 'getUserToken', 'getUserLogin']),
    userRole() {
      return this.getUserRole;
    },
    userToken() {
      return this.getUserToken;
    },
    userLogin() {
      return this.getUserLogin;
    }
  },
  mounted () {
    document.title = 'Распознавание'
  },
  methods: {
    ...mapActions('auth', ['setTestAdminRole', 'setTestRegularRole'])
  }

}
</script>

<!-- Подумать над стилями -->

<style lang="less">
body {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  padding: 0;
  margin: 0;
}

nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
