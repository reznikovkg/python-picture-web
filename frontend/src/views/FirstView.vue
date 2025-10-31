<template>
  <div class="list">
    <div class="main">
      <img :src="require('./../assets/logo.png')" alt="" style="width: 400px">
      <h1 style="text-align: center">
        Добро пожаловать <br> в Систему распознавания кожных заболеваний!
        <div>
          <RouterLink :to="{ name: 'list' }">
            <button class="btn-prime">Войти</button>
          </RouterLink>
        </div>

        <span style="font-size: 16px; margin-top: 20px">Система позволяет распозновать кожные признаки следующего: <br></span>

        <div style="margin-left: 30%; font-size: 14px; text-align: left; margin-top: 10px">
          1) Актинический кератоз (AK) <br>
          2) Базальноклеточная карцинома (BCC) <br>
          3) Доброкачественный кератоз (BKL) <br>
          4) Дерматофиброма (DF) <br>
          5) Меланома (MEL) <br>
          6) Меланоцитарный невус (NV) <br>
          7) Плоскоклеточный рак (SCC) <br>
          8) Сосудистое поражение (VASC) <br>
        </div>
      </h1>
    </div>
  </div>
</template>



<style scoped lang="less">
.main {
  display: flex;
  justify-content: center;
  gap: 40px;
  align-items: center;
  margin-top: 30vh;
  margin-bottom: 30px;
}

.btn-prime {
  padding: 10px 30px;
  font-size: 20px;
  background: #3b8bff;
  color: white;
  border: none;
  cursor: pointer;
  margin-top: 20px;

  &:hover {
    background: #1174fd;
  }
}
</style>
