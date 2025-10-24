import { createPresetConfig } from './presetConfigFactory'

export const artStylesConfig = createPresetConfig({
  category: 'art_styles',
  title: 'Art Styles',
  icon: '🖌️',
  emptyMessage: 'No art styles yet',
  descriptionField: 'mood',
  detailFields: [
    { key: 'medium', label: 'Medium' },
    { key: 'technique', label: 'Technique' },
    { key: 'color_palette', label: 'Color Palette' },
    { key: 'brush_style', label: 'Brush Style' },
    { key: 'texture', label: 'Texture' },
    { key: 'composition_style', label: 'Composition Style' },
    { key: 'artistic_movement', label: 'Artistic Movement' },
    { key: 'mood', label: 'Mood' },
    { key: 'level_of_detail', label: 'Level of Detail' }
  ]
})
