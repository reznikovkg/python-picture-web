const {defineConfig} = require('@vue/cli-service')
module.exports = defineConfig({
  devServer: {
    proxy: {
      '^/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/back/classification-image': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/cnn_table': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/main/media/images/(.*)': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})

