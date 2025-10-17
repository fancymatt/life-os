# Frontend Tests

This directory contains all frontend tests for the Life-OS application.

## Test Structure

```
src/
├── __tests__/
│   ├── smoke.test.jsx              # Infrastructure smoke tests
│   ├── components/
│   │   └── StoryPresetModal.test.jsx  # Component tests
│   └── integration/
│       └── (future integration tests)
└── test/
    └── setup.js                    # Global test setup
```

## Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode (default)
npm test

# Run tests once (CI mode)
npm test -- --run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test StoryPresetModal

# Run tests matching a pattern
npm test -- -t "creates preset"
```

## Writing Tests

### Component Test Example

```jsx
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MyComponent from '../MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })

  it('handles user interaction', async () => {
    const user = userEvent.setup()
    const mockFn = vi.fn()

    render(<MyComponent onClick={mockFn} />)

    await user.click(screen.getByRole('button'))
    expect(mockFn).toHaveBeenCalled()
  })
})
```

### Available Utilities

#### Vitest
- `describe()` - Group tests
- `it()` / `test()` - Define a test
- `expect()` - Assertions
- `vi.fn()` - Mock functions
- `vi.mock()` - Mock modules
- `beforeEach()` / `afterEach()` - Setup/teardown
- `beforeAll()` / `afterAll()` - Global setup/teardown

#### React Testing Library
- `render()` - Render component
- `screen` - Query rendered output
- `waitFor()` - Wait for async changes
- `cleanup()` - Clean up after tests (automatic)

#### User Event
- `userEvent.setup()` - Initialize user event
- `user.click()` - Simulate click
- `user.type()` - Simulate typing
- `user.hover()` - Simulate hover
- `user.keyboard()` - Simulate keyboard input

#### Jest-DOM Matchers
- `toBeInTheDocument()` - Element exists in DOM
- `toBeVisible()` - Element is visible
- `toHaveTextContent()` - Has specific text
- `toBeDisabled()` / `toBeEnabled()` - Button state
- `toHaveClass()` - Has CSS class
- `toHaveStyle()` - Has specific styles

## Test Coverage Goals

- **Critical Components**: 80%+ coverage
  - StoryPresetModal
  - EntityBrowser
  - Character creation flows
  - Story workflows

- **UI Components**: 60%+ coverage
  - Buttons, inputs, modals
  - Navigation components

- **Utilities**: 80%+ coverage
  - API client
  - Helper functions

## Best Practices

1. **Test Behavior, Not Implementation**
   - Test what users see and do
   - Avoid testing internal state
   - Use accessible queries (getByRole, getByLabelText)

2. **Keep Tests Fast**
   - Mock external dependencies (axios, etc.)
   - Avoid unnecessary async waits
   - Use vi.mock() for heavy imports

3. **Write Descriptive Test Names**
   - Good: `it('displays error when name is empty')`
   - Bad: `it('works')`

4. **Arrange-Act-Assert Pattern**
   ```jsx
   it('creates preset successfully', async () => {
     // Arrange: Set up test data and mocks
     const mockPost = vi.fn().mockResolvedValue({ data: { id: '123' } })
     axios.post = mockPost

     // Act: Perform the action
     render(<StoryPresetModal {...props} />)
     await user.type(screen.getByLabelText('Name'), 'Test')
     await user.click(screen.getByRole('button', { name: 'Create' }))

     // Assert: Verify the outcome
     expect(mockPost).toHaveBeenCalled()
   })
   ```

5. **Clean Up Side Effects**
   - Use `afterEach(() => vi.clearAllMocks())`
   - Cleanup is automatic for rendered components

## Debugging Tests

### View Rendered Output
```jsx
import { screen } from '@testing-library/react'

render(<MyComponent />)
screen.debug() // Prints DOM to console
```

### Check What Queries Are Available
```jsx
screen.logTestingPlaygroundURL() // Opens browser with query suggestions
```

### Run Single Test
```bash
npm test -- -t "specific test name"
```

### Enable Verbose Logging
```bash
npm test -- --reporter=verbose
```

## CI Integration

Tests run automatically in CI on:
- Every push
- Every pull request
- Before deployment

Required: All tests must pass before merging to main.

## Troubleshooting

### Tests Timing Out
```jsx
// Increase timeout for specific test
it('slow test', async () => {
  // ... test code
}, 10000) // 10 second timeout
```

### Element Not Found
```jsx
// Use waitFor for async elements
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument()
})
```

### Mock Not Working
```jsx
// Ensure mock is set up before render
vi.mock('axios')
axios.get = vi.fn().mockResolvedValue({ data: {} })

// Or use vi.mocked() for type safety
vi.mocked(axios.get).mockResolvedValue({ data: {} })
```

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [jest-dom Matchers](https://github.com/testing-library/jest-dom)
- [User Event](https://testing-library.com/docs/user-event/intro)
