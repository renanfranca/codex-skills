<script setup>
defineProps({
  entry: {
    type: Object,
    required: true,
  },
});
</script>

<template>
  <template v-if="entry.segments">
    <template v-for="(segment, index) in entry.segments" :key="index">
      <code v-if="segment.type === 'code'">{{ segment.text }}</code>
      <template v-else>{{ segment.text }}</template>
    </template>
  </template>
  <template v-else>{{ entry.description }}</template>
</template>
