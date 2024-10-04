import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ListView from "@/views/ListView.vue";
import LoginView from "@/views/LoginView.vue";

Vue.use(VueRouter)

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
