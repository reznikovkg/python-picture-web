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

    console.log('Отправка запроса:', {
        method: config.method,
        url: config.url,
        params: config.params,
        data: config.data,
    });

    return config;
}, error => {
    return Promise.reject(error);
});

axiosInstance.interceptors.response.use(
    (response) => {
        console.log('Ответ получен:', {
            url: response.config.url,    // URL запроса
            status: response.status,     // Статус ответа
            data: response.data,         // Данные ответа
        });
        return response;  // Обязательно возвращаем response
    },
    (error) => {
        console.error('Ошибка ответа:', error.response);  // Логирование ошибки ответа
        return Promise.reject(error);  // Обработка ошибки
    }
);


export default axiosInstance;