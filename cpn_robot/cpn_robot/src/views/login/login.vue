<script setup>
    import{ref} from 'vue';
    import {LoginApi} from '@/api/users.js';
    import { ElMessage } from 'element-plus';
    import { useRouter } from 'vue-router';
    
    const router = useRouter()
    let log = ref("登录")
    let username = ref('');
    let password = ref('');

    const GoToPage = (loginInfo)=>{
        router.push({
        path: '/index',
        query: { username: loginInfo.username }
        });
    }

    const login = async()=>{
        log.value="登录中...";
        if(!username.value || !password.value){
            alert("请输入完整内容");
            log.value="登录";
            return;
        }
        else{
            const loginInfo = {username: username.value,password: password.value}
            const result = await LoginApi(loginInfo);
            if(result.code){
                log.value="登录";
                localStorage.setItem('loginUserObject',JSON.stringify(result.data));
                username.value = result.data.username;
                console.log(username);
                
                localStorage.setItem('Id',username.value);
                GoToPage(loginInfo);
                
            }
            else{
                ElMessage.error(result.msg);
                log.value="登录";
            }
        }
    }

</script>

<template>
    <div class="container">
        <div id="form">
            <p>登录陪伴机器人管理平台</p>
            <input v-model="username" type="text" id="Uinput" placeholder="用户名：">
            <input v-model="password" type="password" id="Pinput" placeholder="密码:">
            <button @click="login">{{log}}</button>
        </div>
    </div>
</template>

<style>
    .container{
        height: 100vh;
        width: 100vw;
        background-color: rgb(121, 121, 121);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    p{
        margin: 0 0 40px 0;
        font-size: 35px;
        font-weight: 700;
    }  
    #form{
        height: 400px;
        width: 800px;
        background-image: url("http://localhost:8080/images/index_picture.png");
        position: absolute;
        background-size: cover;
        border: 4px solid rgb(73, 73, 73);
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
    }
    #Uinput{
        height: 37px;
        width: 300px;
        font-size: 17px;
        font-weight: 700;
        margin: 0 0 10px 0;
        padding: 10px;
        background-color: rgb(166, 255, 255);
        opacity: 0.7;
    }
    #Pinput{
        height: 37px;
        width: 300px;
        font-size: 17px;
        font-weight: 700;
        margin: 10px 0 0 0;
        padding: 10px;
        background-color: rgb(166, 255, 255);
        opacity: 0.7;
    }
    button{
        margin: 15px;
        height: 30px;
        width: 80px;
        background-color: rgb(255, 255, 255);
        opacity: 0.9;
    }
</style>