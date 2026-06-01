import { reactive } from 'vue'
import type { BaseFormData } from './components/RegAdvisor.vue'

export const sharedFormData = reactive<{ value: BaseFormData | null }>({ value: null })

export function hasUsableRegistrationData(formData: BaseFormData | null): formData is BaseFormData {
  if (!formData) return false

  const hasText = (...values: unknown[]) =>
    values.some(v => typeof v === 'string' && v.trim().length > 0)

  const hasScope =
    typeof formData.scope === 'object' &&
    formData.scope !== null &&
    (hasText(formData.scope.main) || formData.scope.others.some(item => item.trim().length > 0))

  return (
    hasText(
      formData.business,
      formData.companyType,
      formData.namePref,
      formData.name,
      formData.capital,
      formData.address,
      formData.org,
    ) ||
    hasScope ||
    (typeof formData.people === 'number' && formData.people > 0) ||
    (typeof formData.shareholder === 'number' && formData.shareholder > 0)
  )
}
