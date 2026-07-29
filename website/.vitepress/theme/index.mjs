import DefaultTheme from 'vitepress/theme';
import EvidenceStatus from './EvidenceStatus.vue';
import './custom.css';

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('EvidenceStatus', EvidenceStatus);
  },
};
