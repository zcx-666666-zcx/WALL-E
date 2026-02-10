<script setup>
    import * as echarts from 'echarts';
    import {ref,onMounted, h} from 'vue';

    const chartRef = ref(null);
    let myChart = null;

    const initChart = () => {
        // 确保 DOM 元素已挂载
        if (!chartRef.value) return;

        // 初始化 ECharts 实例
        myChart = echarts.init(chartRef.value);

        // 指定图表的配置项和数据（和原生示例一致）
        const option = {
            title: {
              text: '睡眠监测(小时)'
            },
            xAxis: {
                type: 'category',
                data: ['date1', 'date2', 'date3','date4','date5','date6','date7','date8','date9','date10','date11','date12','date13','date14']
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                    data: [7.5, 7.7, 8.2, 7.9, 8.0, 7.6, 8.8, 7.9, 8.3, 8.2, 9.0, 8.2, 7.8, 6.5],
                    type: 'line'
                }
            ]
        };

        //使用配置项显示图表
        myChart.setOption(option);
    };

    //监听窗口大小变化，自适应图表
    const resizeChart = () => {
      if (myChart) {
        myChart.resize();
      }
    };

    onMounted(() => {
      initChart();
    });
</script>

<template>
    111
    <div ref="chartRef" class="echarts-container"></div>
</template>

<style>
    .echarts-container{
        width: 80%;
        height: 50%;
        border: 2px solid red;
    }
</style>