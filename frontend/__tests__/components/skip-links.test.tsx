import { render, screen } from '@testing-library/react';
import SkipLinks from '@/components/skip-links';

describe('SkipLinks', () => {
  it('renders skip links', () => {
    render(<SkipLinks />);
    
    const skipToMainContent = screen.getByRole('link', { name: /skip to main content/i });
    const skipToNavigation = screen.getByRole('link', { name: /skip to navigation/i });
    
    expect(skipToMainContent).toBeInTheDocument();
    expect(skipToNavigation).toBeInTheDocument();
  });

  it('has correct href attributes', () => {
    render(<SkipLinks />);
    
    const skipToMainContent = screen.getByRole('link', { name: /skip to main content/i });
    const skipToNavigation = screen.getByRole('link', { name: /skip to navigation/i });
    
    expect(skipToMainContent).toHaveAttribute('href', '#main-content');
    expect(skipToNavigation).toHaveAttribute('href', '#main-navigation');
  });

  it('has proper accessibility classes for screen readers', () => {
    render(<SkipLinks />);
    
    const container = screen.getByRole('link', { name: /skip to main content/i }).parentElement;
    expect(container).toHaveClass('sr-only', 'focus-within:not-sr-only');
  });

  it('has proper focus management classes', () => {
    render(<SkipLinks />);
    
    const skipToMainContent = screen.getByRole('link', { name: /skip to main content/i });
    const skipToNavigation = screen.getByRole('link', { name: /skip to navigation/i });
    
    // Check for focus-related classes
    expect(skipToMainContent).toHaveClass('focus:outline-none', 'focus:ring-2');
    expect(skipToNavigation).toHaveClass('focus:outline-none', 'focus:ring-2');
    
    // Check for transform classes for slide-in effect
    expect(skipToMainContent).toHaveClass('-translate-y-full', 'focus:translate-y-0');
    expect(skipToNavigation).toHaveClass('-translate-y-full', 'focus:translate-y-0');
  });
});