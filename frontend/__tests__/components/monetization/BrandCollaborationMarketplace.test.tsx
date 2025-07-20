import React from 'react';
import { render, screen } from '@testing-library/react';
import BrandCollaborationMarketplace from '@/components/monetization/BrandCollaborationMarketplace';

// Mock the icons
jest.mock('@heroicons/react/24/outline', () => ({
  MagnifyingGlassIcon: () => <div data-testid="search-icon" />,
  FunnelIcon: () => <div data-testid="filter-icon" />,
  EyeIcon: () => <div data-testid="eye-icon" />,
  CalendarIcon: () => <div data-testid="calendar-icon" />,
  CurrencyDollarIcon: () => <div data-testid="currency-icon" />,
  HandshakeIcon: () => <div data-testid="handshake-icon" />,
  BuildingOfficeIcon: () => <div data-testid="building-icon" />,
  CheckBadgeIcon: () => <div data-testid="check-badge-icon" />
}));

describe('BrandCollaborationMarketplace', () => {
  it('renders without crashing', () => {
    render(<BrandCollaborationMarketplace />);
    expect(screen.getByText(/brand collaboration marketplace/i)).toBeInTheDocument();
  });

  it('displays search input', () => {
    render(<BrandCollaborationMarketplace />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('displays filter section', () => {
    render(<BrandCollaborationMarketplace />);
    expect(screen.getByText(/filters/i)).toBeInTheDocument();
  });

  it('displays campaigns section', () => {
    render(<BrandCollaborationMarketplace />);
    // Look for the demo campaign
    expect(screen.getByText(/StyleCo Fashion/i)).toBeInTheDocument();
  });
});