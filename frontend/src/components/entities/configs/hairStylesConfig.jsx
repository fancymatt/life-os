import { createPresetConfig } from './presetConfigFactory'

export const hairStylesConfig = createPresetConfig({
  category: 'hair_styles',
  title: 'Hair Styles',
  icon: '💇',
  emptyMessage: 'No hair styles yet',
  descriptionField: 'overall_style',
  detailFields: [
    { key: 'cut', label: 'Cut' },
    { key: 'length', label: 'Length' },
    { key: 'layers', label: 'Layers' },
    { key: 'texture', label: 'Texture' },
    { key: 'volume', label: 'Volume' },
    { key: 'parting', label: 'Parting' },
    { key: 'front_styling', label: 'Front Styling' },
    { key: 'overall_style', label: 'Overall Style' }
  ]
})
