<template>
  <div class="login">
    <h1>Войти в личный кабинет</h1>
    <h3>Укажите логин и пароль</h3>
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
      <p v-if="error" style="color: red; text-align: center;">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import { ROUTES } from "@/router";
export const AUTH_TOKEN = 'authToken';

export default {
  data () {
    return {
      username: '',
      password: '',
      error: null,
    };
  },
  methods: {
    async loginUser () {
      this.error = null; // ошибку в ноль
      
      try {
        await this.$store.dispatch('auth/login', { // vuex action для авторизации
          login: this.username,
          password: this.password,
        });
        
        this.$router.push({ name: ROUTES.LIST }); // на страницу списка
      } catch (error) {
        console.error('Login error:', error);
        
        if (error.response && error.response.status === 401) {
          this.error = 'Неверный пароль';
        } else if (error.response && error.response.status === 403) {
          this.error = 'Пользователь не авторизован';
        } else if (error.response && error.response.status === 404) {
          this.error = `Пользователь ${this.username} не найден`;
        } else if (error.response && error.response.data && error.response.data.error) {
          this.error = error.response.data.error;
        } else {
          this.error = 'Ошибка входа. Попробуйте еще раз.';
        }
      }
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