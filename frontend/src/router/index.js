import Vue from 'vue'
import VueRouter from 'vue-router'
import ListView from "@/views/ListView.vue";
import LoginView from "@/views/LoginView.vue";
import FirstView from "@/views/FirstView.vue";
import { AUTH_TOKEN } from "@/views/LoginView.vue";

Vue.use(VueRouter)

export const ROUTES = {
  HOME: 'home',
  LOGIN: 'login',
  LIST: 'list',
  PREVIEW: 'preview',
}

const routes = [
  {
    path: '/login',
    name: ROUTES.LOGIN,
    component: LoginView,
  },
  {
    path: '/list',
    name: ROUTES.LIST,
    component: ListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/', // главная страница доступна без авторизации (сначала - информация о сервисе, а только потом - просьба ввести логин и пароль)
    name: ROUTES.PREVIEW,
    component: FirstView,
  },
  {
    path: '/*',
    redirect: '/', // редирект всех неизвестных путей на главную (на всякий случай)
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem(AUTH_TOKEN);
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !token) {
    // Если маршрут требует авторизации, а токена нет - на страницу логина
    next({ name: ROUTES.LOGIN });
  } else if (to.name === ROUTES.LOGIN && token) {
    // Если пользователь уже авторизован и пытается зайти на логин - на список
    next({ name: ROUTES.LIST });
  } else {
    // Во всех остальных случаях - разрешаем переход
    next();
  }
});

export default router