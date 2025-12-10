import axiosInstance from "@/axios";

const state = {
  userRole: '',
  userToken: '',
  userLogin: '',
  userEmail: '',
  userId: null
};

const mutations = {
  SET_USER_ROLE(state, role) {
    state.userRole = role;
  },
  SET_USER_TOKEN(state, token) {
    state.userToken = token;
  },
  SET_USER_LOGIN(state, login) {
    state.userLogin = login;
  },
  SET_USER_EMAIL(state, email) {
    state.userEmail = email;
  },
  SET_USER_ID(state, id) {
    state.userId = id;
  },
  CLEAR_USER_DATA(state) {
    state.userRole = '';
    state.userToken = '';
    state.userLogin = '';
    state.userEmail = '';
    state.userId = null;
  }
};

const actions = {
  login({ commit }, credentials) {
    console.log('Login attempt with:', credentials);
    
    return axiosInstance.get('/auth', { 
      params: credentials 
    })
    .then(response => {
      console.log('Login response:', response.data);
      
      // сохранение данных пользователя
      if (response.data && response.data.key) { // сохранять информацию о пользователе в localStorage и восстанавливать её при инициализации приложения.
        commit('SET_USER_ROLE', response.data.role || ''); // нужно, чтобы при обновлении страницы, данные полученные при регистрации сохранялись 
        commit('SET_USER_TOKEN', response.data.key);
        commit('SET_USER_LOGIN', response.data.login || '');
        commit('SET_USER_EMAIL', response.data.email || '');
        commit('SET_USER_ID', response.data.id || null);
        
        localStorage.setItem('authToken', response.data.key);
        localStorage.setItem('userRole', response.data.role || '');
        localStorage.setItem('userLogin', response.data.login || '');
        localStorage.setItem('userEmail', response.data.email || '');
        localStorage.setItem('userId', response.data.id || '');
        
        return response.data;
      } else {
        throw new Error('Invalid response format');
      }
    })
    .catch(error => {
      console.error('Login error:', error);
      
      if (error.response) {
        throw error;
      } else {
        throw new Error('Network error');
      }
    });
  },
  
  getCurrentUser({ commit, getters }) {
    const token = getters.getUserToken;
    if (!token) {
      return Promise.reject(new Error('No authentication token'));
    }

    return axiosInstance.get(`/users/${token}/current`)
      .then(response => {
        if (response.data.success) {
          const userData = response.data.user;
          commit('SET_USER_LOGIN', userData.login || '');
          commit('SET_USER_EMAIL', userData.email || '');
          commit('SET_USER_ROLE', userData.role || '');
          commit('SET_USER_ID', userData.id || null);
          
          // обновление localStorage
          localStorage.setItem('userLogin', userData.login || '');
          localStorage.setItem('userEmail', userData.email || '');
          localStorage.setItem('userRole', userData.role || '');
          localStorage.setItem('userId', userData.id || '');
          
          return userData;
        } else {
          throw new Error(response.data.error || 'Failed to get user data');
        }
      })
      .catch(error => {
        console.error('Error getting current user:', error);
        throw error;
      });
  },
  
  logout({ commit }) {
    commit('CLEAR_USER_DATA');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userLogin');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userId');
    
    // возвращение промис для совместимости
    return Promise.resolve();
  },

  initializeUser({ commit }) {
    const token = localStorage.getItem('authToken'); // восстановление всех данных
    const role = localStorage.getItem('userRole');
    const login = localStorage.getItem('userLogin');
    const email = localStorage.getItem('userEmail');
    const userId = localStorage.getItem('userId');
    
    if (token) {
      commit('SET_USER_TOKEN', token);
      commit('SET_USER_ROLE', role || '');
      commit('SET_USER_LOGIN', login || '');
      commit('SET_USER_EMAIL', email || '');
      commit('SET_USER_ID', userId ? parseInt(userId) : null);
    }
    
    // возвращение промис для совместимости
    return Promise.resolve();
  },

  setTestAdminRole({ commit }) {
    commit('SET_USER_ROLE', 'admin');
    commit('SET_USER_TOKEN', 'test-token-admin');
    commit('SET_USER_LOGIN', 'test-admin');
    commit('SET_USER_EMAIL', 'admin@test.com');
    // обновление localStorage для сохранения состояния
    localStorage.setItem('userRole', 'admin');
    localStorage.setItem('authToken', 'test-token-admin');
    localStorage.setItem('userLogin', 'test-admin');
    localStorage.setItem('userEmail', 'admin@test.com');
    
    // возвращение промис для совместимости
    return Promise.resolve();
  },

  setTestRegularRole({ commit }) {
    commit('SET_USER_ROLE', 'regular');
    commit('SET_USER_TOKEN', 'test-token-regular');
    commit('SET_USER_LOGIN', 'test-user');
    commit('SET_USER_EMAIL', 'user@test.com');
    // обновление localStorage для сохранения состояния
    localStorage.setItem('userRole', 'regular');
    localStorage.setItem('authToken', 'test-token-regular');
    localStorage.setItem('userLogin', 'test-user');
    localStorage.setItem('userEmail', 'user@test.com');
    
    // возвращение промис для совместимости
    return Promise.resolve();
  }
};

const getters = {
  getUserRole: (state) => state.userRole,
  getUserToken: (state) => state.userToken,
  getUserLogin: (state) => state.userLogin,
  getUserEmail: (state) => state.userEmail,
  getUserId: (state) => state.userId,
  isAdmin: (state) => state.userRole === 'admin',
  isModerator: (state) => state.userRole === 'moderator',
  isRegular: (state) => state.userRole === 'regular',
  isAuthenticated: (state) => !!state.userToken,
  // геттер для полной информации о пользователе
  getCurrentUser: (state) => ({
    id: state.userId,
    login: state.userLogin,
    email: state.userEmail,
    role: state.userRole,
    token: state.userToken
  })
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};
