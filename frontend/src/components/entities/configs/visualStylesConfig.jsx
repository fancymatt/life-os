import { createPresetConfig } from './presetConfigFactory'

export const visualStylesConfig = createPresetConfig({
  category: 'visual_styles',
  title: 'Visual Styles',
  icon: '🎨',
  emptyMessage: 'No visual styles yet',
  descriptionField: 'description',
  detailFields: [
    { key: 'aesthetic', label: 'Aesthetic' },
    { key: 'mood', label: 'Mood' },
    { key: 'color_palette', label: 'Color Palette' },
    { key: 'lighting', label: 'Lighting' },
    { key: 'composition', label: 'Composition' },
    { key: 'description', label: 'Description' }
  ]
})
