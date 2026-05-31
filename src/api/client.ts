import { currentLang } from '../i18n'

/**
 * 统一的 fetch 封装：自动注入 Content-Type 与 X-Lang 头。
 * X-Lang 在每次调用时读取当前语言，会话中途切换即时生效。
 */
export async function apiFetch(path: string, options: RequestInit = {}) {
  return fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Lang': currentLang(),
      ...(options.headers || {}),
    },
  })
}
