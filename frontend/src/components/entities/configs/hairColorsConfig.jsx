import { createPresetConfig } from './presetConfigFactory'

export const hairColorsConfig = createPresetConfig({
  category: 'hair_colors',
  title: 'Hair Colors',
  icon: '🎨',
  emptyMessage: 'No hair colors yet',
  descriptionField: 'description',
  detailFields: [
    { key: 'base_color', label: 'Base Color' },
    { key: 'highlights', label: 'Highlights' },
    { key: 'lowlights', label: 'Lowlights' },
    { key: 'technique', label: 'Technique' },
    { key: 'tone', label: 'Tone' },
    { key: 'description', label: 'Description' }
  ]
})
