import React from 'react';
import { render, screen } from '@testing-library/react';
import MonetizationDashboard from '@/components/monetization/MonetizationDashboard';

// Mock the icons
jest.mock('@heroicons/react/24/outline', () => ({
  CurrencyDollarIcon: () => <div data-testid="currency-icon" />,
  BuildingOfficeIcon: () => <div data-testid="building-icon" />,
  LinkIcon: () => <div data-testid="link-icon" />,
  ChartBarIcon: () => <div data-testid="chart-icon" />,
  ArrowTrendingUpIcon: () => <div data-testid="trending-icon" />,
  CalendarIcon: () => <div data-testid="calendar-icon" />
}));

describe('MonetizationDashboard', () => {
  it('renders without crashing', () => {
    render(<MonetizationDashboard />);
    expect(screen.getByText(/total earnings/i)).toBeInTheDocument();
  });

  it('displays earnings stats', () => {
    render(<MonetizationDashboard />);
    expect(screen.getByText('$15,750.50')).toBeInTheDocument();
  });

  it('displays collaboration count', () => {
    render(<MonetizationDashboard />);
    expect(screen.getByText(/active collaborations/i)).toBeInTheDocument();
  });

  it('displays affiliate link count', () => {
    render(<MonetizationDashboard />);
    expect(screen.getByText(/affiliate links/i)).toBeInTheDocument();
  });

  it('displays monetization dashboard header', () => {
    render(<MonetizationDashboard />);
    expect(screen.getByText(/monetization dashboard/i)).toBeInTheDocument();
  });
});