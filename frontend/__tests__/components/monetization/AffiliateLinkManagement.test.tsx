import React from 'react';
import { render, screen } from '@testing-library/react';
import AffiliateLinkManagement from '@/components/monetization/AffiliateLinkManagement';

// Mock the icons
jest.mock('@heroicons/react/24/outline', () => ({
  PlusIcon: () => <div data-testid="plus-icon" />,
  LinkIcon: () => <div data-testid="link-icon" />,
  EyeIcon: () => <div data-testid="eye-icon" />,
  ChartBarIcon: () => <div data-testid="chart-icon" />,
  ClipboardDocumentIcon: () => <div data-testid="clipboard-icon" />,
  PencilIcon: () => <div data-testid="pencil-icon" />,
  TrashIcon: () => <div data-testid="trash-icon" />
}));

describe('AffiliateLinkManagement', () => {
  it('renders without crashing', () => {
    render(<AffiliateLinkManagement />);
    expect(screen.getByText(/affiliate link management/i)).toBeInTheDocument();
  });

  it('displays create new link button', () => {
    render(<AffiliateLinkManagement />);
    expect(screen.getByText(/create new link/i)).toBeInTheDocument();
  });

  it('displays performance stats', () => {
    render(<AffiliateLinkManagement />);
    expect(screen.getByText(/total clicks/i)).toBeInTheDocument();
  });

  it('displays existing links', () => {
    render(<AffiliateLinkManagement />);
    // Component shows demo data, so check for one of the demo links
    expect(screen.getByText(/Beauty Essentials/i)).toBeInTheDocument();
  });
});