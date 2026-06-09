<script setup>
import * as echarts from 'echarts';
import { ref, onMounted, watch, onUnmounted } from 'vue';
import { getFallApi, getRateApi, getHumidityApi, getBreatheApi, getTemperatureApi, GetMachineListApi } from '../../api/users';
import { toast } from '../../utils/toast';
import { isAuthSilentError } from '../../utils/authSession';

const DEFAULT_DEVICE_ID = 'WALLE_1';
const deviceId = ref(DEFAULT_DEVICE_ID);
let isFall = ref();
let fall = ref("跌倒");
let userid = ref(localStorage.getItem('Id'));
let picture_url = ref();
const Machines = ref([]);
let showMachine = ref("瓦力");

const rateChartRef = ref(null);
const humidityChartRef = ref(null);
const breathChartRef = ref(null);
const temperatureChartRef = ref(null);
let rateChart = null;
let humidityChart = null;
let breathChart = null;
let temperatureChart = null;

let rate = ref(-1);
let humidity = ref(-1);
let breath = ref(-1);
let temperature = ref(-1);

let maxRate = ref(0); let minRate = ref(240);
let maxHumidity = ref(0); let minHumidity = ref(100);
let maxBreath = ref(0); let minBreath = ref(100);
let maxTemperature = ref(0); let minTemperature = ref(42);

let rateData = ref([]);
let humidityData = ref([]);
let breathData = ref([]);
let temperatureData = ref([]);

let timers = { rate: null, humidity: null, breath: null, temperature: null, fetchData: null };
let resizeHandlers = { rate: null, humidity: null, breath: null, temperature: null };
let active = true;

const logDataError = (message, error) => {
  if (isAuthSilentError(error) || error?.response?.status === 401) return;
  console.error(message, error);
};

const getMachinesList = async () => {
  const userId = userid.value;
  const result = await GetMachineListApi(userId);
  if (result && result.code === 1) {
    Machines.value = result.data?.rows?.length > 0 ? result.data.rows : [];
    const defaultMachine = Machines.value.find(m => m.connectionId === DEFAULT_DEVICE_ID);
    if (defaultMachine) {
      deviceId.value = defaultMachine.connectionId;
      showMachine.value = defaultMachine.machines;
    } else if (Machines.value.length === 0) {
      deviceId.value = DEFAULT_DEVICE_ID;
      showMachine.value = '瓦力';
    }
  } else { toast.error("获取表格数据失败"); }
};

const calculateMinMax = (dataRef, maxRef, minRef) => {
  const values = dataRef.value.map(item => item[1]);
  if (values.length === 0) return;
  maxRef.value = Math.max(...values);
  minRef.value = Math.min(...values);
};

const formatApiData = (apiData, fieldName) => {
  if (!apiData || !apiData.data || !apiData.data.rows) return [];
  const sortedRows = [...apiData.data.rows].sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());
  return sortedRows.map(row => [new Date(row.createdAt).toLocaleTimeString(), row[fieldName]]);
};

const fetchRateData = async () => {
  try { if (!deviceId.value) return;
    const res = await getRateApi(deviceId.value);
    rateData.value = formatApiData(res, 'rate');
    if (rateData.value.length > 0) rate.value = rateData.value[rateData.value.length - 1][1];
  } catch (error) { logDataError('获取心率数据失败:', error); }
};

const fetchHumidityData = async () => {
  try { if (!deviceId.value) return;
    const res = await getHumidityApi(deviceId.value);
    humidityData.value = formatApiData(res, 'humidity');
    if (humidityData.value.length > 0) humidity.value = humidityData.value[humidityData.value.length - 1][1];
  } catch (error) { logDataError('获取湿度数据失败:', error); }
};

const fetchBreathData = async () => {
  try { if (!deviceId.value) return;
    const res = await getBreatheApi(deviceId.value);
    breathData.value = formatApiData(res, 'breathe');
    if (breathData.value.length > 0) breath.value = breathData.value[breathData.value.length - 1][1];
  } catch (error) { logDataError('获取呼吸数据失败:', error); }
};

const fetchTemperatureData = async () => {
  try { if (!deviceId.value) return;
    const res = await getTemperatureApi(deviceId.value);
    temperatureData.value = formatApiData(res, 'temperature');
    if (temperatureData.value.length > 0) temperature.value = temperatureData.value[temperatureData.value.length - 1][1];
  } catch (error) { logDataError('获取体温数据失败:', error); }
};

const getFall = async () => {
  try { if (!deviceId.value) return;
    const res = await getFallApi(deviceId.value);
    if (res) {
      isFall.value = res.data.fall;
      fall.value = isFall.value === false ? '正常' : isFall.value === true ? '跌倒' : '未识别到目标';
    }
  } catch (error) { logDataError('获取姿态失败:', error); }
};

const fetchAllData = async () => {
  if (!active) return;
  await Promise.all([fetchRateData(), fetchHumidityData(), fetchBreathData(), fetchTemperatureData(), getFall()]);
};

const initChart = (chartRef, data, config) => {
  if (!chartRef.value) return null;
  const chart = echarts.init(chartRef.value);
  const chartOption = {
    grid: { left: '3%', right: '3%', top: '8%', bottom: '10%', containLabel: true },
    visualMap: { type: 'piecewise', show: false, dimension: 1, pieces: config.visualPieces },
    xAxis: {
      type: 'category', data: data.value.map(item => item[0]),
      axisLine: { lineStyle: { color: '#C4A898' } },
      axisLabel: { color: '#B09080', fontSize: 10, rotate: 0, interval: 'auto' }
    },
    yAxis: {
      type: 'value', name: config.yAxisName,
      nameTextStyle: { color: '#B09080', fontSize: 10 },
      axisLine: { lineStyle: { color: '#C4A898' } },
      axisLabel: { color: '#B09080', fontSize: 10 },
      min: config.yMin, max: config.yMax, splitLine: { lineStyle: { color: 'rgba(255,160,120,0.08)' } }
    },
    series: [{
      name: config.name, type: 'line', data: data.value.map(item => item[1]),
      lineStyle: { width: 2 }, itemStyle: { color: 'inherit' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: `${config.gradientColor}40` },
        { offset: 1, color: `${config.gradientColor}05` }
      ])},
      smooth: false, showSymbol: false, symbolSize: 4
    }],
    tooltip: {
      trigger: 'axis', textStyle: { color: '#3A2010', fontSize: 12 },
      backgroundColor: 'rgba(255,255,255,0.95)', borderRadius: 8,
      borderColor: 'rgba(255,160,120,0.15)',
      formatter: (params) => `${params[0].axisValue}<br/>${params[0].seriesName}: ${params[0].value}`
    }
  };
  chart.setOption(chartOption);
  const resizeHandler = () => chart?.resize();
  window.addEventListener('resize', resizeHandler);
  return { chart, resizeHandler };
};

const initRateChart = () => {
  const r = initChart(rateChartRef, rateData, {
    name: '心率', yAxisName: '心率(次/分)', yMin: 0, yMax: 240, gradientColor: '#4CAF50',
    visualPieces: [{ min: 170, color: '#E53935' }, { min: 120, max: 169, color: '#FF9800' }, { min: 0, max: 119, color: '#4CAF50' }]
  });
  if (r) { rateChart = r.chart; resizeHandlers.rate = r.resizeHandler; calculateMinMax(rateData, maxRate, minRate); }
};

const initHumidityChart = () => {
  const r = initChart(humidityChartRef, humidityData, {
    name: '湿度', yAxisName: '湿度(%)', yMin: 0, yMax: 100, gradientColor: '#2196F3',
    visualPieces: [{ min: 80, color: '#E53935' }, { min: 40, max: 79, color: '#4CAF50' }, { min: 0, max: 39, color: '#FF9800' }]
  });
  if (r) { humidityChart = r.chart; resizeHandlers.humidity = r.resizeHandler; calculateMinMax(humidityData, maxHumidity, minHumidity); }
};

const initBreathChart = () => {
  const r = initChart(breathChartRef, breathData, {
    name: '呼吸', yAxisName: '呼吸(次/分)', yMin: 0, yMax: 60, gradientColor: '#FF9800',
    visualPieces: [{ min: 30, color: '#E53935' }, { min: 12, max: 29, color: '#4CAF50' }, { min: 0, max: 11, color: '#FF9800' }]
  });
  if (r) { breathChart = r.chart; resizeHandlers.breath = r.resizeHandler; calculateMinMax(breathData, maxBreath, minBreath); }
};

const initTemperatureChart = () => {
  const r = initChart(temperatureChartRef, temperatureData, {
    name: '体温', yAxisName: '体温(℃)', yMin: 30, yMax: 42, gradientColor: '#E53935',
    visualPieces: [{ min: 37.1, color: '#E53935' }, { min: 35.9, max: 37.0, color: '#4CAF50' }, { min: 0, max: 35.8, color: '#FF9800' }]
  });
  if (r) { temperatureChart = r.chart; resizeHandlers.temperature = r.resizeHandler; calculateMinMax(temperatureData, maxTemperature, minTemperature); }
};

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

const ER = () => { if (rateChart) { rateChart.dispose(); rateChart = null; rateData.value = []; initRateChart(); } };
const EH = () => { if (humidityChart) { humidityChart.dispose(); humidityChart = null; humidityData.value = []; initHumidityChart(); } };
const EB = () => { if (breathChart) { breathChart.dispose(); breathChart = null; breathData.value = []; initBreathChart(); } };
const ET = () => { if (temperatureChart) { temperatureChart.dispose(); temperatureChart = null; temperatureData.value = []; initTemperatureChart(); } };

const Reloading = () => {
  [rateChart, humidityChart, breathChart, temperatureChart].forEach(c => { if (c) c.dispose(); });
  rateData.value = []; humidityData.value = []; breathData.value = []; temperatureData.value = [];
  initRateChart(); initHumidityChart(); initBreathChart(); initTemperatureChart();
};

const changeDeviceId = (machine) => {
  deviceId.value = machine?.connectionId || DEFAULT_DEVICE_ID;
  showMachine.value = machine?.machines || '瓦力';
  Reloading();
};

onMounted(async () => {
  initRateChart(); initHumidityChart(); initBreathChart(); initTemperatureChart();
  await fetchAllData();
  getMachinesList(); getFall();
  timers.fetchData = setInterval(fetchAllData, 1000);
});

onUnmounted(() => {
  active = false;
  Object.values(timers).forEach(timer => timer && clearInterval(timer));
  Object.entries(resizeHandlers).forEach(([key, handler]) => { if (handler) window.removeEventListener('resize', handler); });
  [rateChart, humidityChart, breathChart, temperatureChart].forEach(chart => { if (chart) { chart.dispose(); chart = null; } });
});

const rateColor = (v) => v >= 170 ? '#E53935' : v >= 120 ? '#FF9800' : '#4CAF50';
const humidityColor = (v) => v >= 80 ? '#E53935' : v <= 39 ? '#FF9800' : '#4CAF50';
const breathColor = (v) => v >= 30 ? '#E53935' : v <= 11 ? '#FF9800' : '#4CAF50';
const tempColor = (v) => v >= 37.1 ? '#E53935' : v <= 35.8 ? '#FF9800' : '#4CAF50';
const fallColor = (s) => s === '正常' ? '#4CAF50' : s === '跌倒' ? '#E53935' : '#FF9800';
</script>

<template>
  <div class="healthy-root">

    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 14S1.5 10 1.5 6.5a4 4 0 016.5-3A4 4 0 0114.5 6.5C14.5 10 8 14 8 14z" stroke="white" stroke-width="1.4" stroke-linejoin="round"/>
            <path d="M4.5 8h2l1-3 1.5 5 1-2H11.5" stroke="white" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div>
          <div class="page-title">健康监测</div>
          <div class="page-sub">实时体征数据 · 每2秒刷新</div>
        </div>
      </div>
      <button class="btn-reload" @click="Reloading">刷新全部</button>
    </div>

    <!-- 4 指标卡片 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-card-head">
          <span class="chart-card-label">心率</span>
          <span class="chart-card-val" :style="{ color: rateColor(rate) }">{{ rate }} <small>次/分</small></span>
        </div>
        <div class="chart-container" ref="rateChartRef"></div>
        <div class="chart-card-foot">
          <span>最高 {{ maxRate }}</span>
          <span>最低 {{ minRate }}</span>
          <button class="btn-mini" @click="ER">刷新</button>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-card-head">
          <span class="chart-card-label">湿度</span>
          <span class="chart-card-val" :style="{ color: humidityColor(humidity) }">{{ humidity }}<small>%</small></span>
        </div>
        <div class="chart-container" ref="humidityChartRef"></div>
        <div class="chart-card-foot">
          <span>最高 {{ maxHumidity }}%</span>
          <span>最低 {{ minHumidity }}%</span>
          <button class="btn-mini" @click="EH">刷新</button>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-card-head">
          <span class="chart-card-label">呼吸</span>
          <span class="chart-card-val" :style="{ color: breathColor(breath) }">{{ breath }} <small>次/分</small></span>
        </div>
        <div class="chart-container" ref="breathChartRef"></div>
        <div class="chart-card-foot">
          <span>最高 {{ maxBreath }}</span>
          <span>最低 {{ minBreath }}</span>
          <button class="btn-mini" @click="EB">刷新</button>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-card-head">
          <span class="chart-card-label">体温</span>
          <span class="chart-card-val" :style="{ color: tempColor(temperature) }">{{ temperature }}<small>℃</small></span>
        </div>
        <div class="chart-container" ref="temperatureChartRef"></div>
        <div class="chart-card-foot">
          <span>最高 {{ maxTemperature }}℃</span>
          <span>最低 {{ minTemperature }}℃</span>
          <button class="btn-mini" @click="ET">刷新</button>
        </div>
      </div>
    </div>

    <!-- 底部面板 -->
    <div class="bottom-panel">

      <div class="fall-card">
        <div class="fall-status" :style="{ color: fallColor(fall) }">
          <span class="fall-dot" :style="{ background: fallColor(fall) }"></span>
          状态：{{ fall }}
        </div>
        <p class="fall-desc">当设备摄像头范围内未出现人时，显示未识别到目标；有人时进行跌倒检测。跌倒时会自动拍照并显示。</p>
        <div class="fall-actions">
          <button class="btn-mini warn">报警</button>
          <button class="btn-mini">请求图片</button>
        </div>
      </div>

      <div class="device-card">
        <div class="device-list">
          <div
            v-for="(machine, index) in Machines.slice(0, 4)"
            :key="index"
            class="device-item"
            :class="{ active: deviceId === machine.connectionId }"
            @click="changeDeviceId(machine)"
          >{{ machine.machines }}</div>
        </div>
        <div class="device-info">
          <div class="device-current">当前显示：{{ showMachine }}</div>
          <p class="device-hint">点击左侧设备来选择查看的设备数据</p>
        </div>
      </div>

      <div class="quick-actions">
        <button class="btn-mini" @click="Reloading">刷新页面</button>
        <button class="btn-mini warn">报警</button>
      </div>

    </div>
  </div>
</template>

<style scoped>
.healthy-root {
  width: 100%; height: 100%;
  padding: 16px 24px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 14px;
  overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.page-header { display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.page-header-left { display: flex; align-items: center; gap: 12px; }
.page-title-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(255,96,64,0.28); flex-shrink: 0;
}
.page-title { font-size: 18px; font-weight: 700; color: #3A2010; letter-spacing: 0.01em; }
.page-sub { font-size: 12px; color: #B09080; margin-top: 2px; }

.btn-reload {
  height: 34px; padding: 0 16px;
  background: #FFF0E8; color: #E06030;
  border: 1px solid rgba(255,140,100,0.3); border-radius: 10px;
  font-size: 12.5px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
}
.btn-reload:hover { background: #FFE4D4; border-color: #FF8A65; }

/* 图表网格 */
.charts-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 12px;
  min-height: 0;
}

.chart-card {
  background: #FFFFFF;
  border-radius: 16px;
  border: 1px solid rgba(255,160,120,0.12);
  box-shadow: 0 2px 12px rgba(200,90,50,0.05);
  display: flex; flex-direction: column;
  padding: 14px 16px 10px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.chart-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(200,90,50,0.1); }

.chart-card-head {
  display: flex; align-items: baseline; justify-content: space-between;
  margin-bottom: 6px; flex-shrink: 0;
}
.chart-card-label { font-size: 13px; font-weight: 700; color: #3A2010; }
.chart-card-val {
  font-size: 20px; font-weight: 800; line-height: 1;
}
.chart-card-val small { font-size: 11px; font-weight: 500; opacity: 0.7; }

.chart-container {
  flex: 1; min-height: 0;
}

.chart-card-foot {
  display: flex; align-items: center; gap: 12px;
  font-size: 11px; color: #B09080; flex-shrink: 0; padding-top: 4px;
}
.chart-card-foot span:last-of-type { margin-right: auto; }

.btn-mini {
  height: 26px; padding: 0 10px; border: none; border-radius: 7px;
  font-size: 11px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.15s ease;
  background: #FFF0E8; color: #D06030;
}
.btn-mini:hover { background: #FFE4D4; }
.btn-mini:active { transform: scale(0.96); }
.btn-mini.warn { background: #FFF0F0; color: #C03030; }
.btn-mini.warn:hover { background: #FFE0E0; }

/* 底部面板 */
.bottom-panel {
  display: flex; gap: 12px; flex-shrink: 0;
  height: 120px;
}

.fall-card {
  width: 28%; background: #FFFFFF;
  border-radius: 14px; padding: 12px 16px;
  border: 1px solid rgba(255,160,120,0.12);
  box-shadow: 0 2px 12px rgba(200,90,50,0.05);
  display: flex; flex-direction: column; gap: 6px;
}
.fall-status { font-size: 16px; font-weight: 800; display: flex; align-items: center; gap: 7px; }
.fall-dot { width: 8px; height: 8px; border-radius: 50%; animation: blink 2s ease infinite; }
.fall-desc { font-size: 11px; color: #B09080; line-height: 1.5; margin: 0; flex: 1; }
.fall-actions { display: flex; gap: 8px; }

.device-card {
  width: 28%; background: #FFFFFF;
  border-radius: 14px; border: 1px solid rgba(255,160,120,0.12);
  box-shadow: 0 2px 12px rgba(200,90,50,0.05);
  display: flex;
}
.device-list {
  width: 36%; display: flex; flex-direction: column;
  border-right: 1px solid rgba(255,160,120,0.1);
}
.device-item {
  flex: 1; display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600; color: #7A5040;
  cursor: pointer; transition: all 0.15s ease;
  padding: 0 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.device-item:hover { background: #FFF0E8; color: #D06030; }
.device-item.active { background: #FFF0E8; color: #D06030; font-weight: 700; }

.device-info {
  flex: 1; padding: 12px; display: flex; flex-direction: column; justify-content: center;
}
.device-current { font-size: 13px; font-weight: 700; color: #3A2010; }
.device-hint { font-size: 11px; color: #B09080; margin: 4px 0 0; }

.quick-actions {
  width: 8%; background: #FFFFFF;
  border-radius: 14px; border: 1px solid rgba(255,160,120,0.12);
  box-shadow: 0 2px 12px rgba(200,90,50,0.05);
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px;
}

@media (max-width: 1000px) {
  .charts-grid { grid-template-columns: 1fr; }
  .bottom-panel { flex-direction: column; height: auto; }
  .fall-card, .device-card { width: 100%; }
  .quick-actions { width: 100%; flex-direction: row; padding: 12px; }
}
</style>
