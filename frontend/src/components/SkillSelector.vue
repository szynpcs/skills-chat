<template>
  <div class="skill-selector">
    <label>角色 / Skill</label>
    <select :value="modelValue" @change="$emit('update:modelValue', $event.target.value)">
      <option v-for="s in skills" :key="s.id" :value="s.id">{{ s.name }}</option>
    </select>
  </div>
</template>

<script setup>
defineProps({
  skills: Array,
  modelValue: String,
})
defineEmits(['update:modelValue'])
</script>

<style scoped>
.skill-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}
label {
  font-size: 13px;
  color: var(--text-muted);
  white-space: nowrap;
}
select {
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
}
select:focus {
  border-color: var(--primary);
}
</style>
