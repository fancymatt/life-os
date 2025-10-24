import { createPresetConfig } from './presetConfigFactory'

export const expressionsConfig = createPresetConfig({
  category: 'expressions',
  title: 'Expressions',
  icon: '😊',
  emptyMessage: 'No expressions yet',
  descriptionField: 'description',
  detailFields: [
    { key: 'emotion', label: 'Emotion' },
    { key: 'intensity', label: 'Intensity' },
    { key: 'eyes', label: 'Eyes' },
    { key: 'mouth', label: 'Mouth' },
    { key: 'eyebrows', label: 'Eyebrows' },
    { key: 'overall_mood', label: 'Overall Mood' },
    { key: 'description', label: 'Description' }
  ]
})
