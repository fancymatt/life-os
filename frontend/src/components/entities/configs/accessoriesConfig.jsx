import { createPresetConfig } from './presetConfigFactory'

export const accessoriesConfig = createPresetConfig({
  category: 'accessories',
  title: 'Accessories',
  icon: '👜',
  emptyMessage: 'No accessories yet',
  descriptionField: 'description',
  detailFields: [
    { key: 'type', label: 'Type' },
    { key: 'material', label: 'Material' },
    { key: 'color', label: 'Color' },
    { key: 'style', label: 'Style' },
    { key: 'size', label: 'Size' },
    { key: 'description', label: 'Description' }
  ]
})
