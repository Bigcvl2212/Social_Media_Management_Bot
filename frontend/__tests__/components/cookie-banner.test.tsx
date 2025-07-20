import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CookieBanner from '@/components/cookie-banner';

// Mock js-cookie
jest.mock('js-cookie', () => ({
  get: jest.fn(),
  set: jest.fn(),
}));

const mockCookies = require('js-cookie');

// Mock window.gtag
const mockGtag = jest.fn();
Object.defineProperty(window, 'gtag', {
  value: mockGtag,
});

describe('CookieBanner', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockCookies.get.mockReturnValue(undefined); // No existing consent
  });

  it('does not render when consent already exists', () => {
    mockCookies.get.mockReturnValue('{"necessary":true,"analytics":false,"marketing":false}');
    
    render(<CookieBanner />);
    
    expect(screen.queryByText('We use cookies')).not.toBeInTheDocument();
  });

  it('renders cookie banner when no consent exists', async () => {
    render(<CookieBanner />);
    
    await waitFor(() => {
      expect(screen.getByText('We use cookies')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/We use cookies to enhance your experience/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /accept all/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /reject all/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /manage preferences/i })).toBeInTheDocument();
  });

  it('handles accept all functionality', async () => {
    render(<CookieBanner />);
    
    await waitFor(() => {
      expect(screen.getByText('We use cookies')).toBeInTheDocument();
    });
    
    const acceptAllButton = screen.getByRole('button', { name: /accept all/i });
    fireEvent.click(acceptAllButton);
    
    expect(mockCookies.set).toHaveBeenCalledWith(
      'cookie-consent',
      JSON.stringify({
        necessary: true,
        analytics: true,
        marketing: true,
      }),
      { expires: 365 }
    );
    
    expect(mockGtag).toHaveBeenCalledWith('consent', 'update', {
      analytics_storage: 'granted',
      ad_storage: 'granted',
    });
  });

  it('handles reject all functionality', async () => {
    render(<CookieBanner />);
    
    await waitFor(() => {
      expect(screen.getByText('We use cookies')).toBeInTheDocument();
    });
    
    const rejectAllButton = screen.getByRole('button', { name: /reject all/i });
    fireEvent.click(rejectAllButton);
    
    expect(mockCookies.set).toHaveBeenCalledWith(
      'cookie-consent',
      JSON.stringify({
        necessary: true,
        analytics: false,
        marketing: false,
      }),
      { expires: 365 }
    );
  });

  it('opens preferences modal', async () => {
    render(<CookieBanner />);
    
    await waitFor(() => {
      expect(screen.getByText('We use cookies')).toBeInTheDocument();
    });
    
    const managePreferencesButton = screen.getByRole('button', { name: /manage preferences/i });
    fireEvent.click(managePreferencesButton);
    
    expect(screen.getByText('Cookie Preferences')).toBeInTheDocument();
    expect(screen.getByText('Necessary Cookies')).toBeInTheDocument();
    expect(screen.getByText('Analytics Cookies')).toBeInTheDocument();
    expect(screen.getByText('Marketing Cookies')).toBeInTheDocument();
  });

  it('handles custom preferences selection', async () => {
    render(<CookieBanner />);
    
    await waitFor(() => {
      expect(screen.getByText('We use cookies')).toBeInTheDocument();
    });
    
    // Open preferences
    const managePreferencesButton = screen.getByRole('button', { name: /manage preferences/i });
    fireEvent.click(managePreferencesButton);
    
    // Toggle analytics on
    const analyticsCheckbox = screen.getAllByRole('checkbox')[1]; // Second checkbox (analytics)
    fireEvent.click(analyticsCheckbox);
    
    // Save preferences
    const saveButton = screen.getByRole('button', { name: /save preferences/i });
    fireEvent.click(saveButton);
    
    expect(mockCookies.set).toHaveBeenCalledWith(
      'cookie-consent',
      JSON.stringify({
        necessary: true,
        analytics: true,
        marketing: false,
      }),
      { expires: 365 }
    );
    
    expect(mockGtag).toHaveBeenCalledWith('consent', 'update', {
      analytics_storage: 'granted',
      ad_storage: 'denied',
    });
  });

  it('closes preferences modal', async () => {
    render(<CookieBanner />);
    
    await waitFor(() => {
      expect(screen.getByText('We use cookies')).toBeInTheDocument();
    });
    
    // Open preferences
    const managePreferencesButton = screen.getByRole('button', { name: /manage preferences/i });
    fireEvent.click(managePreferencesButton);
    
    expect(screen.getByText('Cookie Preferences')).toBeInTheDocument();
    
    // Close preferences
    const closeButton = screen.getByRole('button', { name: '' }); // X button
    fireEvent.click(closeButton);
    
    expect(screen.queryByText('Cookie Preferences')).not.toBeInTheDocument();
    expect(screen.getByText('We use cookies')).toBeInTheDocument();
  });

  it('necessary cookies are always disabled and checked', async () => {
    render(<CookieBanner />);
    
    await waitFor(() => {
      expect(screen.getByText('We use cookies')).toBeInTheDocument();
    });
    
    // Open preferences
    const managePreferencesButton = screen.getByRole('button', { name: /manage preferences/i });
    fireEvent.click(managePreferencesButton);
    
    const necessaryCheckbox = screen.getAllByRole('checkbox')[0]; // First checkbox (necessary)
    expect(necessaryCheckbox).toBeChecked();
    expect(necessaryCheckbox).toBeDisabled();
  });
});