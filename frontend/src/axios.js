import axios from 'axios';
import {AUTH_TOKEN} from "@/views/LoginView.vue";

const axiosInstance = axios.create({
    baseURL: process.env.BASE_URL,
    timeout: 30000, // 30 секунд по умолчанию
});

axiosInstance.interceptors.request.use(config => {
    const token = localStorage.getItem(AUTH_TOKEN);
    if (token) {
        config.headers['Authorization'] = token;
    }

    // Увеличение таймаута для загрузки файлов
    if (config.data instanceof FormData) {
        config.timeout = 120000; // 2 минуты для загрузки файлов
        // Логирование информации о FormData
        console.log('Отправка FormData:', {
            method: config.method,
            url: config.url,
            params: config.params,
            //hasFiles: this.hasFilesInFormData(config.data),
            hasFiles: hasFilesInFormData(config.data),
        });
    } else {
        console.log('Отправка запроса:', {
            method: config.method,
            url: config.url,
            params: config.params,
            data: config.data,
        });
    }

    return config;
}, error => {
    console.error('Ошибка в перехватчике запроса:', error);
    return Promise.reject(error);
});

axiosInstance.interceptors.response.use(
    (response) => {
        console.log('Ответ получен:', {
            url: response.config.url,    // URL запроса
            status: response.status,     // Статус ответа
            data: response.data,         // Данные ответа
        });
        return response;  // возвращаем response
    },
    (error) => {
        // Улучшенная обработка ошибок
        if (error.code === 'ECONNABORTED') {
            console.error('Таймаут запроса:', {
                url: error.config?.url,
                timeout: error.config?.timeout,
                message: 'Превышено время ожидания ответа от сервера'
            });
            error.message = 'Превышено время ожидания ответа от сервера. Попробуйте снова.';
        } else if (!error.response) {
            console.error('Ошибка сети:', error);
            error.message = 'Ошибка сети. Проверьте подключение к интернету.';
        } else {
            console.error('Ошибка ответа:', {
                url: error.config?.url,
                status: error.response?.status,
                data: error.response?.data,
                headers: error.response?.headers
            });
        }
        
        return Promise.reject(error);  // обработка ошибки
    }
);

// Вспомогательная функция для проверки наличия файлов в FormData
function hasFilesInFormData(formData) {
    for (const pair of formData.entries()) {
        if (pair[1] instanceof File || pair[1] instanceof Blob) {
            return true;
        }
    }
    return false;
}

// Добавление метода к экземпляру axios для использования в других местах
axiosInstance.hasFilesInFormData = hasFilesInFormData;

export default axiosInstance;
