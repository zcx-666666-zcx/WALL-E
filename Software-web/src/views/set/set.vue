<script setup>
import { ref } from 'vue'
import { toast } from '../../utils/toast'

const notiSwitch = ref(true)
const autoSwitch = ref(false)
const voiceNotify = ref(true)

const volume = ref(80)
const voiceType = ref('温馨女声')

function clearCache() { toast.success('缓存已清除') }
function feedback() { toast.info('反馈功能即将上线～') }
function about() { toast.success('智能陪伴机器人 v1.0') }
</script>

<template>
  <div class="set-root">

    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="8" cy="8" r="2.5" stroke="white" stroke-width="1.4"/>
            <path d="M8 1.5v2M8 12.5v2M1.5 8h2M12.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M3.4 12.6l1.4-1.4M11.2 4.8l1.4-1.4" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
        </div>
        <div>
          <div class="page-title">系统设置</div>
          <div class="page-sub">个性化配置你的智能陪伴机器人</div>
        </div>
      </div>
    </div>

    <div class="cards-scroll">

      <div class="setting-card">
        <div class="card-title">基础设置</div>
        <div class="item">
          <div>
            <label>音量调节</label>
            <div class="tip">调节机器人提示音大小</div>
          </div>
          <div class="slider-wrap">
            <span class="vol-val">{{ volume }}</span>
            <input type="range" v-model="volume" min="0" max="100" class="slider" />
          </div>
        </div>
        <div class="item">
          <div>
            <label>语音类型</label>
            <div class="tip">选择机器人播报音色</div>
          </div>
          <select v-model="voiceType" class="select">
            <option>温馨女声</option>
            <option>沉稳男声</option>
            <option>可爱童声</option>
            <option>变形金刚</option>
            <option>猫meme</option>
            <option>曼波</option>
          </select>
        </div>
      </div>

      <div class="setting-card">
        <div class="card-title">消息与提醒</div>
        <div class="item">
          <div>
            <label>事件提醒</label>
            <div class="tip">开启后机器人会按时语音提醒</div>
          </div>
          <div class="switch" :class="{ on: notiSwitch }" @click="notiSwitch = !notiSwitch">
            <div class="circle"></div>
          </div>
        </div>
        <div class="item">
          <div>
            <label>开机自动播报</label>
            <div class="tip">开机后自动播报时间与天气</div>
          </div>
          <div class="switch" :class="{ on: autoSwitch }" @click="autoSwitch = !autoSwitch">
            <div class="circle"></div>
          </div>
        </div>
        <div class="item">
          <div>
            <label>操作语音反馈</label>
            <div class="tip">按钮/操作成功时语音提示</div>
          </div>
          <div class="switch" :class="{ on: voiceNotify }" @click="voiceNotify = !voiceNotify">
            <div class="circle"></div>
          </div>
        </div>
      </div>

      <div class="setting-card">
        <div class="card-title">高级设置</div>
        <div class="item clickable" @click="clearCache">
          <div>
            <label>清除缓存</label>
            <div class="tip">释放存储空间</div>
          </div>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="arrow-icon">
            <path d="M5 2l5 5-5 5" stroke="#C4A898" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="item clickable" @click="feedback">
          <div>
            <label>意见反馈</label>
            <div class="tip">帮助我们优化产品</div>
          </div>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="arrow-icon">
            <path d="M5 2l5 5-5 5" stroke="#C4A898" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="item clickable" @click="about">
          <div>
            <label>关于产品</label>
            <div class="tip">查看版本与信息</div>
          </div>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="arrow-icon">
            <path d="M5 2l5 5-5 5" stroke="#C4A898" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>

      <div class="setting-card">
        <div class="card-title">账号管理</div>
        <div class="item clickable logout-item" @click="$router.push('/login')">
          <div>
            <label class="logout-label">退出登录</label>
            <div class="tip">退出当前账号，返回登录页</div>
          </div>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="arrow-icon" style="color:#E57373">
            <path d="M5 2l5 5-5 5" stroke="#E57373" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.set-root {
  width: 100%; height: 100%;
  padding: 20px 24px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 16px;
  overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.page-header { display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.page-header-left { display: flex; align-items: center; gap: 12px; }
.page-title-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: var(--grad-primary);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(255,96,64,0.28); flex-shrink: 0;
}
.page-title { font-size: 18px; font-weight: 700; color: #3A2010; letter-spacing: 0.01em; }
.page-sub { font-size: 12px; color: #B09080; margin-top: 2px; }

.cards-scroll {
  flex: 1; overflow-y: auto;
  display: flex; flex-direction: column; gap: 14px;
  padding-bottom: 40px;
}

.setting-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px 24px;
  border: 1px solid rgba(255,160,120,0.12);
  box-shadow: 0 2px 12px rgba(200,90,50,0.05);
}

.card-title {
  font-size: 14px; font-weight: 700; color: #3A2010;
  margin-bottom: 14px; padding-bottom: 12px;
  border-bottom: 1px solid rgba(255,160,120,0.1);
}

.item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255,160,120,0.06);
  transition: background 0.15s;
}
.item:last-child { border-bottom: none; }

.item.clickable { cursor: pointer; border-radius: 8px; padding: 12px 8px; margin: 0 -8px; }
.item.clickable:hover { background: #FFF8F5; }
.item.clickable:hover .arrow-icon { transform: translateX(3px); }
.arrow-icon { transition: transform 0.2s ease; }

.item label { font-size: 14px; font-weight: 600; color: #3A2010; display: block; }
.item .tip { font-size: 11.5px; color: #B09080; margin-top: 3px; }

.logout-label { color: #E57373 !important; }
.logout-item:hover { background: #FFF5F5 !important; }

/* 滑块 */
.slider-wrap { display: flex; align-items: center; gap: 10px; }
.vol-val {
  font-size: 13px; font-weight: 700; color: #FF6040;
  min-width: 32px; text-align: right;
}
.slider {
  width: 120px; height: 6px;
  appearance: none; -webkit-appearance: none;
  background: linear-gradient(90deg, #FFD4B8, #FF9A76);
  border-radius: 100px; outline: none; cursor: pointer;
}
.slider::-webkit-slider-thumb {
  appearance: none; -webkit-appearance: none;
  width: 18px; height: 18px;
  background: white;
  border: 2px solid #FF8A65;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(255,96,64,0.25);
  transition: transform 0.15s;
  cursor: pointer;
}
.slider::-webkit-slider-thumb:hover { transform: scale(1.15); }

/* 下拉 */
.select {
  padding: 8px 14px;
  border: 1px solid rgba(255,160,120,0.3);
  border-radius: 10px; outline: none;
  font-size: 13px; font-family: inherit;
  color: #3A2010; background: #FFFAF7;
  cursor: pointer; transition: border-color 0.2s;
}
.select:focus { border-color: #FF8A65; }

/* 开关 */
.switch {
  width: 48px; height: 28px;
  background: #E0D5CE;
  border-radius: 100px; position: relative;
  transition: background 0.3s ease; cursor: pointer;
  flex-shrink: 0;
}
.switch.on { background: linear-gradient(90deg, #FFB899, #FF8A65); }
.circle {
  width: 22px; height: 22px; background: white;
  border-radius: 50%; position: absolute;
  top: 3px; left: 3px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
  transition: left 0.3s cubic-bezier(0.34, 1.4, 0.64, 1);
}
.switch.on .circle { left: 23px; }

@media (max-width: 600px) {
  .set-root { padding: 12px; }
  .setting-card { padding: 16px; }
  .slider { width: 80px; }
}
</style>
