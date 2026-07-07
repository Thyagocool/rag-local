import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders the chat header', () => {
    render(<App />)
    expect(screen.getByText('RAG Chat')).toBeInTheDocument()
  })

  it('shows the mode toggle buttons', () => {
    render(<App />)
    expect(screen.getByText('RAG')).toBeInTheDocument()
    expect(screen.getByText('Agent')).toBeInTheDocument()
  })
})
