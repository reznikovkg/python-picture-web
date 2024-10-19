<template>
  <div class="login">
    <h1>Login</h1>
    <form @submit.prevent="loginUser">
      <div class="login__form-group">
        <label for="username">Логин:</label>
        <input type="text" v-model="username" class="login__input" required/>
      </div>
      <div class="login__form-group">
        <label for="password">Пароль:</label>
        <input type="password" v-model="password" class="login__input" required/>
      </div>
      <button type="submit" class="login__button login__button--large">Войти</button>
      <p v-if="error">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import axiosInstance from "@/axios";
import {ROUTES} from "@/router";

export const AUTH_TOKEN = 'authToken';

export default {
  data() {
    return {
      username: '',
      password: '',
      error: null,
    };
  },
  methods: {
    loginUser() {
      axiosInstance.get('auth/',
          {
            params: {
              login: this.username,
              password: this.password,
            }
          })
          .then((response) => {
            const token = response.data;
            localStorage.setItem(AUTH_TOKEN, token);
            this.$router.push({name: ROUTES.HOME});
          })
          .catch(() => {
            this.error = 'Login error';
          });
    },
  },
};
</script>

<style lang="less" scoped>
.login {
  max-width: 400px;
  margin: 100px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);

  &__form-group {
    margin-bottom: 15px;
  }

  &__input, &__button {
    width: calc(100% - 20px);
    padding: 10px;
    margin: 5px 10px;
    border-radius: 5px;
    box-sizing: border-box;
  }

  &__input {
    border: 1px solid #ccc;
  }

  &__button {
    background-color: #007bff;
    color: white;
    border: none;
    cursor: pointer;

    &:hover {
      background-color: #0056b3;
    }

    &--large {
      padding: 15px;
    }

    &--disabled {
      background-color: #ddd;
      cursor: not-allowed;
    }
  }
}
</style>
