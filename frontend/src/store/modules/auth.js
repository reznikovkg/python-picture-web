import axiosInstance from "@/axios";

const state = {
  userRole: '',
  userToken: '',
  userLogin: '',
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
  CLEAR_USER_DATA(state) {
    state.userRole = '';
    state.userToken = '';
    state.userLogin = '';
  }
};

const actions = {
  async login({ commit }, credentials) {
    try {
      console.log('Login attempt with:', credentials);
      
      const response = await axiosInstance.get('/auth', { 
        params: credentials 
      });
      
      console.log('Login response:', response.data);
      
      // сохранение данных пользователя
      if (response.data && response.data.key) { // сохранять информацию о пользователе в localStorage и восстанавливать её при инициализации приложения.
        commit('SET_USER_ROLE', response.data.role || ''); // нужно, чтобы при обновлении страницы, данные полученные при регистрации сохранялись 
        commit('SET_USER_TOKEN', response.data.key);
        commit('SET_USER_LOGIN', response.data.login || '');
        
        localStorage.setItem('authToken', response.data.key);
        localStorage.setItem('userRole', response.data.role || '');
        localStorage.setItem('userLogin', response.data.login || '');
        
        return response.data;
      } else {
        throw new Error('Invalid response format');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      if (error.response) {
        throw error;
      } else {
        throw new Error('Network error');
      }
    }
  },
  
  logout({ commit }) {
    commit('CLEAR_USER_DATA');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userLogin');
  },

  initializeUser({ commit }) {
    const token = localStorage.getItem('authToken'); // восстановление всех данных
    const role = localStorage.getItem('userRole');
    const login = localStorage.getItem('userLogin');
    if (token) {
      commit('SET_USER_TOKEN', token);
      commit('SET_USER_ROLE', role || '');
      commit('SET_USER_LOGIN', login || '');
    }
  },

  setTestAdminRole({ commit }) {
    commit('SET_USER_ROLE', 'admin');
    commit('SET_USER_TOKEN', 'test-token-admin');
    // Также обновляем localStorage для сохранения состояния
    localStorage.setItem('userRole', 'admin');
    localStorage.setItem('authToken', 'test-token-admin');
  },

  setTestRegularRole({ commit }) {
    commit('SET_USER_ROLE', 'regular');
    commit('SET_USER_TOKEN', 'test-token-regular');
    // Также обновляем localStorage для сохранения состояния
    localStorage.setItem('userRole', 'regular');
    localStorage.setItem('authToken', 'test-token-regular');
  }
};

const getters = {
  getUserRole: (state) => state.userRole,
  getUserToken: (state) => state.userToken,
  getUserLogin: (state) => state.userLogin,
  isAdmin: (state) => state.userRole === 'admin',
  isAuthenticated: (state) => !!state.userToken,
};

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters,
};