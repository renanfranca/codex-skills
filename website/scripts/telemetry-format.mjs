export function formatRecordedDecimal(value) {
  if (value === null || value === undefined) return 'Not recorded';
  const recorded = String(value);
  if (!/[eE]/.test(recorded)) return recorded;
  return new Intl.NumberFormat('en', {
    useGrouping: false,
    maximumFractionDigits: 20,
  }).format(value);
}

export function formatMoney(currency, amount) {
  if (currency === null || currency === undefined || amount === null || amount === undefined) return 'Not recorded';
  return `${currency} ${formatRecordedDecimal(amount)}`;
}

export function formatEstimateStatus(status) {
  if (status === null || status === undefined) return 'Not recorded';
  if (status === 'indeterminate-long-context') return 'Indeterminate: long context';
  return status.charAt(0).toUpperCase() + status.slice(1);
}

export function formatApiReferenceEstimate(estimate) {
  if (estimate.amount !== null && estimate.amount !== undefined && estimate.currency !== null && estimate.currency !== undefined) {
    return formatMoney(estimate.currency, estimate.amount);
  }
  if (
    estimate.baseRateAmount !== null
    && estimate.baseRateAmount !== undefined
    && estimate.currency !== null
    && estimate.currency !== undefined
  ) {
    return `${formatMoney(estimate.currency, estimate.baseRateAmount)} base-rate reference`;
  }
  return formatEstimateStatus(estimate.status);
}
