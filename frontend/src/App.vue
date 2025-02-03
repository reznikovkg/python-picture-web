<template>
  <div>
    <RouterView />
  </div>
</template>

<script>
import { ROUTES } from '@/router'

export default {
  computed: {
    ROUTES (){
      return ROUTES
    }
  },
  mounted () {
    document.title = 'Распознавание'
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
