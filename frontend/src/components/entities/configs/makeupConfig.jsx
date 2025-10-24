import { createPresetConfig } from './presetConfigFactory'

export const makeupConfig = createPresetConfig({
  category: 'makeup',
  title: 'Makeup',
  icon: '💄',
  emptyMessage: 'No makeup styles yet',
  descriptionField: 'overall_look',
  detailFields: [
    { key: 'foundation', label: 'Foundation' },
    { key: 'eye_makeup', label: 'Eye Makeup' },
    { key: 'eyebrows', label: 'Eyebrows' },
    { key: 'lips', label: 'Lips' },
    { key: 'cheeks', label: 'Cheeks' },
    { key: 'highlights_contour', label: 'Highlights & Contour' },
    { key: 'overall_look', label: 'Overall Look' }
  ]
})
