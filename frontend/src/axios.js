import axios from 'axios';
import {AUTH_TOKEN} from "@/views/LoginView.vue";

const axiosInstance = axios.create({
    baseURL: process.env.BASE_URL,
});

axiosInstance.interceptors.request.use(config => {
    const token = localStorage.getItem(AUTH_TOKEN);
    if (token) {
        config.headers['Authorization'] = token;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

export default axiosInstance;