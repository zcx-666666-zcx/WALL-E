<script setup>
    import{ref,onMounted}from 'vue';
    //声明响应式数据
    let name = ref('');

    //声明函数
    function func1(){
        console.log(1)
    };

    //声明钩子函数
    onMounted(()=>{
        console.log(2);
        
    })
</script>

<template>
    <button @click="func1">111</button>
    <button @click="onMounted">222</button>
</template>

<style>

</style>