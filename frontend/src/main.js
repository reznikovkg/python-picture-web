import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store';
import ElementUI from "element-ui";
import 'element-ui/lib/theme-chalk/index.css';

Vue.config.productionTip = false

Vue.use(ElementUI)

new Vue({
  router,
  store,
  render: h => h(App),
  created() {
    // инициализация пользователя при загрузке приложения
    this.$store.dispatch('auth/initializeUser');
  }
}).$mount('#app')
