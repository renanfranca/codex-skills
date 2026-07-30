import DefaultTheme from 'vitepress/theme';
import EvidenceStatus from './EvidenceStatus.vue';
import EvaluationHelp from './EvaluationHelp.vue';
import './custom.css';

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('EvidenceStatus', EvidenceStatus);
    app.component('EvaluationHelp', EvaluationHelp);
  },
};
