import Vue from 'vue'
import VueRouter from 'vue-router'
import ListView from "@/views/ListView.vue";
import LoginView from "@/views/LoginView.vue";
import {AUTH_TOKEN} from "@/views/LoginView.vue";

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
        redirect: {name: ROUTES.LIST},
    },
    {
        path: '/login',
        name: ROUTES.LOGIN,
        component: LoginView,
    },
    {
        path: '/list',
        name: ROUTES.LIST,
        component: ListView,
        meta: {requiresAuth: true},
    }
]

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    routes
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem(AUTH_TOKEN);
    if (to.matched.some(record => record.meta.requiresAuth) && !token) {
        next({name: ROUTES.LOGIN});
    } else {
        next();
    }
});

export default router
