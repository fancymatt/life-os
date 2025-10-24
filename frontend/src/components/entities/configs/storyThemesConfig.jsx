import { createPresetConfig } from './presetConfigFactory'

export const storyThemesConfig = createPresetConfig({
  category: 'story_themes',
  title: 'Story Themes',
  icon: '📖',
  emptyMessage: 'No story themes yet',
  descriptionField: 'description',
  detailFields: [
    { key: 'genre', label: 'Genre' },
    { key: 'subgenre', label: 'Subgenre' },
    { key: 'mood', label: 'Mood' },
    { key: 'themes', label: 'Themes' },
    { key: 'setting', label: 'Setting' },
    { key: 'description', label: 'Description' }
  ]
})
