# ClubOS API Research Documentation

## Overview
This document outlines our research into the ClubOS API messaging system, specifically the challenge of sending SMS and Email messages to members using pure API calls instead of Selenium automation.

## Problem Statement
We have successfully implemented authentication and session management with ClubOS, and can navigate through the web interface to send messages via form submission. However, direct API endpoint calls consistently return "Something isn't right" errors, even with proper authentication context.

## Current Findings

### ✅ What Works
1. **Authentication**: Username/password login works successfully
2. **Session Management**: Can maintain session cookies and navigate web interface  
3. **Form Submission**: Submitting message forms directly to member profile pages works
4. **Browser Headers**: Using proper browser-like headers is critical

### ❌ What Doesn't Work
1. **API Endpoints**: `/action/Api/send-message` and `/action/Api/follow-up` return errors
2. **Direct API Calls**: Even with session cookies, CSRF tokens, and proper headers
3. **Bearer Token Authentication**: Using `apiV3AccessToken` as Bearer token fails

### 🔍 Key Observations

#### Working Approach Pattern
```
1. Login to ClubOS → GET /action/Authentication/log-in
2. Navigate to Dashboard → GET /action/Dashboard  
3. Access Member Profile → GET /action/Dashboard/member/{member_id}
4. Submit Message Form → POST /action/Dashboard/member/{member_id}
```

#### Failing Approach Pattern
```
1. Login to ClubOS → GET /action/Authentication/log-in
2. Extract API Tokens → Various methods tried
3. Call API Endpoint → POST /action/Api/send-message (FAILS)
```

## Technical Analysis

### Authentication Layers Identified
1. **Session Cookies**: Required for maintaining login state
2. **CSRF Tokens**: Present in forms and meta tags
3. **API Access Tokens**: Found in cookies (`apiV3AccessToken`)
4. **Hidden Form Fields**: Various tokens and state data

### Request Format Differences

#### Working Form Submission
- **URL**: `https://anytime.club-os.com/action/Dashboard/member/{member_id}`
- **Method**: POST
- **Content-Type**: `application/x-www-form-urlencoded`
- **Referer**: Same member profile URL
- **Data**: Form fields including hidden inputs and CSRF tokens

#### Failing API Call  
- **URL**: `https://anytime.club-os.com/action/Api/send-message`
- **Method**: POST
- **Content-Type**: `application/x-www-form-urlencoded` or `application/json`
- **Headers**: Various combinations of CSRF and Bearer tokens tried
- **Data**: Structured message data

### Header Analysis

#### Critical Headers for Form Submission
```http
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...
Accept: text/html,application/xhtml+xml,application/xml;q=0.9...
Content-Type: application/x-www-form-urlencoded
Referer: https://anytime.club-os.com/action/Dashboard/member/{member_id}
Origin: https://anytime.club-os.com
Cookie: [session cookies]
```

#### Attempted Headers for API Calls
```http
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...
Accept: application/json, text/plain, */*
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
X-CSRF-TOKEN: [extracted token]
Authorization: Bearer [api access token]
Referer: https://anytime.club-os.com/action/Dashboard/member/{member_id}
Origin: https://anytime.club-os.com
Cookie: [session cookies]
```

## Hypotheses for API Failures

### 1. Session Context Requirements
The API endpoints may require specific session context that's only available after navigating through the member profile page, not just having valid session cookies.

### 2. Form-Specific Tokens
Hidden form fields may contain dynamically generated tokens or state data that the API endpoints expect but we're not capturing.

### 3. Request Origin Validation
The API may validate that requests originate from the correct page flow (member profile → form submission) rather than direct API calls.

### 4. Additional Authentication Layers
There may be additional authentication mechanisms beyond CSRF tokens and API access tokens that we haven't identified.

### 5. Rate Limiting or Session State
The API endpoints may have different rate limiting or session state requirements than form submissions.

## Research Methods Implemented

### 1. Token Capture System
- Extracts CSRF tokens from HTML pages
- Captures API access tokens from cookies
- Identifies hidden form fields and their values
- Analyzes JavaScript configurations

### 2. Traffic Analysis
- Compares working form submissions vs failing API calls
- Captures all headers, cookies, and data payloads
- Identifies differences in request patterns

### 3. Session State Monitoring
- Tracks authentication state throughout the workflow
- Monitors session cookie changes
- Validates token freshness and expiration

## Next Steps for Investigation

### 1. Network Traffic Monitoring
- Use browser developer tools to capture exact network requests for successful form submissions
- Compare byte-for-byte with our API attempt requests
- Identify any missed headers, parameters, or authentication data

### 2. JavaScript Analysis
- Examine client-side JavaScript that handles form submissions
- Look for additional data processing or token generation
- Check for any client-side validation or preprocessing

### 3. API Endpoint Discovery
- Investigate if there are different API endpoints we should be using
- Check for API versioning or alternative message sending endpoints
- Look for API documentation or configuration in the web interface

### 4. Session Flow Analysis
- Test if API calls work when made in the exact same session as a successful form submission
- Investigate timing requirements between authentication and API calls
- Check if specific pages must be visited before API calls

## Current Implementation Status

### ✅ Completed
- ClubOS API client with session management
- Authentication and login functionality
- Working form submission implementation
- Token capture and analysis system
- Traffic pattern comparison tools
- Comprehensive logging and debugging

### 🔄 In Progress
- API endpoint failure analysis
- Session state research
- Network traffic comparison

### 📋 Planned
- JavaScript client-side analysis
- Alternative API endpoint discovery
- Session timing investigation
- Rate limiting research

## Error Patterns Observed

### Common API Response Errors
- "Something isn't right" - Generic error message
- 401 Unauthorized - Despite valid session
- 403 Forbidden - Suggests permission or context issue
- 422 Unprocessable Entity - Suggests data format issue

### Success Indicators
- Form submissions: HTTP 200 with page redirect or success message
- Working requests: Presence of confirmation text or member profile update

## Recommendations for Resolution

### Immediate Actions
1. **Capture Complete Network Traffic**: Use browser dev tools to capture successful form submission
2. **JavaScript Inspection**: Analyze client-side code for form submission handling
3. **API Documentation**: Search for official API documentation or developer resources
4. **Support Contact**: Consider reaching out to ClubOS support for API guidance

### Technical Approaches
1. **Exact Request Replication**: Mirror successful form submissions exactly in API calls
2. **Progressive Enhancement**: Start with form submission approach, gradually modify to API-like calls
3. **Session State Preservation**: Ensure API calls maintain exact same session state as form submissions
4. **Alternative Endpoints**: Investigate other API endpoints that might handle messaging

## Conclusion
While we have successfully implemented the working form submission approach, the direct API endpoint approach remains elusive. The key insight is that form submission works reliably, suggesting that ClubOS does support programmatic message sending - we just need to understand what additional context or authentication the API endpoints require that form submissions provide automatically.

The focus should be on identifying the exact differences between what makes form submissions succeed and API calls fail, likely in the areas of session context, hidden authentication data, or request origin validation.