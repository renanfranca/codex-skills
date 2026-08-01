<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { evaluationGlossary } from '../../scripts/evaluation-glossary.mjs';
import { formatApiReferenceEstimate } from '../../scripts/telemetry-format.mjs';
import GlossaryDescription from './GlossaryDescription.vue';

const props = defineProps({
  data: {
    type: String,
    required: true,
  },
  compact: {
    type: Boolean,
    default: false,
  },
});

const evidence = computed(() => JSON.parse(decodeURIComponent(props.data)));
const open = ref(false);
const mobile = ref(false);
const trigger = ref(null);
const panel = ref(null);
const panelStyle = ref({});
const panelId = `evidence-status-${Math.random().toString(36).slice(2)}`;
let mediaQuery;

const currentReportGroups = computed(() => Object.entries(evidence.value.currentReportGroups));
const suiteEvidence = computed(() =>
  evidence.value.suiteCaseCount === null
    ? 'No suite declared; complete suite evidence cannot be established.'
    : `${evidence.value.passingCaseCount} of ${evidence.value.suiteCaseCount} declared cases have a current pass.`,
);
const numberFormatter = new Intl.NumberFormat('en');

function formatRecordedNumber(value) {
  return value === null ? 'Not recorded' : numberFormatter.format(value);
}

function formatDuration(durationMs) {
  if (durationMs === null) return 'Not recorded';
  if (durationMs < 1000) return `${durationMs} ms`;
  const seconds = durationMs / 1000;
  if (seconds < 60) return `${seconds.toFixed(1)} s`;
  return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
}

function formatCompleteness(value) {
  if (value === null) return 'Not recorded';
  return value ? 'Complete' : 'Incomplete';
}

function updateMode() {
  mobile.value = mediaQuery.matches;
  updatePosition();
}

function updatePosition() {
  if (!open.value || mobile.value || !trigger.value) {
    panelStyle.value = {};
    return;
  }
  const bounds = trigger.value.getBoundingClientRect();
  const width = Math.min(420, window.innerWidth - 32);
  const left = Math.max(16, Math.min(bounds.left, window.innerWidth - width - 16));
  const panelHeight = panel.value?.getBoundingClientRect().height ?? 0;
  const below = bounds.bottom + 10;
  const above = bounds.top - panelHeight - 10;
  const top = below + panelHeight <= window.innerHeight - 16 ? below : Math.max(16, above);
  panelStyle.value = {
    left: `${left}px`,
    top: `${top}px`,
    width: `${width}px`,
  };
}

async function show() {
  open.value = true;
  await nextTick();
  updatePosition();
  panel.value?.focus();
}

function close({ restoreFocus = true } = {}) {
  if (!open.value) return;
  open.value = false;
  if (restoreFocus) nextTick(() => trigger.value?.focus());
}

function handleDocumentClick(event) {
  if (!open.value || mobile.value) return;
  if (!panel.value?.contains(event.target) && !trigger.value?.contains(event.target)) {
    close();
  }
}

function handleDocumentKey(event) {
  if (event.key === 'Escape' && open.value) {
    event.preventDefault();
    close();
  }
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
    ref="trigger"
    class="evidence-status-trigger"
    :class="{ 'evidence-status-trigger-compact': compact }"
    type="button"
    aria-haspopup="dialog"
    :aria-expanded="open"
    :aria-controls="panelId"
    :aria-label="`Explain evidence for ${evidence.skill}: ${evidence.label}`"
    @click="open ? close() : show()"
  >
    <span v-if="!compact" class="evidence-state-indicator" aria-hidden="true"></span>
    {{ compact ? 'Why this status?' : 'Inspect current evidence' }}
  </button>

  <Teleport to="body">
    <div v-if="open && mobile" class="evidence-status-backdrop" data-testid="evidence-backdrop" @click="close()"></div>
    <section
      v-if="open"
      :id="panelId"
      ref="panel"
      class="evidence-status-panel"
      :class="[`evidence-state-${evidence.variant}`, mobile ? 'evidence-status-sheet' : 'evidence-status-popover']"
      :style="panelStyle"
      role="dialog"
      :aria-modal="mobile ? 'true' : undefined"
      :aria-label="`${evidence.skill} evidence status`"
      tabindex="-1"
    >
      <header>
        <div>
          <span>Evidence status</span>
          <strong><span class="evidence-state-indicator" aria-hidden="true"></span>{{ evidence.label }}</strong>
        </div>
        <button type="button" aria-label="Close evidence status" @click="close()">Close</button>
      </header>

      <p>{{ evidence.description }}</p>

      <dl class="evidence-status-facts">
        <div>
          <dt>Suite evidence</dt>
          <dd>{{ suiteEvidence }}</dd>
        </div>
        <div>
          <dt>Validated promotion</dt>
          <dd>{{ evidence.promotion ? 'Passing promotion found' : 'No matching promotion' }}</dd>
        </div>
        <div>
          <dt>Historical reports</dt>
          <dd>{{ evidence.historicalReportCount }}</dd>
        </div>
      </dl>

      <div v-if="evidence.promotionSummary" class="evidence-promotion-detail">
        <section>
          <strong>Qualification gates</strong>
          <ul class="evidence-gate-list">
            <li v-for="gate in evidence.qualificationGates" :key="gate">{{ gate }}</li>
          </ul>
        </section>

        <section>
          <strong>Recorded effort</strong>
          <dl class="evidence-effort-grid">
            <div>
              <dt>Executor sessions</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.sessions.executor) }}</dd>
            </div>
            <div>
              <dt>Judge sessions</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.sessions.judge) }}</dd>
            </div>
            <div>
              <dt>Total sessions</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.sessions.total) }}</dd>
            </div>
            <div>
              <dt>Input tokens</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.tokens.input) }}</dd>
            </div>
            <div>
              <dt>Cached input tokens</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.tokens.cachedInput) }}</dd>
            </div>
            <div>
              <dt>Output tokens</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.tokens.output) }}</dd>
            </div>
            <div>
              <dt>Reasoning output tokens</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.tokens.reasoningOutput) }}</dd>
            </div>
            <div>
              <dt>Total tokens</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.tokens.total) }}</dd>
            </div>
            <div>
              <dt>Duration</dt>
              <dd>{{ formatDuration(evidence.promotionSummary.durationMs) }}</dd>
            </div>
            <div>
              <dt>Usage events</dt>
              <dd>{{ formatRecordedNumber(evidence.promotionSummary.eventCount) }}</dd>
            </div>
            <div>
              <dt>API reference estimate</dt>
              <dd>{{ formatApiReferenceEstimate(evidence.promotionSummary.apiReferenceEstimate) }}</dd>
            </div>
            <div>
              <dt>Runtime telemetry</dt>
              <dd>{{ formatCompleteness(evidence.promotionSummary.telemetry.runtimeComplete) }}</dd>
            </div>
            <div>
              <dt>Token telemetry</dt>
              <dd>{{ formatCompleteness(evidence.promotionSummary.telemetry.usageComplete) }}</dd>
            </div>
          </dl>
          <p><GlossaryDescription :entry="evaluationGlossary.modelSession" /></p>
          <p><GlossaryDescription :entry="evaluationGlossary.fields.totalTokens" /></p>
          <a class="evidence-promotion-report" :href="evidence.promotionSummary.report.href" @click="close({ restoreFocus: false })">
            Inspect promotion report
          </a>
        </section>
      </div>

      <div class="evidence-result-groups">
        <strong>Current reports by recorded result</strong>
        <ul v-if="currentReportGroups.length">
          <li v-for="[result, reports] in currentReportGroups" :key="result">
            <div>
              <span :class="`status status-${result.toLowerCase().replaceAll(/[^a-z0-9]+/g, '-')}`">{{ result }}</span>
              <span>{{ reports.length }}</span>
            </div>
            <ul class="evidence-report-links">
              <li v-for="report in reports" :key="report.id">
                <a :href="report.href" @click="close({ restoreFocus: false })">{{ report.operationDisplay }} · {{ report.id }}</a>
              </li>
            </ul>
          </li>
        </ul>
        <p v-else>No archived report matches the current source fingerprint.</p>
      </div>

      <a class="evidence-history-action" :href="evidence.historyHref" @click="close({ restoreFocus: false })">
        View evaluation history →
      </a>
    </section>
  </Teleport>
</template>
