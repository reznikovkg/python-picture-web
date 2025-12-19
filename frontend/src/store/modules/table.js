import axiosInstance from "@/axios";

const state = {
    tableData: [],
    loading: false,
    error: null,
    pagination: {
        current_page: 1,
        total_pages: 1,
        total_count: 0,
        has_previous: false,
        has_next: false
    },
    filters: {
        page: 1,
        page_size: 10,
        show: 'active' // all, active, deleted (показ всех анализов, неудалённых и удалённых)
    }
};

const mutations = {
    SET_TABLE_DATA(state, data) {
        // сохранение results в tableData
        state.tableData = data.results || [];
        
        // сохранение пагинации (если она есть в ответе)
        if (data.pagination) {
            state.pagination = {
                current_page: data.pagination.current_page || 1,
                total_pages: data.pagination.total_pages || 1,
                total_count: data.pagination.total_count || 0,
                has_previous: data.pagination.has_previous || false,
                has_next: data.pagination.has_next || false
            };
        }
    },
    SET_LOADING(state, loading) {
        state.loading = loading;
    },
    SET_ERROR(state, error) {
        state.error = error;
    },
    CLEAR_ERROR(state) {
        state.error = null;
    },
    SET_FILTERS(state, filters) {
        state.filters = { ...state.filters, ...filters };
    },
    SET_PAGINATION(state, pagination) {
        state.pagination = { ...state.pagination, ...pagination };
    }
};

const actions = {
    fetchData({ commit, rootGetters, state }, filters = {}) {
        commit('SET_LOADING', true);
        commit('CLEAR_ERROR');
        
        // обновление фильтров
        if (Object.keys(filters).length > 0) {
            commit('SET_FILTERS', filters);
        }
        
        const currentFilters = { ...state.filters, ...filters };
        const authToken = rootGetters['auth/getUserToken'];
        
        // параметры запроса
        const params = {
            page: currentFilters.page,
            page_size: currentFilters.page_size,
            show: currentFilters.show
        };
        
        return axiosInstance.get(`cnn_table/${authToken}/get`, { params })
            .then(response => {
                if (response.data.success) {
                    commit('SET_TABLE_DATA', response.data);
                    return response.data;
                } else {
                    throw new Error(response.data.message || 'Ошибка при получении данных');
                }
            })
            .catch(error => {
                const errorMessage = error.response?.data?.message || error.message || 'Ошибка при получении данных';
                commit('SET_ERROR', errorMessage);
                
                // уведомление об ошибке
                if (error.response?.status === 403) {
                    throw new Error('Доступ запрещен.');
                } else if (error.response?.status === 404) {
                    throw new Error('Данные не найдены.');
                } else {
                    throw new Error(errorMessage);
                }
            })
            .finally(() => {
                commit('SET_LOADING', false);
            });
    },

    predictData({ dispatch, commit, rootGetters }, { selectedFile, patient, description }) {
        commit('SET_LOADING', true);
        commit('CLEAR_ERROR');
        
        const authToken = rootGetters['auth/getUserToken'];
        const formData = new FormData();
        formData.append('patient', patient);
        formData.append('description', description);
        formData.append('image', selectedFile);
        
        // Логирование информации о файле
        console.log('Отправка файла на анализ:', {
            fileName: selectedFile.name,
            fileType: selectedFile.type,
            //fileSize: this.formatFileSize(selectedFile.size),
            fileSize: (selectedFile.size / (1024*1024)).toFixed(2) + 'MB',
            patient: patient,
            description: description
        });

        return axiosInstance.post(`/back/classification-image/${authToken}`, formData)
            .then(response => {
                if (response.data && response.data.success !== false) {
                    // после успешного создания перезагрузка данных с текущими фильтрами
                    return dispatch('fetchData').then(() => {
                        return response.data;
                    });
                } else {
                    throw new Error(response.data?.message || 'Ошибка при загрузке изображения');
                }
            })
            .catch(error => {
                const errorMessage = error.response?.data?.message || error.message || 'Ошибка при загрузке изображения';
                commit('SET_ERROR', errorMessage);
                
                // более детальные сообщения об ошибках
                if (error.response?.status === 403) {
                    throw new Error('Доступ запрещен. Проверьте права пользователя.');
                } else if (error.response?.status === 404) {
                    throw new Error('Пользователь не найден.');
                } else if (error.response?.status === 400) {
                    throw new Error(errorMessage || 'Некорректный запрос.');
                } else {
                    throw new Error(errorMessage);
                }
            })
            .finally(() => {
                commit('SET_LOADING', false);
            });
    },

    predictListData({ dispatch, commit, rootGetters }, { selectedFiles, patient, description }) {
        commit('SET_LOADING', true);
        commit('CLEAR_ERROR');
        
        const authToken = rootGetters['auth/getUserToken'];
        const BATCH_SIZE = 50;
        const batches = [];

        // Логирование информации о файлах
        console.log('Отправка пакета файлов на анализ:', {
            fileCount: selectedFiles.length,
            patient: patient,
            description: description,
            files: selectedFiles.map(file => ({
                name: file.name,
                type: file.type,
                //size: this.formatFileSize(file.size)
                size: (selectedFile.size / (1024*1024)).toFixed(2) + 'MB'
            }))
        });

        for (let i = 0; i < selectedFiles.length; i += BATCH_SIZE) {
            batches.push(selectedFiles.slice(i, i + BATCH_SIZE));
        }

        console.log('Количество батчей:', batches.length);

        const sendBatch = (batch) => {
            const formData = new FormData();
            formData.append('patient', patient);
            formData.append('description', description);

            batch.forEach((file) => {
                formData.append('images', file);
            });

            console.log('Отправка батча с количеством файлов:', batch.length);

            return axiosInstance.post(`/back/classification-images/${authToken}`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                timeout: 600000,
            })
                .then((response) => {
                    console.log('Батч успешно отправлен');
                    return response;
                })
                .catch((error) => {
                    console.error('Ошибка при отправке батча:', error);
                    throw error;
                });
        };

        const batchPromises = batches.map((batch) => sendBatch(batch));

        return Promise.all(batchPromises)
            .then(() => {
                console.log('Все батчи успешно отправлены');
                // после успешной загрузки перезагрузка данных с текущими фильтрами
                return dispatch('fetchData');
            })
            .catch(error => {
                const errorMessage = error.response?.data?.message || error.message || 'Ошибка при отправке данных';
                commit('SET_ERROR', errorMessage);
                
                // более детальные сообщения об ошибках
                if (error.response?.status === 403) {
                    throw new Error('Доступ запрещен. Проверьте права пользователя.');
                } else if (error.response?.status === 404) {
                    throw new Error('Пользователь не найден.');
                } else if (error.response?.status === 400) {
                    throw new Error(errorMessage || 'Некорректный запрос.');
                } else {
                    throw new Error(errorMessage);
                }
            })
            .finally(() => {
                commit('SET_LOADING', false);
            });
    },

    removeData({ dispatch, commit, rootGetters }, { id, permanent = false }) {
        commit('SET_LOADING', true);
        commit('CLEAR_ERROR');
        
        const authToken = rootGetters['auth/getUserToken'];

        const params = { id };
        if (permanent) {
            params.permanent = 'true';
        }

        return axiosInstance.get(`/cnn_table/${authToken}/delete`, { params })
            .then(response => {
                if (response.data === true || response.status === 200) {
                    // после успешного удаления перезагрука данных с текущими фильтрами
                    return dispatch('fetchData').then(() => {
                        return { success: true, message: 'Запись успешно удалена' };
                    });
                } else {
                    throw new Error('Ошибка при удалении данных');
                }
            })
            .catch(error => {
                const errorMessage = error.response?.data?.message || error.message || 'Ошибка при удалении данных';
                commit('SET_ERROR', errorMessage);
                
                if (error.response?.status === 403) {
                    throw new Error('Доступ запрещен.');
                } else if (error.response?.status === 404) {
                    throw new Error('Запись не найдена.');
                } else {
                    throw new Error(errorMessage);
                }
            })
            .finally(() => {
                commit('SET_LOADING', false);
            });
    },

    removeAllData({ dispatch, commit, rootGetters }, { permanent = false, show = 'active' } = {}) {
        commit('SET_LOADING', true);
        commit('CLEAR_ERROR');
        
        const authToken = rootGetters['auth/getUserToken'];

        const params = {
            permanent: permanent ? 'true' : 'false',
            show: show
        };

        return axiosInstance.get(`/cnn_table/${authToken}/delete_all`, { params })
            .then(response => {
                console.log('Response from delete_all:', response.data);
                
                if (response.data && response.data.success) {
                    // после успешного удаления перезагрузка данных с текущими фильтрами
                    return dispatch('fetchData').then(() => {
                        return response.data;
                    });
                } else {
                    throw new Error(response.data?.message || 'Ошибка при удалении всех данных');
                }
            })
            .catch(error => {
                console.error('Error in removeAllData:', error);
                
                if (error.response) {
                    console.error('Response status:', error.response.status);
                    console.error('Response data:', error.response.data);
                }
                
                const errorMessage = error.response?.data?.message || error.message || 'Ошибка при удалении всех данных';
                commit('SET_ERROR', errorMessage);
                
                if (error.response?.status === 403) {
                    throw new Error('Доступ запрещен. У вас недостаточно прав для выполнения этого действия.');
                } else if (error.response?.status === 400) {
                    throw new Error(errorMessage || 'Некорректный запрос.');
                } else if (error.response?.status === 404) {
                    throw new Error('Записи не найдены.');
                } else {
                    throw new Error(errorMessage);
                }
            })
            .finally(() => {
                commit('SET_LOADING', false);
            });
    },

    updateRecord({ dispatch, commit, rootGetters }, payload) {
        commit('SET_LOADING', true);
        commit('CLEAR_ERROR');
        
        const authToken = rootGetters['auth/getUserToken'];

        return axiosInstance.post(`/cnn_table/${authToken}/update`, payload)
            .then(response => {
                if (response.data.success) {
                    // после успешного удаления перезагрузка данных с текущими фильтрами
                    return dispatch('fetchData').then(() => {
                        return response.data;
                    });
                } else {
                    throw new Error(response.data.message || 'Ошибка при обновлении записи');
                }
            })
            .catch(error => {
                const errorMessage = error.response?.data?.message || error.message || 'Ошибка при обновлении записи';
                commit('SET_ERROR', errorMessage);
                
                if (error.response?.status === 403) {
                    throw new Error('Доступ запрещен.');
                } else if (error.response?.status === 404) {
                    throw new Error('Запись не найдена.');
                } else {
                    throw new Error(errorMessage);
                }
            })
            .finally(() => {
                commit('SET_LOADING', false);
            });
    },

    setFilters({ commit }, filters) {
        commit('SET_FILTERS', filters);
    },

    clearError({ commit }) {
        commit('CLEAR_ERROR');
    },

    // Вспомогательная функция для форматирования размера файла
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

const getters = {
    // возвращение объекта с results и pagination для совместимости с существующим кодом
    getTableData: (state) => ({
        results: state.tableData || [],
        pagination: state.pagination
    }),
    getLoading: (state) => state.loading,
    getError: (state) => state.error,
    getPagination: (state) => state.pagination,
    getFilters: (state) => state.filters,
    
    // геттер для получения отфильтрованных данных (если нужно на фронтенде)
    getFilteredData: (state) => {
        if (state.filters.show === 'all') {
            return state.tableData;
        } else if (state.filters.show === 'active') {
            return state.tableData.filter(item => !item.is_deleted);
        } else if (state.filters.show === 'deleted') {
            return state.tableData.filter(item => item.is_deleted);
        }
        return state.tableData;
    },
    
    // геттер для статистики
    getStats: (state) => {
        const total = state.tableData.length;
        const active = state.tableData.filter(item => !item.is_deleted).length;
        const deleted = state.tableData.filter(item => item.is_deleted).length;
        
        return {
            total,
            active,
            deleted
        };
    }
};

export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters,
};
