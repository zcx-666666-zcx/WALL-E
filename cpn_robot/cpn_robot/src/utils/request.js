import axios from "axios";
import { ElMessage } from "element-plus";
import router from "../router";

const request = axios.create({
    baseURL: 'http://localhost:8080',
    headers: {
        'Content-Type': 'application/json'  // 设置默认请求头
    },
    timeout: 60000
})

request.interceptors.request.use(
    (config)=>{
        const loginUser = JSON.parse(localStorage.getItem('loginUserObject'))
        if(loginUser && loginUser.token){
            config.headers.token = loginUser.token
        }
        return config
    },
    (error)=>{
        return Promise.reject(error)
    }
)

request.interceptors.response.use(
    (response)=>{
        return response.data
    },
    (error)=>{
        if(error.response.status === 401){
            ElMessage.error("登陆超时，请先登录");
            router.push('/login')
        }
        return Promise.reject(error)
    }
);

export default request