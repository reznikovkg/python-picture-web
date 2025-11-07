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
import { mapState } from 'vuex'

export default {
  computed: {
    ROUTES (){
      return ROUTES
    },
    ...mapState('auth', ['userRole', 'userToken'])
  },
  mounted () {
    document.title = 'Распознавание'
  },
  methods: {
    setTestRole() {
      this.$store.commit('auth/SET_USER_ROLE', 'admin');
      this.$store.commit('auth/SET_USER_TOKEN', 'test-token');
    },
    setRegularRole() {
      this.$store.commit('auth/SET_USER_ROLE', 'regular');
      this.$store.commit('auth/SET_USER_TOKEN', 'test-token');
    }
  }

}
</script>

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
