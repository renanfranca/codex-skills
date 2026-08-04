export function resolveSiteBase(defaultBase) {
  return process.env.NETLIFY ? '/' : defaultBase;
}
