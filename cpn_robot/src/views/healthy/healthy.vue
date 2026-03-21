<script setup>
import * as echarts from 'echarts';
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { getFallApi, getRateApi, getHumidityApi, getBreatheApi, getTemperatureApi, GetMachineListApi } from '../../api/users';

const deviceId = ref('kCx33ym0Dt'); //请替换为实际的设备ID
let isFall = ref();
let fall = ref("未识别到目标");
let userid = ref(localStorage.getItem('Id'));
let picture_url = ref();
const Machines = ref([]);
let showMachine = ref("暂无")

//这儿是图表的定义
const rateChartRef = ref(null);
const humidityChartRef = ref(null);
const breathChartRef = ref(null);
const temperatureChartRef = ref(null);
let rateChart = null;
let humidityChart = null;
let breathChart = null;
let temperatureChart = null;

//实时显示的数值
let rate = ref(-1);
let humidity = ref(-1);
let breath = ref(-1);
let temperature = ref(-1);

//最值
let maxRate = ref(0);
let minRate = ref(240);
let maxHumidity = ref(0);
let minHumidity = ref(100);
let maxBreath = ref(0);
let minBreath = ref(100);
let maxTemperature = ref(0);
let minTemperature = ref(42);

//所有数据的二维数组 [时间，值]
let rateData = ref([]);
let humidityData = ref([]);
let breathData = ref([]);
let temperatureData = ref([]);

//定时器和resize监听函数（按图表分类）
let timers = {
  rate: null,
  humidity: null,
  breath: null,
  temperature: null,
  fetchData: null
};
let resizeHandlers = {
  rate: null,
  humidity: null,
  breath: null,
  temperature: null
};

const getMachinesList = async()=>{
    const userId = userid.value;
    const result = await GetMachineListApi(userId);
    if(result && result.code === 1){
            if(result.data && result.data.rows && result.data.rows.length > 0){
                Machines.value = result.data.rows;
                console.log(Machines)
                return;
            }
            else{
                Machines.value = [];
                return;
            }
        }
        else{
            alert("获取表格数据失败")
            return;
        }
  }

//最值计算
const calculateMinMax = (dataRef, maxRef, minRef) => {
  const values = dataRef.value.map(item => item[1]);
  if (values.length === 0) return;
  
  maxRef.value = Math.max(...values);
  minRef.value = Math.min(...values);
};

//处理接口返回的数据
const formatApiData = (apiData, fieldName) => {
  if (!apiData || !apiData.data || !apiData.data.rows) return [];
  
  const sortedRows = [...apiData.data.rows].sort((a, b) => {
    return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
  });
  
  return sortedRows.map((row, index) => {
    const timeStr = new Date(row.createdAt).toLocaleTimeString();
    return [timeStr, row[fieldName]];
  });
};

//获取心率数据
const fetchRateData = async () => {
  try {
    if (!deviceId.value) return;
    const res = await getRateApi(deviceId.value);
    rateData.value = formatApiData(res, 'rate');

    if (rateData.value.length > 0) {
      rate.value = rateData.value[rateData.value.length - 1][1];
      console.log("心率:" + rate.value);
    }
  } catch (error) {
    console.error('获取心率数据失败:', error);
  }
};

//获取湿度数据
const fetchHumidityData = async () => {
  try {
    if (!deviceId.value) return;
    const res = await getHumidityApi(deviceId.value);
    humidityData.value = formatApiData(res, 'humidity');
    
    if (humidityData.value.length > 0) {
      humidity.value = humidityData.value[humidityData.value.length - 1][1];
      console.log("湿度:" + humidity.value);
    }
  } catch (error) {
    console.error('获取湿度数据失败:', error);
  }
};

//获取呼吸数据
const fetchBreathData = async () => {
  try {
    if (!deviceId.value) return;
    const res = await getBreatheApi(deviceId.value);
    breathData.value = formatApiData(res, 'breathe');
    
    if (breathData.value.length > 0) {
      breath.value = breathData.value[breathData.value.length - 1][1];
      console.log("呼吸:" + breath.value);
    }
  } catch (error) {
    console.error('获取呼吸数据失败:', error);
  }
};

//获取体温数据
const fetchTemperatureData = async () => {
  try {
    if (!deviceId.value) return;
    const res = await getTemperatureApi(deviceId.value);
    temperatureData.value = formatApiData(res, 'temperature');
    
    if (temperatureData.value.length > 0) {
      temperature.value = temperatureData.value[temperatureData.value.length - 1][1];
      console.log("温度:" + temperature.value);
    }
  } catch (error) {
    console.error('获取体温数据失败:', error);
  }
};

//获取跌倒检测
const getFall = async () => {
  try {
    if(!deviceId.value) return;
    const res = await getFallApi(deviceId.value);
    if(res){
      isFall.value = res.data.fall;
      if(isFall.value == false){
        fall.value = '正常';
      }
      else if(isFall.value == true){
        fall.value = '跌倒';
      }
      else{
        fall.value = '未识别到目标';
      }
      console.log(fall.value);
    }
    
  } catch (error){
    console.error('获取姿态失败:',error);
  }
}

//批量获取所有数据
const fetchAllData = async () => {
  await Promise.all([
    fetchRateData(),
    fetchHumidityData(),
    fetchBreathData(),
    fetchTemperatureData(),
    getFall()
  ]);
};

//通用图表初始化函数
const initChart = (chartRef, chartInstance, data, config) => {
  if (!chartRef.value) {
    console.warn(`❌ ${config.name}图表容器未找到，请检查ref绑定`);
    return null;
  }

  const chart = echarts.init(chartRef.value);

  //图表配置
  const chartOption = {
    maintainAspectRatio: false,
    grid: {
      left: '2%',
      right: '2%',
      top: '5%',
      bottom: '10%', 
      containLabel: true
    },
    //视觉映射（按不同指标的阈值配置）
    visualMap: {
      type: 'piecewise',
      show: false,
      dimension: 1,
      pieces: config.visualPieces
    },
    xAxis: {
      type: 'category',
      data: data.value.map(item => item[0]),
      axisLine: { lineStyle: { color: '#fff' } },
      axisLabel: { 
        color: '#fff', 
        fontSize: '1vw',
        rotate: 0,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: config.yAxisName,
      nameTextStyle: { color: '#fff', fontSize: '1vw' },
      axisLine: { lineStyle: { color: '#fff' } },
      axisLabel: { color: '#fff', fontSize: '1vw' },
      min: config.yMin,
      max: config.yMax
    },
    series: [
      {
        name: config.name,
        type: 'line',
        data: data.value.map(item => item[1]),
        lineStyle: { width: 2 },
        itemStyle: { color: 'inherit' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: `${config.gradientColor}80` },
            { offset: 0, color: `${config.gradientColor}10` }
          ])
        },
        smooth: false,
        showSymbol: false,
        symbolSize: 4
      }
    ],
    tooltip: {
      trigger: 'axis',
      textStyle: { color: '#000', fontSize: '1vw' },
      backgroundColor: 'rgba(255,255,255,0.9)',
      borderRadius: 4,
      formatter: function(params) {
        // 自定义tooltip格式，显示时间和数值
        return `${params[0].axisValue}<br/>${params[0].seriesName}: ${params[0].value}`;
      }
    }
  };

  //渲染图表
  chart.setOption(chartOption);

  //窗口缩放监听
  const resizeHandler = () => {
    chart?.resize();
  };
  window.addEventListener('resize', resizeHandler);

  //返回图表实例和resize监听函数
  return { chart, resizeHandler };
};

//各图表的个性化初始化
const initRateChart = () => {
  const { chart, resizeHandler } = initChart(rateChartRef, rateChart, rateData, {
    name: '心率',
    yAxisName: '心率(次/分)',
    yMin: 0,
    yMax: 240,
    gradientColor: '#00ff99', 
    visualPieces: [
      { min: 170, color: '#ff0000' },
      { min: 120, max: 169, color: '#ffff00' },
      { min: 0, max: 119, color: '#00ff99' }
    ]
  });
  rateChart = chart;
  resizeHandlers.rate = resizeHandler;
  
  calculateMinMax(rateData, maxRate, minRate);
};

const initHumidityChart = () => {
  const { chart, resizeHandler } = initChart(humidityChartRef, humidityChart, humidityData, {
    name: '湿度',
    yAxisName: '湿度(%)',
    yMin: 0,
    yMax: 100,
    gradientColor: '#6699ff', //湿度渐变主色（蓝色）
    visualPieces: [
      { min: 80, color: '#ff0000' },    //过高：红色
      { min: 40, max: 79, color: '#00ff99' }, //正常：绿色
      { min: 0, max: 39, color: '#ffff00' }    //过低：黄色
    ]
  });
  humidityChart = chart;
  resizeHandlers.humidity = resizeHandler;
  
  calculateMinMax(humidityData, maxHumidity, minHumidity);
};

const initBreathChart = () => {
  const { chart, resizeHandler } = initChart(breathChartRef, breathChart, breathData, {
    name: '呼吸',
    yAxisName: '呼吸(次/分)',
    yMin: 0,
    yMax: 60,
    gradientColor: '#ff9966',
    visualPieces: [
      { min: 30, color: '#ff0000' },    
      { min: 12, max: 29, color: '#00ff99' },
      { min: 0, max: 11, color: '#ffff00' }
    ]
  });
  breathChart = chart;
  resizeHandlers.breath = resizeHandler;
  calculateMinMax(breathData, maxBreath, minBreath);
};

const initTemperatureChart = () => {
  const { chart, resizeHandler } = initChart(temperatureChartRef, temperatureChart, temperatureData, {
    name: '体温',
    yAxisName: '体温(℃)',
    yMin: 30,
    yMax: 42,
    gradientColor: '#ff6666', 
    visualPieces: [
      { min: 37.1, color: '#ff0000' },
      { min: 35.9, max: 37.0, color: '#00ff99' },
      { min: 0, max: 35.8, color: '#ffff00' }
    ]
  });
  temperatureChart = chart;
  resizeHandlers.temperature = resizeHandler;

  calculateMinMax(temperatureData, maxTemperature, minTemperature);
};

//监听各图表数据变化，自动更新
watch(rateData, (newVal) => {
  if (rateChart) rateChart.setOption({ xAxis: { data: newVal.map(i => i[0]) }, series: [{ data: newVal.map(i => i[1]) }] });
  
  calculateMinMax(rateData, maxRate, minRate);
}, { deep: true });

watch(humidityData, (newVal) => {
  if (humidityChart) humidityChart.setOption({ xAxis: { data: newVal.map(i => i[0]) }, series: [{ data: newVal.map(i => i[1]) }] });
  
  calculateMinMax(humidityData, maxHumidity, minHumidity);
}, { deep: true });

watch(breathData, (newVal) => {
  if (breathChart) breathChart.setOption({ xAxis: { data: newVal.map(i => i[0]) }, series: [{ data: newVal.map(i => i[1]) }] });
  
  calculateMinMax(breathData, maxBreath, minBreath);
}, { deep: true });

watch(temperatureData, (newVal) => {
  if (temperatureChart) temperatureChart.setOption({ xAxis: { data: newVal.map(i => i[0]) }, series: [{ data: newVal.map(i => i[1]) }] });
  
  calculateMinMax(temperatureData, maxTemperature, minTemperature);
}, { deep: true });

//刷新
const ER = () => {
  if(rateChart){
    rateChart.dispose();
    rateChart = null;
    rateData.value=[];
    initRateChart();
  }
}
const EH = () => {
  if(humidityChart){
    humidityChart.dispose();
    humidityChart = null;
    humidityData.value=[];
    initHumidityChart();
  }
}
const EB = () => {
  if(breathChart){
    breathChart.dispose();
    breathChart = null;
    breathData.value=[];
    initBreathChart();
  }
}
const ET = () => {
  if(temperatureChart){
    temperatureChart.dispose();
    temperatureChart = null;
    temperatureData.value=[];
    initTemperatureChart();
  }
}
const Reloading = () => {
  [rateChart, humidityChart, breathChart, temperatureChart].forEach(chart => {
    if (chart) {
      chart.dispose();
      chart = null;
    }
    rateData.value=[];
    humidityData.value=[];
    breathData.value=[];
    temperatureData.value=[];
  });

  initRateChart();
  initHumidityChart();
  initBreathChart();
  initTemperatureChart();

}
//挂载时初始化所有图表和数据获取
onMounted(async () => {
  console.log(userid.value);

  initRateChart();
  initHumidityChart();
  initBreathChart();
  initTemperatureChart();

  await fetchAllData();

  getMachinesList();
  getFall();

  //设置定时器，每1秒获取一次数据
  timers.fetchData = setInterval(fetchAllData, 2000);
});

//卸载时清理资源
onUnmounted(() => {
  // 清除所有定时器
  Object.values(timers).forEach(timer => timer && clearInterval(timer));
  // 移除所有resize监听
  Object.entries(resizeHandlers).forEach(([key, handler]) => {
    if (handler) window.removeEventListener('resize', handler);
  });
  // 销毁所有图表实例
  [rateChart, humidityChart, breathChart, temperatureChart].forEach(chart => {
    if (chart) {
      chart.dispose();
      chart = null;
    }
  });
});
</script>

<template>
  <div class="Acontainer1">
    <!-- 心率图表 -->
    <div class="A" id="rate">
      <div class="TEXT" :style="{ color: rate >= 170 ? 'red' : rate >= 120 ? 'yellow' : '#00FF99' }">
        心率 : {{ rate }}
      </div>
      <div class="chart-container" ref="rateChartRef"></div>
      <div class="B">
        <text>最高：{{ maxRate }}<br>最低：{{ minRate }}</text>
      </div>
      <div class="choices">
        <button class="E" @click="ER">刷新</button>
        <button class="K">报警</button>
      </div>
    </div>
    <!-- 湿度图表 -->
    <div class="A" id="humidity">
      <div class="TEXT" :style="{ color: humidity >= 80 ? 'red' : humidity <= 39 ? 'yellow' : '#00FF99' }">
        湿度 : {{ humidity }}%
      </div>
      <div class="chart-container" ref="humidityChartRef"></div>
      <div class="B">
        <text>最高：{{ maxHumidity }}%<br>最低：{{ minHumidity }}%</text>
      </div>
      <div class="choices">
        <button class="E" @click="EH">刷新</button>
        <button class="K">报警</button>
      </div>
    </div>
    <!-- 呼吸图表 -->
    <div class="A" id="breath">
      <div class="TEXT" :style="{ color: breath >= 30 ? 'red' : breath <= 11 ? 'yellow' : '#00FF99' }">
        呼吸 : {{ breath }}次/分
      </div>
      <div class="chart-container" ref="breathChartRef"></div>
      <div class="B">
        <text>最高：{{ maxBreath }}次/分<br>最低：{{ minBreath }}次/分</text>
      </div>
      <div class="choices">
        <button class="E" @click="EB">刷新</button>
        <button class="K">报警</button>
      </div>
    </div>
    <!-- 体温图表 -->
    <div class="A" id="temperature">
      <div class="TEXT" :style="{ color: temperature >= 37.1 ? 'red' : temperature <= 35.8 ? 'yellow' : '#00FF99' }">
        温度 : {{ temperature }}℃
      </div>
      <div class="chart-container" ref="temperatureChartRef"></div>
      <div class="B">
        <text>最高：{{ maxTemperature }}℃<br>最低：{{ minTemperature }}℃</text>
      </div>
      <div class="choices">
        <button class="E" @click="ET">刷新</button>
        <button class="K">报警</button>
      </div>
    </div>
  </div>

  <div class="Acontainer2">

    <div id="Bcontainer1">
      <div id="fall">
        <div id="FALLTEXT"
        :style="{ color: fall === '未识别到目标' ? '#ffff00' : fall === '正常' ? '#00ff00' : '#ff0000' }">状态：{{ fall }}
        </div>
        当设备摄像头范围内未出现人时，显示未识别到目标，有人时进行检测。跌倒时会自动拍照并显示
        <picture id="picture" herf="{{ picture_url }}">

        </picture>
      </div>
      <div id="S">

      </div>
      <div id="DeviceC">
        <div id="D">
          <div class="devices" 
            v-for="(machine, index) in Machines.slice(0, 4)" 
            :key="index"
            @click="changeDeviceId(machine.id)" >
            {{ machine.machines }}
          </div>
        </div>
        <div id="info">
          <div id="show">当前显示：{{ showMachine }}</div>
          <div id="say">点击左侧设备来选择查看的设备数据<br>
            <button id="reloading" @click="Reloading">刷新页面</button>
          </div>
        </div>
      </div>

      <div class="choices">
          <button class="FE">刷新</button>
          <button class="FK">报警</button>
          <button id="C">请求图片</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
#reloading{
  height: 50%;
  width: 35%;
  background-color: rgb(9, 75, 7);
  color: white;
}
#show{
  width: 100%;
  height: 20%;
  font-size: 1.2vw;
  color: white;
}
#say{
  padding-top: 1%;
  width: 100%;
  height: 40%;
  color: white;
}
#info{
  width: 70%;
  height: 100%;
  padding: 2%;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  box-sizing: border-box;
}
.devices{
  width: 100%;
  height: 25%;
  background-color: rgb(110, 35, 35);
  color: #fff;
  font-size: 0.7vw;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 2%;
  box-sizing: border-box;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.devices:hover{
  background-color: rgb(140, 35, 35);
}
#D{
  width: 30%;
  height: 100%;
  border-right: 2px solid rgb(172, 172, 172);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: flex-start;
  box-sizing: border-box;

}
#DeviceC{
  border-right: 2px solid rgb(172, 172, 172);
  background-color: rgb(41, 41, 41);
  width: 31%;
  display: flex;
}
#S{
  width: 30%;
  border-right: 2px solid rgb(172, 172, 172);
  background-color: rgb(12, 12, 12);
}
#C{
  height: 20%;
  width: 80%;
  background-color: rgb(146, 108, 2);
  color: white;
  margin: 5% 0 0 0;
  font-size: 0.7vw;
  text-align: center;
}
.FE{
  height: 20%;
  background-color: rgb(173, 173, 173);
  margin: 0 0 5% 0;
}
.FK{
  height: 20%;
  background-color: rgb(124, 39, 39);
  margin: 5% 0 5% 0;
  color: white;
}
.E{
  background-color: rgb(173, 173, 173);
  margin: 0 0 5% 0;
}
.K{
  background-color: rgb(124, 39, 39);
  margin: 5% 0 0 0;
  color: white;
}
button{
  width: 80%;
  height: 30%;
  font-size: 0.7vw;
}
.choices{
  width: 8%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgb(41, 41, 41);
}
.chart-container {
  width: 65%;
  height: 96%;
  margin-left: 3%;
  background-color: rgb(39, 39, 39);
  position: relative;
  box-sizing: border-box;
}
.TEXT {
  width: 11%;
  height: 96%;
  color: rgb(255, 255, 255);
  font-size: 1.3vw;
  font-weight: 700;
  display: flex;
  align-items: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.A {
  padding: 0 0 0 2%;
  margin: 0.01% 1%;
  width: 98%;
  height: 85%;
  background-color: rgb(68, 68, 68);
  color: white;
  font-size: 2vw;
  font-weight: 800;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}
.B{
    padding: 0.5%;
    margin:  0 1%;
    width: 10%;
    height: 70%;
    font-size: 55%;
    font-weight: 600;
    /* 优化B区域样式，让文字居中显示 */
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: #fff;
}
.Acontainer1 {
  width: 100%;
  height: 65vh; 
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: repeat(4, 1fr);
  gap: 1%;
  box-sizing: border-box;
  background-color: rgb(204, 204, 204);
  padding: 1%;
}
.Acontainer2 {
  width: 100%;
  height: 20vh; 
  background-color: rgb(204, 204, 204);
  padding: 0 2%;
}
#Bcontainer1{
  width: 100%;
  height: 100%;
  background-color: rgb(68, 68, 68);
  display: flex;
}
#fall{
  width: 30%;
  height: 100%;
  background-color: rgb(68, 68, 68);
  padding: 1%;
  display: flex;
  flex-direction: column;
  font-size: 100%;
  color: white;
}
#FALLTEXT{
  height: 20%;
  width: 100%;
  font-size: 150%;
  font-weight: 700;
  display: flex;
  align-items: center;
}
#picture{
  height: 100px;
  width: 100px;
  background-color: rgb(20, 20, 20);
  border: 3px solid rgb(104, 104, 104);
}
</style>