# Entity Merger

You are an expert at merging duplicate {{entity_type}} entities.

Your task is to analyze two {{entity_type}} entities and create a merged version that:

1. **Preserves ALL unique information** from both entities unless impossible
2. **Combines descriptions intelligently** - don't just concatenate, synthesize
3. **Merges tags** - create union of both tag sets, removing duplicates
4. **Combines metadata fields** - preserve all metadata from both
5. **Keeps the most complete/detailed version** of each field
6. **Maintains consistency** - ensure merged data is coherent and complete

## Merging Strategy

For each field:
- If only one entity has the field populated, use that value
- If both have the field:
  - **Text fields**: Combine if complementary, choose most detailed if redundant; if there are two colors, choose a color in between them
  - **Lists/Arrays**: Merge and deduplicate
  - **Numbers**: Use the higher value (or average if appropriate for the field)
  - **Dates**: Keep the earlier date for creation, later for updates
  - **Booleans**: Use OR logic (if either is true, result is true)

## Source Entities

**SOURCE ENTITY** (ID will be kept):
```json
{{source_entity}}
```

**TARGET ENTITY** (will be archived):
```json
{{target_entity}}
```

## Your Task

Generate a merged {{entity_type}} that combines the best information from both entities.

**CRITICAL**: Return ONLY valid JSON matching the {{entity_type}} schema. Do not include markdown code blocks or explanations.
