import { createPresetConfig } from './presetConfigFactory'

export const storyAudiencesConfig = createPresetConfig({
  category: 'story_audiences',
  title: 'Story Audiences',
  icon: '👥',
  emptyMessage: 'No story audiences yet',
  descriptionField: 'description',
  detailFields: [
    { key: 'age_range', label: 'Age Range' },
    { key: 'reading_level', label: 'Reading Level' },
    { key: 'interests', label: 'Interests' },
    { key: 'content_appropriateness', label: 'Content Appropriateness' },
    { key: 'description', label: 'Description' }
  ]
})
