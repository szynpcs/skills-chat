<template>
  <div class="app">
    <!-- 顶部导航 -->
    <header class="topbar">
      <div class="logo">
        <span class="logo-icon">⚡</span>
        <span>Skills Chat</span>
      </div>
      <SkillSelector
        v-if="skills.length"
        :skills="skills"
        v-model="activeSkillId"
      />
      <div v-if="loadError" class="error-badge">{{ loadError }}</div>
    </header>

    <!-- 当前 skill 描述 -->
    <div v-if="activeSkill" class="skill-desc">
      {{ activeSkill.description }}
    </div>

    <!-- 聊天窗口 -->
    <ChatWindow v-if="activeSkillId" :skill-id="activeSkillId" />
    <div v-else class="loading">
      <span>{{ loadError ? '加载失败' : '正在加载 skills...' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SkillSelector from './components/SkillSelector.vue'
import ChatWindow from './components/ChatWindow.vue'
import { fetchSkills } from './api/chat.js'

const skills = ref([])
const activeSkillId = ref('')
const loadError = ref('')

const activeSkill = computed(() =>
  skills.value.find(s => s.id === activeSkillId.value)
)

onMounted(async () => {
  try {
    skills.value = await fetchSkills()
    if (skills.value.length > 0) {
      activeSkillId.value = skills.value[0].id
    }
  } catch (e) {
    loadError.value = '无法连接后端，请检查 FastAPI 是否启动'
  }
})
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg);
}

.topbar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}
.logo-icon { font-size: 20px; }

.error-badge {
  margin-left: auto;
  font-size: 12px;
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid rgba(255, 107, 107, 0.3);
}

.skill-desc {
  padding: 8px 20px;
  font-size: 12px;
  color: var(--text-muted);
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 0;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: var(--text-muted);
  font-size: 15px;
}
</style>
