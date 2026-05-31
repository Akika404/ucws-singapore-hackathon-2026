import { createI18n } from 'vue-i18n'
import en from './messages/en'
import zh from './messages/zh'

export type Lang = 'en' | 'zh'

const STORAGE_KEY = 'luckyos-lang'

function initialLocale(): Lang {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored === 'zh' || stored === 'en' ? stored : 'en' // 默认英文 / default English
}

const locale = initialLocale()

export const i18n = createI18n({
  legacy: false,
  locale,
  fallbackLocale: 'en',
  messages: { en, zh },
})

document.documentElement.lang = locale

/** 切换语言：更新 i18n、持久化、同步 <html lang> */
export function setLocale(l: Lang) {
  i18n.global.locale.value = l
  localStorage.setItem(STORAGE_KEY, l)
  document.documentElement.lang = l
}

/** 组件外读取当前语言（供 fetch 封装等使用） */
export function currentLang(): Lang {
  return i18n.global.locale.value as Lang
}
