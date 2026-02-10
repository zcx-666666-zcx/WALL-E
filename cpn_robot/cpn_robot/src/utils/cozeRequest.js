import axios from "axios";

const cozerequest = axios.create({
    //token: '',
    baseURL: 'https://api.coze.cn',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer pat_qjJdH6KguUMKmyhr9uDIr38KxfHVL9eMSfRHVOZKUiKujB4TWcKAvZfzsxbRIQuJ`
    },
    timeout: 60000
})

cozerequest.interceptors.request.use(
    (config) => {
      // 确保 POST/PUT 请求的参数是 JSON 格式
      if (config.method === 'post' || config.method === 'put') {
        config.data = config.data || {};
      }
      return config;
    },
    (error) => Promise.reject(error)
);

export default cozerequest