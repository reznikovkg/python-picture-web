<template>
  <div>
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

export default {
  data() {
    return {
      imageUrl: '',
      selectedFile: null,
    };
  },
  methods: {
    handleImageChange(file) {
      this.selectedFile = file.raw;
      this.imageUrl = URL.createObjectURL(file.raw);
    },

    submitImage() {
      if (!this.selectedFile) {
        this.$message.error('Пожалуйста, выберите изображение.');
        return;
      }

      const formData = new FormData();
      formData.append('image', this.selectedFile);

      axiosInstance.post('/back/classification-image', formData)
          .then(() => {
            this.$message.success('Изображение успешно загружено!');
          })
          .catch(() => {
            this.$message.error('Ошибка при загрузке изображения.');
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