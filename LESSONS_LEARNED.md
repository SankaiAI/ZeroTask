# Lessons Learned

This document captures important lessons learned during the development of the ZeroTask application to prevent future mistakes and improve development practices.

---

## Development Workflow & Tooling

### Google OAuth Client Propagation Delays Cause 404 Errors
**Date:** August 30, 2025
**Technology:** Google OAuth 2.0, Google Cloud Console
**Project Context:** ZeroTask Gmail integration

#### Context
We implemented Gmail OAuth 2.0 integration for the ZeroTask application. After setting up the OAuth client correctly in Google Cloud Console with proper redirect URIs and JavaScript origins, we encountered persistent 404 errors when trying to use the OAuth flow. All configuration appeared correct - client ID existed in console, redirect URIs matched, JavaScript origins were set properly.

#### What Happened
- OAuth client was properly configured in Google Cloud Console
- Client ID: 18963162183-4ala04s2aqftj8i253nvgih0mbscjeu2.apps.googleusercontent.com
- Redirect URI: http://localhost:8000/oauth2/callback  
- JavaScript origins: http://localhost:3001, http://localhost:3000
- Google's OAuth endpoint returned "404 Not Found" error consistently
- Frontend debugging showed perfect OAuth URL construction
- Backend callback endpoint was working correctly
- curl tests to Google's OAuth endpoint returned 404

#### Impact
This caused several hours of debugging and troubleshooting what appeared to be configuration issues, when it was actually normal propagation delay. Development was blocked while investigating non-existent configuration problems.

#### Root Cause
Google OAuth clients require propagation time through Google's systems after creation or modification. According to official Google documentation:
- Standard propagation time: 5 minutes to a few hours
- In some cases: up to 24 hours for full propagation  
- 404 errors on newly created OAuth clients are normal and temporary

#### Lesson
**When setting up Google OAuth clients, especially newly created ones, expect propagation delays that can cause 404 errors for several hours. This is documented, expected behavior, not a configuration error.**

#### Future Application
1. Always ask when OAuth client was created when troubleshooting 404 errors
2. Check Google's official documentation for propagation times before debugging
3. Wait at least 2-4 hours after creating OAuth client before extensive debugging
4. Document propagation times in development setup guides
5. For development teams, create OAuth clients well in advance of when they're needed
6. Include propagation delay warnings in OAuth setup documentation

#### Prevention Strategies
- **Before debugging OAuth 404s:** Check when the client was created
- **During setup:** Allow 2-24 hours for propagation before reporting issues
- **For teams:** Create OAuth clients at least 1 day before they're needed in development
- **Documentation:** Always mention propagation delays in OAuth setup guides

---

## Research and Planning

### Slack OAuth HTTPS Requirement Misinterpretation Led to Unnecessary Implementation
**Date:** August 30, 2025
**Technology:** Slack OAuth 2.0, HTTPS/SSL, Node.js/Express
**Project Context:** ZeroTask Slack integration

#### Context
During Slack OAuth 2.0 integration setup, a user requested HTTPS implementation after encountering an error message mentioning "https://localhost:8000/oauth2/slack/callback" was required. Without researching Slack's actual requirements for localhost development, HTTPS/SSL certificates were immediately implemented with significant code changes to support secure connections.

#### What Happened
- Error message suggested HTTPS was required for Slack OAuth callback
- Immediately implemented SSL certificates and HTTPS server configuration
- Updated all frontend API calls and backend endpoints to use HTTPS
- Encountered frontend connection issues and CORS complications
- Had to revert all HTTPS changes back to HTTP
- Later discovered Slack API actually accepts HTTP for localhost development environments

#### Impact
- Significant development time wasted implementing unnecessary HTTPS changes
- Additional time spent reverting all HTTPS-related code modifications
- Consumed excessive tokens on implementation and rollback
- Development momentum disrupted by pursuing wrong solution path
- User experience degraded during the unsuccessful HTTPS implementation attempt

#### Root Cause
Failed to research Slack's OAuth documentation before implementing major architectural changes. The error message was misleading - Slack OAuth actually supports HTTP for localhost development environments, and the issue likely required a simpler configuration fix in the Slack app settings.

#### Lesson
**Always research API documentation thoroughly before implementing major architectural changes like HTTPS/SSL. Question whether requirements make technical sense in the development context, and consider simpler configuration solutions first.**

#### Future Application
1. **Research First:** Always consult official API documentation before making architectural changes
2. **Use Research Tools:** Leverage WebSearch and official docs to verify requirements before implementation
3. **Question Assumptions:** Challenge whether complex solutions are actually needed for development environments
4. **Try Simple Solutions:** Check configuration options (like updating Slack app config) before code changes
5. **Validate Requirements:** Confirm that localhost development actually requires the same constraints as production
6. **Progressive Implementation:** Start with minimal changes and verify they solve the problem before major refactoring

#### Prevention Strategies
- **Before major changes:** Search "[API Provider] [feature] localhost development requirements"
- **During error resolution:** Check if the error is configuration-related rather than implementation-related
- **For OAuth setup:** Verify localhost vs production requirements in official documentation
- **Documentation review:** Always read the "Development" or "Testing" sections of API docs first
- **Sanity check:** Ask whether the proposed solution complexity matches the problem scope

---

## Template for Future Entries

### [Lesson Title]
**Date:** [Date]
**Technology:** [Tech stack involved]
**Project Context:** [Brief project context]

#### Context
[Situation and circumstances]

#### What Happened
[The mistake, discovery, or insight]

#### Impact
[Consequences or effects observed]

#### Root Cause
[What actually caused the issue]

#### Lesson
[Key takeaway in bold, actionable terms]

#### Future Application
[How to apply this knowledge going forward]

#### Prevention Strategies
[Specific steps to avoid this issue in the future]