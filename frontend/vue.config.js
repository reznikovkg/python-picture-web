const {defineConfig} = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    proxy: {
      '^/auth': {
        //запускать бэк на 8000 порту или поменять тут
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '^/back/classification-image': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})