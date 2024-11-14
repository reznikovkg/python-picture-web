const {defineConfig} = require('@vue/cli-service')
module.exports = defineConfig({
  devServer: {
    proxy: {
      '^/auth': {
        target: 'http://back:8000',
        changeOrigin: true,
      },
      '^/back/classification-image': {
        target: 'http://back:8000',
        changeOrigin: true,
      },
      '^/cnn_table': {
        target: 'http://back:8000',
        changeOrigin: true,
      }
    }
  }
})

