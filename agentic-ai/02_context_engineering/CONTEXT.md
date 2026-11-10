# 0. The Challenge of Implicit Context and Architecture

## Prompt used
```
You are a senior software developer.
The project uses JavaScript. 

Given the existing file @user.service.js and @user.repository.js 

Task: Generate a new data export service. 
Constraint: Reproduce exactly the repository access pattern and exception handling.
```

## Files provided 

- `/src/services/user.service.js`
- `/src/repositories/user.repository.js`

## File generated
Name: DataExportService
Path: `/src/services/data-export.service.js`

## Summary of existing architecture elementts reused by AI 

| Element | How it was reused |
|--------|-------------------|
| **Layering** | Service in `src/services/` depends on `src/repositories/` only (no direct access to the in-memory store). |
| **Repository access** | `require('../repositories/user.repository')` and delegation to `findByEmail(email)` on the exported singleton. |
| **Singleton export** | `module.exports = new DataExportService()` matches `UserService` / `UserRepository`. |
| **Exception handling** | After a repository lookup, `if (!user)` then `throw new Error("User not found in the system")`. |
| **Async service API** | Public method is `async`, consistent with `getUserProfile`, even though the repository call is synchronous. |
| **Data source** | Same in-memory `Map` and seed user (`dev@entreprise.com`) as defined in `user.repository.js`. |