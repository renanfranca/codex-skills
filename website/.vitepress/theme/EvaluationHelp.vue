<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { evaluationGlossary } from '../../scripts/evaluation-glossary.mjs';
import GlossaryDescription from './GlossaryDescription.vue';

const props = defineProps({
  context: { type: String, default: 'report' },
  field: { type: String, default: '' },
  current: { type: String, default: 'Not recorded' },
  detail: { type: String, default: '' },
  guide: { type: Boolean, default: false },
});

const open = ref(false);
const mobile = ref(false);
const trigger = ref(null);
const panel = ref(null);
const panelStyle = ref({});
const panelId = `evaluation-help-${Math.random().toString(36).slice(2)}`;
let mediaQuery;

const definition = computed(() =>
  props.context === 'evaluation'
    ? (evaluationGlossary.evaluationPage.fields[props.field] ?? null)
    : (evaluationGlossary.fields[props.field] ?? evaluationGlossary.observationFields[props.field] ?? null),
);
const taxonomy = computed(() => {
  if (props.context === 'evaluation' && props.field === 'suiteState') return evaluationGlossary.evaluationPage.suiteStates;
  if (props.context === 'evaluation' && props.field === 'currentEvidence') return evaluationGlossary.caseEvidenceStatuses;
  if (props.context === 'evaluation' && props.field === 'kind') return evaluationGlossary.kinds;
  if (props.context === 'evaluation') return null;
  if (props.field === 'failureCategory') return evaluationGlossary.failureCategories;
  if (props.field === 'result') return evaluationGlossary.results;
  if (props.field === 'kind') return evaluationGlossary.kinds;
  if (props.field === 'role') return evaluationGlossary.roles;
  if (props.field === 'judge') return { ...evaluationGlossary.judgeStates, ...evaluationGlossary.judgeVerdicts };
  return null;
});
const guideGroups = Object.freeze([
  {
    title: 'How an evaluation is produced',
    entries: [
      evaluationGlossary.runner,
      evaluationGlossary.executor,
      evaluationGlossary.judge,
      evaluationGlossary.modelSession,
      evaluationGlossary.concepts.evidenceStatus,
      ...Object.entries(evaluationGlossary.evidenceStatuses).map(([code, value]) => ({ ...value, code })),
      evaluationGlossary.concepts.operationType,
      evaluationGlossary.concepts.recordedResult,
    ],
  },
  { title: 'Operations', entries: Object.entries(evaluationGlossary.operations).map(([key, value]) => ({ ...value, code: key })) },
  {
    title: 'Execution facts',
    entries: [
      ...Object.entries(evaluationGlossary.fields)
        .filter(([key]) => key !== 'sessions')
        .map(([, value]) => value),
      ...Object.entries(evaluationGlossary.failureCategories).map(([key, value]) => ({
        ...value,
        code: key === 'none' ? 'null' : key,
      })),
    ],
  },
  {
    title: 'Observations',
    entries: [
      ...Object.entries(evaluationGlossary.results).map(([code, value]) => ({ ...value, code })),
      ...Object.entries(evaluationGlossary.kinds).map(([code, value]) => ({ ...value, code })),
      ...Object.entries(evaluationGlossary.roles).map(([code, value]) => ({ ...value, code })),
      ...Object.entries(evaluationGlossary.judgeStates).map(([code, value]) => ({ ...value, code })),
      ...Object.entries(evaluationGlossary.judgeVerdicts).map(([code, value]) => ({ ...value, code })),
    ],
  },
]);

function updateMode() {
  mobile.value = mediaQuery.matches;
  updatePosition();
}

async function updatePosition() {
  if (!open.value || mobile.value || props.guide || !trigger.value) {
    panelStyle.value = {};
    return;
  }
  const width = Math.min(400, window.innerWidth - 32);
  const initialBounds = trigger.value.getBoundingClientRect();
  const initialLeft = Math.max(16, Math.min(initialBounds.left, window.innerWidth - width - 16));
  panelStyle.value = {
    ...panelStyle.value,
    width: `${width}px`,
    left: `${initialLeft}px`,
  };
  await nextTick();
  if (!open.value || mobile.value || props.guide || !trigger.value || !panel.value) return;

  const bounds = trigger.value.getBoundingClientRect();
  const left = Math.max(16, Math.min(bounds.left, window.innerWidth - width - 16));
  const panelHeight = panel.value?.getBoundingClientRect().height ?? 0;
  const below = bounds.bottom + 10;
  const above = bounds.top - panelHeight - 10;
  const top = below + panelHeight <= window.innerHeight - 16 ? below : Math.max(16, above);
  panelStyle.value = {
    width: `${width}px`,
    top: `${top}px`,
    left: `${left}px`,
  };
}

async function show() {
  open.value = true;
  await nextTick();
  await updatePosition();
  panel.value?.focus();
}

function close({ restoreFocus = true } = {}) {
  open.value = false;
  if (restoreFocus) nextTick(() => trigger.value?.focus());
}

function handleDocumentClick(event) {
  if (!open.value || mobile.value || props.guide) return;
  if (!panel.value?.contains(event.target) && !trigger.value?.contains(event.target)) close();
}

function handleDocumentKey(event) {
  if (open.value && event.key === 'Escape') close();
}

onMounted(() => {
  mediaQuery = window.matchMedia('(max-width: 640px)');
  updateMode();
  mediaQuery.addEventListener('change', updateMode);
  document.addEventListener('click', handleDocumentClick);
  document.addEventListener('keydown', handleDocumentKey);
  window.addEventListener('resize', updatePosition);
  window.addEventListener('scroll', updatePosition, true);
});

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener('change', updateMode);
  document.removeEventListener('click', handleDocumentClick);
  document.removeEventListener('keydown', handleDocumentKey);
  window.removeEventListener('resize', updatePosition);
  window.removeEventListener('scroll', updatePosition, true);
});
</script>

<template>
  <button
    v-if="guide"
    ref="trigger"
    type="button"
    class="evaluation-guide-trigger"
    :aria-expanded="open"
    :aria-controls="panelId"
    @click="show"
  >
    Learn how to read this report
  </button>
  <button v-else ref="trigger" type="button" class="evaluation-field-trigger" :aria-expanded="open" :aria-controls="panelId" @click="show">
    {{ definition?.label ?? field }} <span aria-hidden="true">ⓘ</span>
  </button>

  <Teleport to="body">
    <div v-if="open && (mobile || guide)" class="evaluation-help-backdrop" data-testid="evaluation-help-backdrop" @click="close()"></div>
    <section
      v-if="open"
      :id="panelId"
      ref="panel"
      class="evaluation-help-panel"
      :class="[mobile ? 'evaluation-help-sheet' : guide ? 'evaluation-help-guide' : 'evaluation-help-popover']"
      :style="panelStyle"
      role="dialog"
      :aria-modal="mobile || guide ? 'true' : undefined"
      :aria-label="guide ? 'Learn how to read this report' : `${definition?.label ?? field} help`"
      tabindex="-1"
    >
      <header>
        <div>
          <span>{{ guide ? 'Evaluation vocabulary' : context === 'evaluation' ? 'Evaluation term' : 'Execution fact' }}</span>
          <strong>{{ guide ? 'Learn how to read this report' : definition?.label }}</strong>
        </div>
        <button type="button" aria-label="Close evaluation help" @click="close()">Close</button>
      </header>

      <template v-if="guide">
        <p>Evidence status, operation type, and recorded result answer different questions. Read them independently.</p>
        <div class="evaluation-guide-groups">
          <section v-for="group in guideGroups" :key="group.title">
            <h2>{{ group.title }}</h2>
            <dl>
              <div v-for="item in group.entries" :key="`${item.label}-${item.code ?? ''}`">
                <dt>
                  {{ item.label }} <code v-if="item.code">{{ item.code }}</code>
                </dt>
                <dd><GlossaryDescription :entry="item" /></dd>
              </div>
            </dl>
          </section>
        </div>
      </template>
      <template v-else>
        <p><GlossaryDescription v-if="definition" :entry="definition" /></p>
        <dl class="evaluation-current-value">
          <div>
            <dt>Current value</dt>
            <dd>{{ current }}</dd>
          </div>
          <div v-if="detail">
            <dt>Related detail</dt>
            <dd>{{ detail }}</dd>
          </div>
        </dl>
        <section v-if="taxonomy" class="evaluation-taxonomy">
          <strong>Possible values</strong>
          <dl>
            <div v-for="(item, key) in taxonomy" :key="key">
              <dt>
                <code>{{ key === 'none' ? 'null' : key }}</code> {{ item.label }}
              </dt>
              <dd>{{ item.description }}</dd>
            </div>
          </dl>
        </section>
      </template>
    </section>
  </Teleport>
</template>
