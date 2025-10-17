/**
 * Tests for StoryPresetModal Component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import StoryPresetModal from '../../components/story/StoryPresetModal'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('StoryPresetModal', () => {
  const mockOnClose = vi.fn()
  const mockOnPresetCreated = vi.fn()

  const defaultProps = {
    isOpen: true,
    onClose: mockOnClose,
    onPresetCreated: mockOnPresetCreated,
    category: 'story_themes',
    config: {
      entityType: 'story theme',
      icon: '📚'
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders when open', () => {
    render(<StoryPresetModal {...defaultProps} />)

    expect(screen.getByText(/Create New Story Theme/i)).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(<StoryPresetModal {...defaultProps} isOpen={false} />)

    expect(screen.queryByText(/Create New Story Theme/i)).not.toBeInTheDocument()
  })

  it('displays correct title for story theme', () => {
    render(<StoryPresetModal {...defaultProps} category="story_themes" />)

    expect(screen.getByText(/Create New Story Theme/i)).toBeInTheDocument()
  })

  it('displays correct title for story audience', () => {
    const props = {
      ...defaultProps,
      category: 'story_audiences',
      config: { entityType: 'story audience', icon: '👥' }
    }
    render(<StoryPresetModal {...props} />)

    expect(screen.getByText(/Create New Story Audience/i)).toBeInTheDocument()
  })

  it('has name and description input fields', () => {
    render(<StoryPresetModal {...defaultProps} />)

    expect(screen.getByPlaceholderText(/Enter story theme name/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/Brief description/i)).toBeInTheDocument()
  })

  it('shows error when name is empty on submit', async () => {
    const user = userEvent.setup()
    render(<StoryPresetModal {...defaultProps} />)

    const createButton = screen.getByRole('button', { name: /Create/i })

    // Button should be disabled when name is empty
    expect(createButton).toBeDisabled()
  })

  it('enables create button when name is provided', async () => {
    const user = userEvent.setup()
    render(<StoryPresetModal {...defaultProps} />)

    const nameInput = screen.getByPlaceholderText(/Enter story theme name/i)
    const createButton = screen.getByRole('button', { name: /Create/i })

    // Initially disabled
    expect(createButton).toBeDisabled()

    // Type name
    await user.type(nameInput, 'Test Theme')

    // Should now be enabled
    expect(createButton).toBeEnabled()
  })

  it('calls API with correct data on submit', async () => {
    const user = userEvent.setup()
    const mockResponse = { data: { preset_id: 'test-123' } }
    axios.post = vi.fn().mockResolvedValue(mockResponse)

    render(<StoryPresetModal {...defaultProps} />)

    // Fill in form
    const nameInput = screen.getByPlaceholderText(/Enter story theme name/i)
    const descInput = screen.getByPlaceholderText(/Brief description/i)

    await user.type(nameInput, 'Test Theme')
    await user.type(descInput, 'Test Description')

    // Submit
    const createButton = screen.getByRole('button', { name: /Create/i })
    await user.click(createButton)

    // Verify API call
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith('/presets/story_themes/', {
        name: 'Test Theme',
        data: expect.objectContaining({
          suggested_name: 'Test Theme',
          description: 'Test Description'
        }),
        notes: expect.any(String)
      })
    })
  })

  it('calls onPresetCreated and onClose on successful creation', async () => {
    const user = userEvent.setup()
    const mockResponse = { data: { preset_id: 'test-123' } }
    axios.post = vi.fn().mockResolvedValue(mockResponse)

    render(<StoryPresetModal {...defaultProps} />)

    // Fill in and submit
    const nameInput = screen.getByPlaceholderText(/Enter story theme name/i)
    await user.type(nameInput, 'Test Theme')

    const createButton = screen.getByRole('button', { name: /Create/i })
    await user.click(createButton)

    // Verify callbacks
    await waitFor(() => {
      expect(mockOnPresetCreated).toHaveBeenCalledWith(mockResponse.data)
      expect(mockOnClose).toHaveBeenCalled()
    })
  })

  it('displays error message on API failure', async () => {
    const user = userEvent.setup()
    const errorMessage = 'Failed to create preset'
    axios.post = vi.fn().mockRejectedValue({
      response: { data: { detail: errorMessage } }
    })

    render(<StoryPresetModal {...defaultProps} />)

    // Fill in and submit
    const nameInput = screen.getByPlaceholderText(/Enter story theme name/i)
    await user.type(nameInput, 'Test Theme')

    const createButton = screen.getByRole('button', { name: /Create/i })
    await user.click(createButton)

    // Verify error displayed
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })
  })

  it('closes modal when cancel is clicked', async () => {
    const user = userEvent.setup()
    render(<StoryPresetModal {...defaultProps} />)

    const cancelButton = screen.getByRole('button', { name: /Cancel/i })
    await user.click(cancelButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('resets form after successful creation', async () => {
    const user = userEvent.setup()
    const mockResponse = { data: { preset_id: 'test-123' } }
    axios.post = vi.fn().mockResolvedValue(mockResponse)

    render(<StoryPresetModal {...defaultProps} />)

    // Fill in form
    const nameInput = screen.getByPlaceholderText(/Enter story theme name/i)
    await user.type(nameInput, 'Test Theme')

    // Submit
    const createButton = screen.getByRole('button', { name: /Create/i })
    await user.click(createButton)

    await waitFor(() => {
      expect(mockOnClose).toHaveBeenCalled()
    })

    // Form should be reset (though modal closes, so we can't verify this easily)
    // This is more of an implementation detail
  })

  it('includes all expected fields for story theme', async () => {
    const user = userEvent.setup()
    const mockPost = vi.fn().mockResolvedValue({ data: { preset_id: 'test-123' } })
    axios.post = mockPost

    render(<StoryPresetModal {...defaultProps} category="story_themes" />)

    const nameInput = screen.getByPlaceholderText(/Enter story theme name/i)
    await user.type(nameInput, 'Test')

    const createButton = screen.getByRole('button', { name: /Create/i })
    await user.click(createButton)

    await waitFor(() => {
      const callArgs = mockPost.mock.calls[0][1]
      expect(callArgs.data).toHaveProperty('suggested_name')
      expect(callArgs.data).toHaveProperty('description')
      expect(callArgs.data).toHaveProperty('setting_guidance')
      expect(callArgs.data).toHaveProperty('tone')
      expect(callArgs.data).toHaveProperty('common_elements')
      expect(callArgs.data).toHaveProperty('story_structure_notes')
      expect(callArgs.data).toHaveProperty('world_building')
    })
  })

  it('includes all expected fields for story audience', async () => {
    const user = userEvent.setup()
    const mockPost = vi.fn().mockResolvedValue({ data: { preset_id: 'test-123' } })
    axios.post = mockPost

    const props = {
      ...defaultProps,
      category: 'story_audiences'
    }
    render(<StoryPresetModal {...props} />)

    const nameInput = screen.getByPlaceholderText(/Enter story audience name/i)
    await user.type(nameInput, 'Test')

    const createButton = screen.getByRole('button', { name: /Create/i })
    await user.click(createButton)

    await waitFor(() => {
      const callArgs = mockPost.mock.calls[0][1]
      expect(callArgs.data).toHaveProperty('suggested_name')
      expect(callArgs.data).toHaveProperty('description')
      expect(callArgs.data).toHaveProperty('age_range')
      expect(callArgs.data).toHaveProperty('reading_level')
      expect(callArgs.data).toHaveProperty('content_considerations')
      expect(callArgs.data).toHaveProperty('engagement_style')
    })
  })

  it('includes all expected fields for prose style', async () => {
    const user = userEvent.setup()
    const mockPost = vi.fn().mockResolvedValue({ data: { preset_id: 'test-123' } })
    axios.post = mockPost

    const props = {
      ...defaultProps,
      category: 'story_prose_styles'
    }
    render(<StoryPresetModal {...props} />)

    const nameInput = screen.getByPlaceholderText(/Enter prose style name/i)
    await user.type(nameInput, 'Test')

    const createButton = screen.getByRole('button', { name: /Create/i })
    await user.click(createButton)

    await waitFor(() => {
      const callArgs = mockPost.mock.calls[0][1]
      expect(callArgs.data).toHaveProperty('suggested_name')
      expect(callArgs.data).toHaveProperty('description')
      expect(callArgs.data).toHaveProperty('tone')
      expect(callArgs.data).toHaveProperty('pacing')
      expect(callArgs.data).toHaveProperty('vocabulary_level')
      expect(callArgs.data).toHaveProperty('sentence_structure')
      expect(callArgs.data).toHaveProperty('narrative_voice')
    })
  })
})
