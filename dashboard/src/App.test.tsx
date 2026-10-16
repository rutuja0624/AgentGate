import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('AgentGate Dashboard App', () => {
  it('renders AgentGate brand title and header elements', () => {
    render(<App />);
    expect(screen.getByText('AgentGate')).toBeInTheDocument();
    expect(screen.getByText('Verification Gate for Pull Requests')).toBeInTheDocument();
    expect(screen.getByText(/Gateway & Engine Online/i)).toBeInTheDocument();
  });
});
