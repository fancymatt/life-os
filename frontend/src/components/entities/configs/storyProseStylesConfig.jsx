import { createPresetConfig } from './presetConfigFactory'

export const storyProseStylesConfig = createPresetConfig({
  category: 'story_prose_styles',
  title: 'Prose Styles',
  icon: '✍️',
  emptyMessage: 'No prose styles yet',
  descriptionField: 'description',
  detailFields: [
    { key: 'narrative_voice', label: 'Narrative Voice' },
    { key: 'pacing', label: 'Pacing' },
    { key: 'sentence_structure', label: 'Sentence Structure' },
    { key: 'vocabulary_level', label: 'Vocabulary Level' },
    { key: 'tone', label: 'Tone' },
    { key: 'description', label: 'Description' }
  ]
})
