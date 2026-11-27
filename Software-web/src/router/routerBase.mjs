export function routerBase(base, documentBase) {
  return base.startsWith('/') ? base : new URL(base, documentBase).pathname
}
