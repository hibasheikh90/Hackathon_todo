# ADR-002: JWT Security Strategy

**Status**: Accepted
**Date**: 2026-01-31
**Deciders**: Engineering Team

## Context

We need a secure authentication mechanism for our full-stack todo application that allows users to sign up, log in, and securely access their personal tasks. The solution must work across both frontend (Next.js) and backend (FastAPI) while ensuring proper user data isolation.

## Decision

We will use Better Auth for frontend authentication combined with custom JWT verification middleware in FastAPI. Better Auth will handle user registration, login, password hashing, and JWT token generation. FastAPI will verify JWT tokens using a custom dependency that extracts the current user information.

## Rationale

- **Security**: Better Auth is a well-maintained, security-focused authentication library with built-in protections against common vulnerabilities
- **Developer Experience**: Provides React hooks and easy integration with Next.js
- **Flexibility**: Allows us to customize JWT payload and implement custom authorization logic in FastAPI
- **Maintainability**: Reduces custom security code that could introduce vulnerabilities
- **Performance**: JWTs eliminate server-side session storage while enabling stateless API authentication

## Approach

1. **Frontend Integration**:
   - Configure Better Auth with JWT plugin
   - Use Better Auth hooks for authentication state management
   - Automatically attach JWT tokens to API requests

2. **Backend Integration**:
   - Implement JWT verification middleware using Python-JOSE or similar
   - Create FastAPI dependency to extract current user from token
   - Inject current_user into protected endpoints

3. **Token Management**:
   - Use RS256 algorithm for stronger security
   - Set appropriate expiration times (15 min access tokens, 7 days refresh tokens)
   - Implement secure token refresh mechanism

## Consequences

### Positive
- Reduces custom security implementation, lowering vulnerability risk
- Provides industry-standard authentication solution
- Enables scalable, stateless API architecture
- Integrates well with both Next.js and FastAPI ecosystems

### Negative
- Creates dependency on Better Auth library
- Requires careful secret/key management
- Need to handle token refresh and expiration properly
- Additional complexity in debugging authentication issues

## Alternatives Considered

1. **Custom JWT Implementation**: Higher security risk due to potential implementation flaws
2. **Simple Sessions**: Would require server-side session storage and complicate scaling
3. **OAuth-only**: Doesn't meet requirement for email/password authentication
4. **Supabase Auth**: Would tie us to specific provider, reducing flexibility