<script setup>
import { ref } from 'vue'

const activeKey = ref('element')

const sections = {
  element: {
    icon: `<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="2" y="1" width="14" height="16" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M5 6h8M5 9.5h8M5 13h5" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>`,
    label: '事件提醒', title: '事件提醒', sub: '让机器人成为贴心的日程助手',
    badge: '常用功能', badgeColor: '#4CAF84',
    content: [
      { type: 'section', heading: '应用场景', text: '通过在小程序或网页中添加事件，让机器人在指定时间为用户进行语音提示，避免遗忘重要事项。可作为记事本或智能闹钟使用，特别适合记忆力减退的老年用户。' },
      { type: 'section', heading: '使用方法', text: '在网页端「事件管理」或微信小程序「事件」页中，查看已设置的事件，并对其进行管理，包括新增事件、编辑事件或删除事件等操作。' },
      { type: 'fields', heading: '字段说明', items: [
        { label: '事件名称', desc: '在小程序和网页端显示，便于识别' },
        { label: '事件优先级', desc: '同一时间多个事件时，按优先级从高到低依次提醒。不建议同一时间设置超过 3 个事件' },
        { label: '事件描述', desc: '机器人触发时实际播报的语音内容，请填写完整句子' },
        { label: '绑定设备', desc: '需将事件绑定给具体设备才可生效，设备号可在「设备管理」中查看' },
      ]},
      { type: 'tip', text: '可在「命令查询」中查看事件是否被成功触发，以验证设置是否生效。' }
    ]
  },
  agent: {
    icon: `<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="3" y="5" width="12" height="9" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M6 5V4a3 3 0 016 0v1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="7" cy="10" r="1" fill="currentColor"/><circle cx="11" cy="10" r="1" fill="currentColor"/></svg>`,
    label: '智能陪聊', title: '智能陪聊', sub: '为长辈定制专属的 AI 伴侣',
    badge: 'AI 功能', badgeColor: '#7B61FF',
    content: [
      { type: 'section', heading: '应用场景', text: '通过自定义 AI 人设，让机器人以特定的风格与用户进行日常对话，缓解老年人的孤独感，提供情感陪伴与互动。' },
      { type: 'section', heading: '使用方法', text: '在「AI 设置」页面描述希望 AI 呈现的性格和说话风格。建议先点击「获取当前人设」查看已有设置，再在其基础上修改后提交。' },
      { type: 'fields', heading: '设置建议', items: [
        { label: '用户信息', desc: '描述被陪护者的基本情况，如年龄、性别、爱好等' },
        { label: 'AI 性格', desc: '设定 AI 的说话风格，如温和、幽默、耐心等' },
        { label: '互动习惯', desc: '例如：每次说完话询问对方感受，主动分享话题等' },
      ]},
      { type: 'tip', text: '可在「聊天调试窗口」中测试人设效果，满意后再正式投入使用。' }
    ]
  },
  safe: {
    icon: `<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 2C6 2 3 4 3 7c0 5 6 9 6 9s6-4 6-9c0-3-3-5-6-5z" stroke="currentColor" stroke-width="1.5"/><path d="M6 9h1.5l1-2 1.5 4 1-2H13" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    label: '安全监测', title: '安全监测', sub: '实时守护长辈的身体健康',
    badge: '核心功能', badgeColor: '#FF6040',
    content: [
      { type: 'section', heading: '应用场景', text: '通过机器人内置传感器，实时采集被监护者的心率、体温、呼吸频率、体表湿度等生命体征数据，并在异常时自动触发报警。' },
      { type: 'section', heading: '使用方法', text: '进入「状态监测」页面，选择对应设备后即可查看实时数据。页面每 2 秒自动刷新一次，数据异常时指标卡片将自动变色提示。' },
      { type: 'fields', heading: '监测指标', items: [
        { label: '心率', desc: '正常范围 60–100 次/分；高于 120 为注意，高于 170 为异常' },
        { label: '体温', desc: '正常范围 35.9–37.0℃；高于 37.1℃ 提示发热' },
        { label: '呼吸频率', desc: '正常范围 12–29 次/分，低于 12 或高于 30 为异常' },
        { label: '跌倒检测', desc: '摄像头持续识别姿态，跌倒时自动拍照并触发报警' },
      ]},
      { type: 'tip', text: '若数据长期显示「—」，请检查设备是否在线，以及传感器是否正确佩戴。' }
    ]
  },
  video: {
    icon: `<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="1" y="4" width="11" height="10" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M12 7l5-2.5v9L12 11V7z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>`,
    label: '远程通话', title: '远程通话', sub: '随时查看长辈的实时画面',
    badge: '监护功能', badgeColor: '#2196F3',
    content: [
      { type: 'section', heading: '应用场景', text: '通过 WebRTC 技术实现家属端与机器人端的实时视频连接，家属可随时查看被监护者的实时状态，也可与其进行视频通话。' },
      { type: 'section', heading: '使用方法', text: '进入「远程监护」页面，输入与机器人端一致的房间号，点击「加入房间」完成连接。待摄像头启动后，点击「请求监视」即可接收远端画面。' },
      { type: 'fields', heading: '注意事项', items: [
        { label: '房间号', desc: '需与机器人端保持一致，默认为 0001' },
        { label: '网络要求', desc: '建议双方均使用稳定的 Wi-Fi 网络，以保障画面流畅' },
        { label: '摄像头权限', desc: '首次使用需在浏览器弹窗中允许访问摄像头和麦克风' },
      ]},
      { type: 'tip', text: '若连接失败，请确认机器人已上线，并刷新页面重试。' }
    ]
  },
  drive: {
    icon: `<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="5" y="2" width="8" height="14" rx="2" stroke="currentColor" stroke-width="1.5"/><circle cx="9" cy="13" r="1.8" stroke="currentColor" stroke-width="1.3"/><path d="M9 5v3M7.5 6.5h3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>`,
    label: '远程遥控', title: '远程遥控', sub: '远程操控机器人的移动与动作',
    badge: '控制功能', badgeColor: '#FF9800',
    content: [
      { type: 'section', heading: '应用场景', text: '通过网页界面远程控制机器人的移动方向和动作，适用于需要引导机器人到达特定位置，或远程操作机器人执行任务的场景。' },
      { type: 'section', heading: '使用方法', text: '点击左侧菜单中的「远程遥控」，系统将在新标签页中打开遥控界面。确保机器人已上线后，即可通过方向键控制移动。' },
      { type: 'tip', text: '远程遥控对网络延迟较敏感，建议在低延迟网络环境下使用，操作时请确保机器人周围无障碍物。' }
    ]
  },
  more: {
    icon: `<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="1.5"/><path d="M9 8v5M9 5.5v.5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>`,
    label: '更多功能', title: '更多功能', sub: '持续迭代，敬请期待',
    badge: '即将上线', badgeColor: '#9E9E9E',
    content: [
      { type: 'section', heading: '开发计划', text: '我们正在持续优化和扩展平台功能，以下功能正在开发中，敬请期待。' },
      { type: 'fields', heading: '规划功能', items: [
        { label: '健康报告', desc: '自动生成周期性健康趋势报告，可导出分享给家属或医生' },
        { label: '紧急联系', desc: '异常事件发生时，自动向紧急联系人发送通知' },
        { label: '小程序同步', desc: '微信小程序与网页端数据实时同步，随时随地掌握状态' },
        { label: '多设备管理', desc: '支持同时管理多台机器人设备，适合养老机构场景' },
      ]},
      { type: 'tip', text: '如有功能建议，欢迎向开发团队反馈，您的意见将直接影响产品迭代方向。' }
    ]
  }
}

const current = ref(sections.element)
const select = (key) => { activeKey.value = key; current.value = sections[key] }
</script>

<template>
  <div class="help-root">

    <div class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-icon">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <rect x="1" y="1" width="12" height="12" rx="2" stroke="white" stroke-width="1.3"/>
            <path d="M3.5 4.5h7M3.5 7h7M3.5 9.5h4" stroke="white" stroke-width="1.2" stroke-linecap="round"/>
          </svg>
        </div>
        使用说明
      </div>

      <nav class="sidebar-nav">
        <div v-for="(sec, key) in sections" :key="key" class="nav-item" :class="{ active: activeKey === key }" @click="select(key)">
          <span class="nav-icon" v-html="sec.icon"></span>
          <span class="nav-label">{{ sec.label }}</span>
          <svg v-if="activeKey === key" width="12" height="12" viewBox="0 0 12 12" fill="none" class="nav-chevron">
            <path d="M4 2l4 4-4 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </nav>

      <div class="sidebar-footer">
        <div class="footer-dot"></div>
        智能陪伴机器人平台
      </div>
    </div>

    <div class="content-area">
      <transition name="slide-fade" mode="out-in">
        <div :key="activeKey" class="content-inner">

          <div class="doc-header">
            <div class="doc-badge" :style="{ background: current.badgeColor + '18', color: current.badgeColor, borderColor: current.badgeColor + '30' }">
              {{ current.badge }}
            </div>
            <h1 class="doc-title">{{ current.title }}</h1>
            <p class="doc-sub">{{ current.sub }}</p>
            <div class="doc-divider"></div>
          </div>

          <div class="doc-body">
            <template v-for="(block, i) in current.content" :key="i">

              <div v-if="block.type === 'section'" class="doc-section">
                <div class="section-heading">
                  <div class="heading-bar"></div>
                  {{ block.heading }}
                </div>
                <p class="section-text">{{ block.text }}</p>
              </div>

              <div v-if="block.type === 'fields'" class="doc-section">
                <div class="section-heading">
                  <div class="heading-bar"></div>
                  {{ block.heading }}
                </div>
                <div class="fields-list">
                  <div class="field-item" v-for="(item, j) in block.items" :key="j">
                    <div class="field-label">{{ item.label }}</div>
                    <div class="field-desc">{{ item.desc }}</div>
                  </div>
                </div>
              </div>

              <div v-if="block.type === 'tip'" class="tip-box">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style="flex-shrink:0;margin-top:1px">
                  <circle cx="8" cy="8" r="6.5" stroke="#E07040" stroke-width="1.3"/>
                  <path d="M8 7v4M8 5.5v.5" stroke="#E07040" stroke-width="1.4" stroke-linecap="round"/>
                </svg>
                <span>{{ block.text }}</span>
              </div>

            </template>
          </div>

        </div>
      </transition>
    </div>

  </div>
</template>

<style scoped>
.help-root {
  width: 100%; height: 100%;
  display: flex; overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  background: #FBF5F0;
}

/* 侧边栏 */
.sidebar {
  width: 200px; flex-shrink: 0;
  background: #FFFFFF;
  border-right: 1px solid rgba(255,160,120,0.12);
  box-shadow: 2px 0 16px rgba(200,100,60,0.05);
  display: flex; flex-direction: column; overflow: hidden;
}
.sidebar-header {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 16px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  font-size: 13px; font-weight: 700; color: white; flex-shrink: 0;
}
.sidebar-icon {
  width: 26px; height: 26px; border-radius: 7px;
  background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.sidebar-nav { flex: 1; padding: 8px; display: flex; flex-direction: column; gap: 2px; overflow-y: auto; }
.sidebar-nav::-webkit-scrollbar { width: 0; }

.nav-item {
  display: flex; align-items: center; gap: 9px;
  padding: 10px 11px; border-radius: 10px;
  cursor: pointer; transition: all 0.2s ease;
  color: #7A5040; font-size: 13px; font-weight: 500;
}
.nav-item:hover { background: #FFF0E8; color: #C05020; }
.nav-item.active {
  background: linear-gradient(90deg, #FFF0E8, #FFE8DC);
  color: #C05020; font-weight: 700;
  border: 1px solid rgba(255,150,100,0.2);
}
.nav-icon { width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav-label { flex: 1; }
.nav-chevron { color: #E07050; opacity: 0.7; }

.sidebar-footer {
  display: flex; align-items: center; gap: 7px;
  padding: 12px 16px;
  border-top: 1px solid rgba(255,160,120,0.12);
  font-size: 11px; color: #C4A898; flex-shrink: 0;
}
.footer-dot { width: 6px; height: 6px; border-radius: 50%; background: #5AB060; animation: blink 2s ease infinite; flex-shrink: 0; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }

/* 内容区 */
.content-area { flex: 1; overflow-y: auto; padding: 36px 44px; }
.content-area::-webkit-scrollbar { width: 5px; }
.content-area::-webkit-scrollbar-thumb { background: rgba(255,160,120,0.25); border-radius: 4px; }
.content-inner { max-width: 680px; }

/* 文档头部 */
.doc-header { margin-bottom: 30px; }
.doc-badge {
  display: inline-flex; align-items: center;
  font-size: 11.5px; font-weight: 600;
  border-radius: 100px; padding: 3px 12px;
  border: 1px solid transparent; margin-bottom: 12px;
}
.doc-title { font-size: 26px; font-weight: 800; color: #2A1408; letter-spacing: -0.01em; margin: 0 0 8px; }
.doc-sub { font-size: 13.5px; color: #B09080; margin: 0 0 20px; }
.doc-divider { height: 1px; background: linear-gradient(90deg, rgba(255,160,100,0.25), transparent); }

/* 文档正文 */
.doc-body { display: flex; flex-direction: column; gap: 26px; }
.doc-section { display: flex; flex-direction: column; gap: 12px; }
.section-heading {
  display: flex; align-items: center; gap: 8px;
  font-size: 14.5px; font-weight: 700; color: #3A2010;
}
.heading-bar { width: 3px; height: 15px; border-radius: 2px; background: linear-gradient(180deg, #FF9A76, #FF6040); flex-shrink: 0; }

.section-text {
  font-size: 13.5px; color: #6A4030; line-height: 1.85;
  margin: 0; padding-left: 11px;
  border-left: 1px solid rgba(255,160,100,0.15);
}

.fields-list { display: flex; flex-direction: column; gap: 7px; padding-left: 11px; }
.field-item {
  background: #FFFAF7; border: 1px solid rgba(255,160,100,0.14);
  border-radius: 10px; padding: 11px 15px;
  display: flex; align-items: baseline; gap: 14px;
  transition: border-color 0.18s;
}
.field-item:hover { border-color: rgba(255,140,80,0.28); }
.field-label {
  font-size: 12px; font-weight: 700; color: #C05020;
  min-width: 68px; flex-shrink: 0;
  background: rgba(255,150,100,0.1); border-radius: 6px;
  padding: 2px 8px; text-align: center;
}
.field-desc { font-size: 13px; color: #6A4030; line-height: 1.65; }

.tip-box {
  display: flex; gap: 10px; align-items: flex-start;
  background: #FFF8F4;
  border: 1px solid rgba(255,150,100,0.18);
  border-left: 3px solid #FF9A76;
  border-radius: 0 10px 10px 0;
  padding: 12px 16px;
  font-size: 13px; color: #8A4030; line-height: 1.7;
}

/* 过渡 */
.slide-fade-enter-active { transition: all 0.22s ease; }
.slide-fade-leave-active { transition: all 0.16s ease; }
.slide-fade-enter-from { opacity: 0; transform: translateX(10px); }
.slide-fade-leave-to   { opacity: 0; transform: translateX(-6px); }
</style>