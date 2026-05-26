import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://localhost:8080'

// https://vitejs.dev/config/
export default defineConfig({
  base:'./',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // 添加服务器代理配置
  server: {
    proxy: {
      '/api': {
        target: apiProxyTarget,
        changeOrigin: true, // 修改请求头中的 Origin
        // rewrite: (path) => path.replace(/^\/api/, ''), // 后端路径本身包含 /api，不需要去掉
        // 更多配置选项
        // secure: false, // 如果后端使用 HTTPS 且证书无效，可以设为 false
        // ws: true, // 如果要代理 WebSocket
      }
    },
    // 可选：端口配置
    port: 5173,
    // 可选：自动打开浏览器
    open: true
  }
})
