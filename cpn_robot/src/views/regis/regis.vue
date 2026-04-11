<script setup>
import { ref } from 'vue';
import { RegisApi } from '@/api/users.js';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

const router = useRouter()
let log = ref("注 册")
let loading = ref(false)
let username = ref('');
let password = ref('');
let sure_password = ref('');
let phoneNumber = ref('');

const GoToLogin = () => { router.push({ path: '/login' }) }

const regis = async () => {
    if (loading.value) return;
    if (!username.value || !password.value || !sure_password.value) {
        ElMessage.warning("请输入完整内容"); return;
    }
    if (password.value !== sure_password.value) {
        ElMessage.warning("两次密码输入不一致"); return;
    }
    loading.value = true;
    log.value = "注册中…";
    const RegisInfo = { username: username.value, phoneNumber: phoneNumber.value, password: password.value };
    const result = await RegisApi(RegisInfo);
    if (result.code) {
        log.value = "✓ 成功";
        ElMessage.success("注册成功，即将跳转登录");
        setTimeout(() => GoToLogin(), 1000);
    } else {
        ElMessage.error(result.msg);
        log.value = "注 册";
        loading.value = false;
    }
}

const handleKeydown = (e) => { if (e.key === 'Enter') regis(); }
</script>

<template>
  <div class="regis-root">

    <div class="bg-image"></div>
    <div class="bg-overlay"></div>
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>

    <div class="login-card">

      <!-- 左侧品牌区 -->
      <div class="card-brand">
        <div class="brand-inner">
          <div class="brand-logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <path d="M16 4C10 4 5 8.5 5 14c0 8 11 16 11 16s11-8 11-16c0-5.5-5-10-11-10z" fill="rgba(255,255,255,0.2)" stroke="white" stroke-width="1.5"/>
              <path d="M10 15h3.5l2-5 3 10 2-5H23" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="brand-name">智能陪伴</h1>
          <p class="brand-sub">机器人管理平台</p>
          <div class="brand-divider"></div>
          <p class="brand-desc">创建您的账号<br>开始守护您的家人</p>
          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-dot"></div>
              实时健康监测
            </div>
            <div class="feature-item">
              <div class="feature-dot"></div>
              智能事件提醒
            </div>
            <div class="feature-item">
              <div class="feature-dot"></div>
              AI 情感陪伴
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="card-form">
        <div class="form-inner">
          <div class="form-header">
            <h2 class="form-title">创建账号</h2>
            <p class="form-sub">填写以下信息完成注册</p>
          </div>

          <div class="form-fields">
            <div class="field-group">
              <label class="field-label">用户名</label>
              <div class="field-wrap">
                <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="6" r="3" stroke="#C4A898" stroke-width="1.3"/>
                  <path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="#C4A898" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
                <input class="field-input" v-model="username" type="text" placeholder="请设置用户名" @keydown="handleKeydown" autocomplete="username"/>
              </div>
            </div>

            <div class="field-group">
              <label class="field-label">密码</label>
              <div class="field-wrap">
                <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="3" y="7" width="10" height="7" rx="1.5" stroke="#C4A898" stroke-width="1.3"/>
                  <path d="M5 7V5a3 3 0 016 0v2" stroke="#C4A898" stroke-width="1.3" stroke-linecap="round"/>
                  <circle cx="8" cy="10.5" r="1" fill="#C4A898"/>
                </svg>
                <input class="field-input" v-model="password" type="password" placeholder="请设置密码" @keydown="handleKeydown" autocomplete="new-password"/>
              </div>
            </div>

            <div class="field-group">
              <label class="field-label">确认密码</label>
              <div class="field-wrap">
                <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="3" y="7" width="10" height="7" rx="1.5" stroke="#C4A898" stroke-width="1.3"/>
                  <path d="M5 7V5a3 3 0 016 0v2" stroke="#C4A898" stroke-width="1.3" stroke-linecap="round"/>
                  <path d="M6 10.5l1.5 1.5 2.5-2.5" stroke="#C4A898" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <input class="field-input" v-model="sure_password" type="password" placeholder="请再次输入密码"
                  :class="{ 'input-error': sure_password && password !== sure_password, 'input-ok': sure_password && password === sure_password }"
                  @keydown="handleKeydown" autocomplete="new-password"/>
              </div>
              <span class="field-hint error" v-if="sure_password && password !== sure_password">两次密码不一致</span>
              <span class="field-hint ok" v-if="sure_password && password === sure_password">密码一致 ✓</span>
            </div>

            <div class="field-group">
              <label class="field-label">手机号码 <span class="label-opt">（选填）</span></label>
              <div class="field-wrap">
                <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="4" y="1" width="8" height="14" rx="2" stroke="#C4A898" stroke-width="1.3"/>
                  <circle cx="8" cy="12" r="1" fill="#C4A898"/>
                </svg>
                <input class="field-input" v-model="phoneNumber" type="tel" placeholder="请输入手机号码" @keydown="handleKeydown"/>
              </div>
            </div>
          </div>

          <button class="regis-btn" :class="{ loading }" @click="regis" :disabled="loading">
            <span class="btn-text">{{ log }}</span>
            <div class="btn-shine"></div>
          </button>

          <div class="form-footer">
            <span class="footer-text">已有账号？</span>
            <span class="footer-link" @click="GoToLogin">返回登录</span>
          </div>
        </div>
      </div>

    </div>

    <div class="page-footer">智能陪伴机器人管理平台 · 安全 · 贴心 · 专业</div>

  </div>
</template>

<style scoped>
.regis-root {
  width: 100vw; height: 100vh;
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.bg-image {
  position: absolute; inset: 0;
  background: url("http://localhost:8080/images/index_picture.png") center / cover no-repeat;
  transform: scale(1.05);
  filter: brightness(0.75) saturate(0.9);
}
.bg-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(80,30,10,0.55) 0%, rgba(160,70,20,0.35) 50%, rgba(40,15,5,0.6) 100%);
}
.bg-orb { position: absolute; border-radius: 50%; pointer-events: none; filter: blur(80px); }
.orb-1 { width: 600px; height: 600px; top: -200px; left: -150px; background: radial-gradient(circle, rgba(255,150,80,0.2) 0%, transparent 70%); }
.orb-2 { width: 500px; height: 500px; bottom: -150px; right: -100px; background: radial-gradient(circle, rgba(255,120,60,0.15) 0%, transparent 70%); }

/* 卡片 */
.login-card {
  position: relative; z-index: 10;
  width: min(900px, 90vw);
  height: min(600px, 90vh);
  display: flex;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 28px; overflow: hidden;
  backdrop-filter: blur(24px);
  box-shadow: 0 32px 80px rgba(20,8,2,0.5), 0 0 0 1px rgba(255,255,255,0.08) inset;
  animation: cardIn 0.7s cubic-bezier(0.34,1.4,0.64,1) both;
}
@keyframes cardIn {
  from { opacity:0; transform:translateY(32px) scale(0.96); }
  to   { opacity:1; transform:translateY(0) scale(1); }
}

/* 左侧品牌 */
.card-brand {
  width: 42%; flex-shrink: 0;
  background: linear-gradient(160deg, rgba(255,120,60,0.35) 0%, rgba(180,60,10,0.45) 100%);
  border-right: 1px solid rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center;
  padding: 48px 40px; position: relative; overflow: hidden;
}
.card-brand::before {
  content: ''; position: absolute; top: -60px; right: -60px;
  width: 220px; height: 220px; border-radius: 50%;
  background: rgba(255,200,150,0.08); pointer-events: none;
}
.card-brand::after {
  content: ''; position: absolute; bottom: -40px; left: -40px;
  width: 160px; height: 160px; border-radius: 50%;
  background: rgba(255,160,100,0.06); pointer-events: none;
}
.brand-inner { display: flex; flex-direction: column; align-items: flex-start; position: relative; z-index: 1; }
.brand-logo {
  width: 60px; height: 60px; border-radius: 18px;
  background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}
.brand-name { font-size: 32px; font-weight: 800; color: white; letter-spacing: -0.01em; margin: 0 0 4px; line-height: 1; }
.brand-sub { font-size: 14px; color: rgba(255,255,255,0.65); margin: 0 0 20px; letter-spacing: 0.04em; }
.brand-divider { width: 40px; height: 2px; border-radius: 1px; background: linear-gradient(90deg, rgba(255,200,150,0.8), transparent); margin-bottom: 16px; }
.brand-desc { font-size: 13.5px; color: rgba(255,255,255,0.55); line-height: 1.8; margin: 0 0 24px; }
.brand-features { display: flex; flex-direction: column; gap: 10px; }
.feature-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: rgba(255,255,255,0.7); }
.feature-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; background: rgba(255,200,150,0.9); box-shadow: 0 0 6px rgba(255,200,150,0.5); }

/* 右侧表单 */
.card-form {
  flex: 1; background: rgba(255,252,248,0.96);
  display: flex; align-items: center; justify-content: center;
  padding: 40px 44px; overflow-y: auto;
}
.card-form::-webkit-scrollbar { width: 0; }

.form-inner { width: 100%; max-width: 320px; }
.form-header { margin-bottom: 24px; }
.form-title { font-size: 24px; font-weight: 800; color: #2A1408; letter-spacing: -0.01em; margin: 0 0 6px; }
.form-sub { font-size: 13px; color: #B09080; margin: 0; }

.form-fields { display: flex; flex-direction: column; gap: 13px; margin-bottom: 22px; }
.field-group { display: flex; flex-direction: column; gap: 5px; }
.field-label { font-size: 12.5px; font-weight: 600; color: #6A4030; display: flex; align-items: center; gap: 4px; }
.label-opt { font-weight: 400; color: #C4A898; font-size: 11px; }

.field-wrap { position: relative; display: flex; align-items: center; }
.field-icon { position: absolute; left: 12px; pointer-events: none; flex-shrink: 0; }

.field-input {
  width: 100%; height: 42px;
  padding: 0 14px 0 38px;
  border: 1.5px solid rgba(255,160,120,0.25); border-radius: 12px;
  font-size: 13.5px; font-family: inherit;
  color: #3A2010; background: #FFFAF7; outline: none;
  box-sizing: border-box; transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.field-input:focus { border-color: #FF8A65; background: #FFFFFF; box-shadow: 0 0 0 3px rgba(255,138,101,0.12); }
.field-input::placeholder { color: #C4A898; }
.field-input.input-error { border-color: rgba(200,50,50,0.5); }
.field-input.input-error:focus { border-color: #E03030; box-shadow: 0 0 0 3px rgba(200,50,50,0.1); }
.field-input.input-ok { border-color: rgba(76,175,100,0.5); }
.field-input.input-ok:focus { border-color: #4CAF64; box-shadow: 0 0 0 3px rgba(76,175,100,0.1); }

.field-hint { font-size: 11.5px; padding-left: 2px; }
.field-hint.error { color: #C03030; }
.field-hint.ok { color: #3A8A50; }

/* 注册按钮 */
.regis-btn {
  width: 100%; height: 46px;
  background: linear-gradient(90deg, #FF9A76, #FF5A30);
  color: white; border: none; border-radius: 12px;
  font-size: 15px; font-weight: 700; font-family: inherit;
  cursor: pointer; transition: all 0.25s ease;
  box-shadow: 0 6px 20px rgba(255,90,48,0.35);
  position: relative; overflow: hidden; letter-spacing: 0.06em;
}
.regis-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(255,90,48,0.45); }
.regis-btn:active:not(:disabled) { transform: translateY(0); }
.regis-btn:disabled { opacity: 0.75; cursor: not-allowed; }
.regis-btn.loading { background: linear-gradient(90deg, #FFB090, #FF8060); }

.btn-shine {
  position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: skewX(-20deg); animation: shine 3s ease infinite;
}
@keyframes shine { 0%{ left:-100%; } 40%{ left:140%; } 100%{ left:140%; } }
.btn-text { position: relative; z-index: 1; }

.form-footer { display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 18px; font-size: 13px; }
.footer-text { color: #B09080; }
.footer-link { color: #E07040; font-weight: 600; cursor: pointer; transition: color 0.18s; text-decoration: underline; text-underline-offset: 2px; text-decoration-color: rgba(224,112,64,0.4); }
.footer-link:hover { color: #C05020; }

.page-footer {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  font-size: 11.5px; color: rgba(255,255,255,0.35); white-space: nowrap; z-index: 10; letter-spacing: 0.04em;
}
</style>