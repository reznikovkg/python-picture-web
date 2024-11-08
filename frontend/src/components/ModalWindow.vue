<template>
  <div v-loading="loading">
    <el-upload
        class="upload-demo"
        action=""
        :on-change="handleImageChange"
        :auto-upload="false"
        :show-file-list="false"
    >
      <el-button type="primary">Загрузить изображение</el-button>
    </el-upload>

    <div v-if="imageUrl" class="image-preview">
      <h4>Предварительный просмотр:</h4>
      <img :src="imageUrl" alt="Загруженное изображение" class="image-preview__img"/>
    </div>

    <el-button
        v-if="imageUrl"
        type="success"
        @click="submitImage"
        style="margin-top: 10px;">
      Отправить
    </el-button>
  </div>
</template>

<script>
import axiosInstance from "@/axios";
import {mapActions} from 'vuex';
import {ROUTES} from "@/router";

export default {
  data() {
    return {
      imageUrl: '',
      selectedFile: null,
      loading: false,
    };
  },
  methods: {
    ...mapActions('table', ['addTableData']),

    handleImageChange(file) {
      this.selectedFile = file.raw;
      this.imageUrl = URL.createObjectURL(file.raw);
    },

    submitImage() {
      if (!this.selectedFile) {
        this.$message.error('Пожалуйста, выберите изображение.');
        return;
      }

      this.loading = true;

      const formData = new FormData();
      formData.append('image', this.selectedFile);

      axiosInstance.post('/back/classification-image', formData)
          .then((response) => {
            const predictions = response.data.individual_predictions.map(prediction => prediction[0]);
            const ensemble = response.data.ensemble_prediction[0];
            const newData = {
              image: this.selectedFile.name,
              firstModelResult: predictions[0],
              secondModelResult: predictions[1],
              thirdModelResult: predictions[2],
              ensembleModelsResult: ensemble
            };
            this.addTableData(newData);
            this.$router.push({name: ROUTES.LIST});
          })
          .catch(() => {
            this.$message.error('Ошибка при загрузке изображения.');
          })
          .finally(() => {
            this.loading = false;
          });
    },
  },
};
</script>

<style lang="less" scoped>
.image-preview {
  margin-top: 20px;
  text-align: center;

  &__img {
    max-height: 400px;
    width: auto;
    border: 1px solid #ddd;
    padding: 5px;
  }
}
</style>