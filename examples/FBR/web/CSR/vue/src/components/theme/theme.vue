
<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';
import ThemeButton from './themeButton.vue';
import SunIcon from './sunIcon.vue';
import MoonIcon from './moonIcon.vue';
import MonitorIcon from './monitorIcon.vue';

type ThemeMode = 'light' | 'dark' | 'system';
const active = ref<ThemeMode>((localStorage.getItem('nexy-theme') as ThemeMode) || 'system');
const containerRef = ref<HTMLDivElement | null>(null);
const applyTheme = (isDark: boolean) => { document.documentElement.classList.toggle('dark', isDark); };
const updateThemeLogic = () => {
  localStorage.setItem('nexy-theme', active.value);
  if (active.value === 'system') { applyTheme(window.matchMedia('(prefers-color-scheme: dark)').matches); }
  else { applyTheme(active.value === 'dark'); }
};
const updateSlider = async () => {
  await nextTick();
  const el = containerRef.value?.querySelector(`[data-mode="${active.value}"]`) as HTMLElement;
  if (el) {
    const root = document.documentElement;
    root.style.setProperty('--slider-left', `${el.offsetLeft}px`);
    root.style.setProperty('--slider-width', `${el.offsetWidth}px`);
  }
};
watch(active, () => { updateThemeLogic(); updateSlider(); }, { immediate: true });
onMounted(() => {
  updateSlider();
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (active.value === 'system') updateThemeLogic();
  });
});
</script>
<template>
  <div ref="containerRef" class="relative flex justify-center items-center p-1 gap-0.5 border border-border rounded-full size-fit transition-colors">
    <div class="absolute left-0 size-7 bg-foreground rounded-full transition-all duration-300 ease-in-out" :style="{ transform: `translateX(var(--slider-left))`, width: `var(--slider-width)` }" />
    <ThemeButton mode="light" :active="active" @click="active = 'light'"><SunIcon /></ThemeButton>
    <ThemeButton mode="dark" :active="active" @click="active = 'dark'"><MoonIcon /></ThemeButton>
    <ThemeButton mode="system" :active="active" @click="active = 'system'"><MonitorIcon /></ThemeButton>
  </div>
</template>
