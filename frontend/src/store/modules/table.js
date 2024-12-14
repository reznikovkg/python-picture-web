import axiosInstance from "@/axios";

const state = {
    tableData: [],
};

const mutations = {
    SET_TABLE_DATA(state, data) {
        state.tableData = data;
    },
};

const actions = {
    fetchData({commit}) {
        const authToken = localStorage.getItem('authToken')
        return axiosInstance.get(`cnn_table/${authToken}/get`)
            .then((response) => {
                console.log('Полученные данные:', response.data);
                commit('SET_TABLE_DATA', response.data);
            })
            .catch(error => {
                commit('SET_TABLE_DATA', []);
                console.error('Ошибка при получении данных:', error);
            });
    },
    // eslint-disable-next-line no-unused-vars
    predictData({dispatch, commit}, {selectedFile, patient, description}) {
        const authToken = localStorage.getItem('authToken')
        const formData = new FormData();
        formData.append('patient', patient);
        formData.append('description', description);
        formData.append('image', selectedFile);

        return axiosInstance.post(`/back/classification-image/${authToken}`, formData)
            .then(() => {
                dispatch('fetchData');
            })
            .catch(error => {
                console.error('Ошибка при загрузке изображения:', error);
            });
    },
    // eslint-disable-next-line no-unused-vars
    predictListData({dispatch, commit}, {selectedFiles, patient, description}) {
        const authToken = localStorage.getItem('authToken');
        const BATCH_SIZE = 50;
        const batches = [];

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
                .then(() => {
                    console.log('Батч успешно отправлен');
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
                dispatch('fetchData');
            })
            .catch((error) => {
                console.error('Ошибка при отправке данных:', error);
            });
    },
    removeData({dispatch}, index) {
        const authToken = localStorage.getItem('authToken')

        return axiosInstance.get(`/cnn_table/${authToken}/delete`, {
            params: { id: index }
        })
            .then(() => {
                dispatch('fetchData');
            })
            .catch(error => {
                console.error('Ошибка при удалении данных:', error);
            });
    },
    removeAllData({ dispatch }) {
        const authToken = localStorage.getItem('authToken');

        return axiosInstance.get(`/cnn_table/${authToken}/delete_all`)
            .then(() => {
                dispatch('fetchData');
            })
            .catch(error => {
                console.error('Ошибка при удалении всех данных:', error);
            });
    },
    updateRecord({ dispatch }, payload) {
        const authToken = localStorage.getItem('authToken');
        
        return axiosInstance.post(`/cnn_table/${authToken}/update`, payload)
            .then(() => {
                dispatch('fetchData');
            })
            .catch((error) => {
                console.error('Ошибка при обновлении записи:', error);
            });
      },
};

const getters = {
    getTableData: (state) => state.tableData,
};

export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters,
};
