import axiosInstance from "@/axios";

const state = {
  users: [],
  loading: false,
  error: null
};

const mutations = {
  SET_USERS(state, users) {
    state.users = users;
  },
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  SET_ERROR(state, error) {
    state.error = error;
  },
  ADD_USER(state, user) {
    state.users.push(user);
  },
  UPDATE_USER(state, updatedUser) {
    const index = state.users.findIndex(user => user.id === updatedUser.id);
    if (index !== -1) {
      state.users.splice(index, 1, updatedUser);
    }
  },
  REMOVE_USER(state, userId) {
    state.users = state.users.filter(user => user.id !== userId);
  },
  CLEAR_ERROR(state) {
    state.error = null;
  }
};

const actions = {
  fetchUsers({ commit, rootGetters }) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    const authToken = rootGetters['auth/getUserToken'];
    console.log('Fetching users with token:', authToken);
    
    return axiosInstance.get(`/users/${authToken}/list`)
      .then(response => {
        console.log('Users response:', response.data);
        
        if (response.data.success) {
          commit('SET_USERS', response.data.users);
          return response.data;
        } else {
          throw new Error(response.data.error || 'Ошибка при загрузке пользователей');
        }
      })
      .catch(error => {
        console.error('Error in fetchUsers:', error);
        
        // логирование ошибки
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        }
        
        const errorMessage = error.response?.data?.error || error.message || 'Ошибка при загрузке пользователей';
        commit('SET_ERROR', errorMessage);
        
        // сообщения об ошибках
        if (error.response?.status === 403) {
          throw new Error('Доступ запрещен. Требуются права администратора.');
        } else if (error.response?.status === 404) {
          throw new Error('Endpoint не найден. Проверьте URL.');
        } else if (error.response?.status === 500) {
          throw new Error('Ошибка сервера при загрузке пользователей.');
        } else {
          throw new Error(errorMessage);
        }
      })
      .finally(() => {
        commit('SET_LOADING', false);
      });
  },

  createUser({ commit, rootGetters }, userData) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    const authToken = rootGetters['auth/getUserToken'];
    console.log('Creating user with token:', authToken, 'data:', userData);
    
    return axiosInstance.post(`/users/${authToken}/create`, userData)
      .then(response => {
        console.log('Create user response:', response.data);
        
        if (response.data.success) {
          commit('ADD_USER', response.data.user);
          return response.data;
        } else {
          throw new Error(response.data.error || 'Ошибка при создании пользователя');
        }
      })
      .catch(error => {
        console.error('Error in createUser:', error);
        
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        }
        
        const errorMessage = error.response?.data?.error || error.message || 'Ошибка при создании пользователя';
        commit('SET_ERROR', errorMessage);
        
        if (error.response?.status === 403) {
          throw new Error('Доступ запрещен. Требуются права администратора.');
        } else if (error.response?.status === 400) {
          throw new Error(errorMessage);
        } else {
          throw new Error(errorMessage);
        }
      })
      .finally(() => {
        commit('SET_LOADING', false);
      });
  },

  updateUser({ commit, rootGetters }, { id, ...userData }) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    const authToken = rootGetters['auth/getUserToken'];
    console.log('Updating user with token:', authToken, 'id:', id, 'data:', userData);
    
    return axiosInstance.put(`/users/${authToken}/update/${id}`, userData)
      .then(response => {
        console.log('Update user response:', response.data);
        
        if (response.data.success) {
          commit('UPDATE_USER', response.data.user);
          return response.data;
        } else {
          throw new Error(response.data.error || 'Ошибка при обновлении пользователя');
        }
      })
      .catch(error => {
        console.error('Error in updateUser:', error);
        
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        }
        
        const errorMessage = error.response?.data?.error || error.message || 'Ошибка при обновлении пользователя';
        commit('SET_ERROR', errorMessage);
        
        if (error.response?.status === 403) {
          throw new Error('Доступ запрещен. Требуются права администратора.');
        } else if (error.response?.status === 404) {
          throw new Error('Пользователь не найден.');
        } else if (error.response?.status === 400) {
          throw new Error(errorMessage);
        } else {
          throw new Error(errorMessage);
        }
      })
      .finally(() => {
        commit('SET_LOADING', false);
      });
  },

  deleteUser({ commit, rootGetters }, userId) {
    commit('SET_LOADING', true);
    commit('CLEAR_ERROR');
    
    const authToken = rootGetters['auth/getUserToken'];
    console.log('Deleting user with token:', authToken, 'id:', userId);
    
    return axiosInstance.delete(`/users/${authToken}/delete/${userId}`)
      .then(response => {
        console.log('Delete user response:', response.data);
        
        if (response.data.success) {
          commit('REMOVE_USER', userId);
          return response.data;
        } else {
          throw new Error(response.data.error || 'Ошибка при удалении пользователя');
        }
      })
      .catch(error => {
        console.error('Error in deleteUser:', error);
        
        if (error.response) {
          console.error('Response status:', error.response.status);
          console.error('Response data:', error.response.data);
        }
        
        const errorMessage = error.response?.data?.error || error.message || 'Ошибка при удалении пользователя';
        commit('SET_ERROR', errorMessage);
        
        if (error.response?.status === 403) {
          throw new Error('Доступ запрещен. Требуются права администратора.');
        } else if (error.response?.status === 404) {
          throw new Error('Пользователь не найден.');
        } else if (error.response?.status === 400) {
          throw new Error(errorMessage);
        } else {
          throw new Error(errorMessage);
        }
      })
      .finally(() => {
        commit('SET_LOADING', false);
      });
  },

  clearError({ commit }) {
    commit('CLEAR_ERROR');
  }
};

const getters = {
  users: (state) => state.users,
  loading: (state) => state.loading,
  error: (state) => state.error,
  getUserById: (state) => (id) => {
    return state.users.find(user => user.id === id);
  },
  searchUsers: (state) => (query) => {
    if (!query) return state.users;
    
    const lowerQuery = query.toLowerCase();
    return state.users.filter(user => 
      user.login.toLowerCase().includes(lowerQuery) ||
      (user.email && user.email.toLowerCase().includes(lowerQuery))
    );
  },
  usersByRole: (state) => (role) => {
    if (!role) return state.users;
    return state.users.filter(user => user.role === role);
  }
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
