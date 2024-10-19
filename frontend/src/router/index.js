import Vue from 'vue'
import ElementUI from 'element-ui';
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ListView from "@/views/ListView.vue";
import LoginView from "@/views/LoginView.vue";
import 'element-ui/lib/theme-chalk/index.css';

Vue.use(VueRouter)
Vue.use(ElementUI)

export const ROUTES = {
  HOME: 'home',
  LOGIN: 'login',
  LIST: 'list',
}

const routes = [
  {
    path: '/',
    name: ROUTES.HOME,
    component: HomeView
  },
  {
    path: '/login',
    name: ROUTES.LOGIN,
    component: LoginView
  },
  {
    path: '/list',
    name: ROUTES.LIST,
    component: ListView
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
