/**
 * Smoke Tests - Fast sanity checks
 *
 * These tests verify that the basic testing infrastructure is working.
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

// Simple component for testing
function HelloWorld({ name = 'World' }) {
  return <h1>Hello {name}!</h1>
}

describe('Testing Infrastructure', () => {
  it('vitest is working', () => {
    expect(true).toBe(true)
  })

  it('can render React components', () => {
    render(<HelloWorld />)
    expect(screen.getByText('Hello World!')).toBeInTheDocument()
  })

  it('can pass props to components', () => {
    render(<HelloWorld name="Testing" />)
    expect(screen.getByText('Hello Testing!')).toBeInTheDocument()
  })

  it('jest-dom matchers are available', () => {
    render(<HelloWorld />)
    const element = screen.getByText('Hello World!')

    expect(element).toBeInTheDocument()
    expect(element).toBeVisible()
    expect(element).toHaveTextContent('Hello World!')
  })
})
