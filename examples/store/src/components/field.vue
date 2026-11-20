<script setup lang="ts">
// A field of a form with its label, and the server's reason when it refused the value.
const value = defineModel<string>({ required: true });
defineProps<{
  name: string;
  label: string;
  error?: string;
  type?: string;
  autocomplete?: string;
  maxlength?: number;
}>();
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label :for="`field-${name}`" class="text-sm font-medium">{{ label }}</label>
    <input
      :id="`field-${name}`"
      v-model="value"
      :name="name"
      :type="type ?? 'text'"
      :autocomplete="autocomplete"
      :maxlength="maxlength"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="error ? `field-${name}-error` : undefined"
      class="min-h-12 border border-border-second bg-background px-4 text-base text-foreground focus:border-foreground focus:outline-none aria-[invalid=true]:border-danger"
    />
    <p v-if="error" :id="`field-${name}-error`" class="text-sm text-danger">{{ error }}</p>
  </div>
</template>
