<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

// Sits under a password field of a server form, in the same wrapper. The form works without it; once it runs it
// adds a Show button, and, for a new password (`data-strength`), how hard it is to guess. It never
// refuses a password: the server alone decides, with the same rule for everyone.
const COMMON = ["password", "12345678", "123456789", "qwertyuiop", "iloveyou", "kestrel123"];
const LABELS = ["Too short", "Easy to guess", "Fair", "Good", "Strong"];

const root = ref<HTMLElement | null>(null);
const field = ref<HTMLInputElement | null>(null);
const value = ref("");
const shown = ref(false);
const measured = ref(false);

function score(password: string): number {
  if (password.length < 8) return 0;
  if (COMMON.includes(password.toLowerCase())) return 1;
  const kinds = [/[a-z]/, /[A-Z]/, /[0-9]/, /[^a-zA-Z0-9]/].filter((kind) => kind.test(password)).length;
  const length = password.length >= 16 ? 3 : password.length >= 12 ? 2 : 1;
  return Math.min(4, length + (kinds >= 3 ? 1 : 0));
}

const strength = computed(() => score(value.value));

onMounted(() => {
  // The island and its field share a wrapper: the island's container (no box of its own) is a
  // child of it, and so is the field.
  const wrapper = root.value?.parentElement?.parentElement;
  const input = wrapper?.querySelector("input[data-password]");
  if (!(input instanceof HTMLInputElement)) return;
  field.value = input;
  measured.value = input.hasAttribute("data-strength");
  input.addEventListener("input", () => (value.value = input.value));
});

function toggle() {
  if (!field.value) return;
  shown.value = !shown.value;
  field.value.type = shown.value ? "text" : "password";
  field.value.focus();
}
</script>

<template>
  <div ref="root" class="mt-1.5 flex items-center gap-3">
    <template v-if="field">
      <div v-if="measured" class="flex min-w-0 flex-1 items-center gap-2">
        <div class="flex flex-1 gap-1" aria-hidden="true">
          <span v-for="n in 4" :key="n" class="h-1.5 flex-1 rounded-full" :class="n <= strength ? `meter-${strength}` : 'bg-border'" />
        </div>
        <span class="w-28 text-right text-xs text-foreground-second" aria-live="polite">{{ value ? LABELS[strength] : "" }}</span>
      </div>
      <button type="button" class="ml-auto flex min-h-11 items-center px-1 text-xs font-medium text-accent underline underline-offset-4" :aria-pressed="shown" @click="toggle">
        {{ shown ? "Hide password" : "Show password" }}
      </button>
    </template>
  </div>
</template>
