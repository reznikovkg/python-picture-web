<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <ModalWindow msg="Welcome to Your Vue.js App"/>
  </div>
</template>

<script>
import FormView from '@/components/ModalWindow.vue'

export default {
  name: 'ModalFormView',
  components: {
    ModalWindow: FormView
  }
}
</script>
