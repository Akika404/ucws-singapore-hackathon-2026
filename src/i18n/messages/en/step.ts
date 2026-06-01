export default {
  counter: 'Step {current} / {total}',
  // name step
  name: {
    prefLabel: 'Company name preference',
    prefPlaceholder: 'e.g. Xinghe Yunchuang, Zhiyun Tech...',
    descLabel: 'Business description',
    descOptional: '(optional)',
    descPlaceholder:
      'Describe the business area to generate more fitting names, e.g. a SaaS collaboration platform for SMEs',
    descHint: 'The more detail you provide, the more tailored the generated names',
    generate: 'Generate name suggestions',
    regenerate: 'Regenerate',
    generating: 'Generating name suggestions...',
    chooseHint: 'Please choose your intended company name',
    customName: 'Custom name',
    customNamePlaceholder: 'Enter the full company name you have chosen...',
    bizLabel: 'Main business',
    bizSelectPlaceholder: 'Select an industry category',
    aiReco: '✨ AI recommended',
    bizHint:
      'Reference: business scope, company type and registered capital will be smartly recommended in later steps based on this',
    approvalChecking: 'Checking approval requirements...',
    approvalNeeded: 'Involves {type}',
    approvalDesc:
      'Your selected business type requires related approval procedures. Please learn the requirements in advance',
    viewDetail: 'View details',
  },
  // type step
  type: {
    peopleLabel: 'Number of employees',
    peoplePlaceholder: 'Enter number of employees',
    shareholderLabel: 'Number of shareholders',
    shareholderHint: 'If company headcount is greater than 1, the number of shareholders must be greater than 2.',
    shareholderPlaceholder: 'Enter number of shareholders',
    unit: 'persons',
    loading: 'Recommending a suitable company type for you...',
    error: 'Failed to load company type recommendation, please try again',
    resultLabel: 'Recommended company type:',
    empty: 'Enter employee and shareholder counts to auto-recommend a company type',
  },
  // scope step
  scope: {
    selectedBusiness: 'Selected main business',
    loading: 'Drafting business scope...',
    error: 'Failed to generate business scope, please try again',
    mainTag: 'Main business',
    othersTitle: 'Other business scope',
  },
  // capital step
  capital: {
    intentionLabel: 'Intended investment amount',
    intentionPlaceholder: 'Enter investment amount',
    unit: '× 10k CNY',
    tip: 'The new Company Law requires full payment within five years.',
    estimateLabel: 'Estimated registered / subscribed capital',
    estimating: 'Estimating...',
    error: 'Failed to get estimate, please try again',
    empty: 'Auto-displayed after entering the subscribed amount',
    money: '{amount} × 10k CNY',
    answer: 'Intended investment: {intention}; estimated registered/subscribed capital: {estimated}',
  },
  // address step
  address: {
    label: 'Registered address',
    selectPlaceholder: 'Select a province',
    recommendTitle: 'Recommended',
    loading: 'Generating registered address suggestions...',
    error: 'Failed to get registered address recommendation, please try again',
    empty: 'Recommended address type is shown after selecting a province',
    answer: '{province}: recommended: {recommendation}',
  },
  // org step
  org: {
    imageAlt: 'Org structure diagram',
    tipsLabel: 'Tips: ',
    generating: 'Generating suggestions...',
  },
  optionsLoading: 'AI is generating options based on your information...',
  recommended: 'Recommended',
  expand: 'View details ▼',
  collapse: 'Collapse ▲',
  customPlaceholder: 'Enter custom content...',
  // nav bar
  nav: {
    back: 'Back',
    prev: 'Previous',
    next: 'Next →',
    finish: 'Finish registration plan 🎉',
    orgNext: 'Generate personalized advice & full workflow',
    selected: 'Selected: {value}',
    pickOption: 'Please select an option',
    typeHintEmpty: 'Please enter employee and shareholder counts',
    nameHintForm: 'Please fill the name preference and select a main business',
    nameHintPick: 'Please pick an AI-recommended name, or enter a custom name',
    scopeSelectedMain: 'Selected main: {main}',
    scopeDrafting: 'Drafting business scope...',
  },
  modal: {
    title: '{type} details',
    ack: 'Got it',
  },
}
