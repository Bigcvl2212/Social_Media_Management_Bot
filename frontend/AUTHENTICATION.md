# Authentication Setup Guide

This guide explains how to configure and use the authentication system in the Social Media Management Bot frontend.

## Overview

The authentication system is built using NextAuth.js v4 and supports:
- OAuth providers (Google, GitHub)
- JWT-based sessions
- Route protection middleware
- User profile management
- Error handling and user feedback

## Environment Variables

### Required Environment Variables

Create a `.env.local` file in the frontend directory with the following variables:

```bash
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-key-here

# OAuth Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Setting up OAuth Providers

#### Google OAuth Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure the consent screen
6. Add authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google` (development)
   - `https://yourdomain.com/api/auth/callback/google` (production)
7. Copy the Client ID and Client Secret to your `.env.local` file

#### GitHub OAuth Setup

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the application details:
   - Homepage URL: `http://localhost:3000` (development)
   - Authorization callback URL: `http://localhost:3000/api/auth/callback/github`
4. Copy the Client ID and Client Secret to your `.env.local` file

### Generating NEXTAUTH_SECRET

Generate a secure secret key using:

```bash
openssl rand -base64 32
```

## Route Protection

The middleware automatically protects the following routes:
- `/dashboard/*`
- `/accounts/*`
- `/content/*`
- `/analytics/*`
- `/settings/*`

Users will be redirected to `/auth/signin` if they try to access protected routes while unauthenticated.

## Authentication Flow

1. **Sign In**: Users click "Sign In" and are redirected to `/auth/signin`
2. **Provider Selection**: Users choose their preferred OAuth provider (Google or GitHub)
3. **OAuth Flow**: Users are redirected to the provider for authentication
4. **Callback**: After successful authentication, users are redirected back to the app
5. **Session Creation**: NextAuth creates a JWT session
6. **Dashboard Access**: Users can now access protected routes

## Session Management

- Sessions are stored as JWTs (JSON Web Tokens)
- Sessions are automatically refreshed
- Session data is available via `useSession()` hook
- Sessions persist across browser sessions

## User Profile

The profile page (`/profile`) displays:
- User information (name, email, avatar)
- Account details from OAuth provider
- Session status
- Security information

## Error Handling

The authentication system handles various error scenarios:
- Authentication failures
- Access denied
- Configuration errors
- Network issues

Error messages are displayed to users with appropriate feedback and retry options.

## Usage in Components

### Checking Authentication Status

```tsx
import { useSession } from "next-auth/react"

function MyComponent() {
  const { data: session, status } = useSession()

  if (status === "loading") return <p>Loading...</p>
  if (status === "unauthenticated") return <p>Access Denied</p>

  return <p>Welcome {session?.user?.name}</p>
}
```

### Sign Out

```tsx
import { signOut } from "next-auth/react"

function SignOutButton() {
  return (
    <button onClick={() => signOut({ callbackUrl: "/" })}>
      Sign Out
    </button>
  )
}
```

### Conditional Rendering

```tsx
import { useSession } from "next-auth/react"

function Navigation() {
  const { data: session } = useSession()

  return (
    <nav>
      {session ? (
        <UserMenu user={session.user} />
      ) : (
        <SignInButton />
      )}
    </nav>
  )
}
```

## Security Considerations

1. **HTTPS in Production**: Always use HTTPS in production environments
2. **Secure Secrets**: Keep your OAuth secrets and NEXTAUTH_SECRET secure
3. **Domain Validation**: Ensure redirect URIs match your domain exactly
4. **Session Security**: JWT tokens are signed and encrypted
5. **CSRF Protection**: NextAuth includes built-in CSRF protection

## Troubleshooting

### Common Issues

1. **"Configuration Error"**: Check your environment variables
2. **"Access Denied"**: Verify OAuth app configuration and redirect URIs
3. **"Invalid State"**: Clear browser cookies and try again
4. **Build Errors**: Ensure all imports and types are correct

### Debug Mode

Enable debug mode in development by adding to your `.env.local`:

```bash
NEXTAUTH_DEBUG=true
```

### Logs

Check the browser console and server logs for detailed error information.

## Production Deployment

1. Update `NEXTAUTH_URL` to your production domain
2. Update OAuth provider redirect URIs
3. Use secure, randomly generated secrets
4. Enable HTTPS
5. Test the complete authentication flow

## Additional Resources

- [NextAuth.js Documentation](https://next-auth.js.org/)
- [Google OAuth Guide](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Guide](https://docs.github.com/en/developers/apps/building-oauth-apps)