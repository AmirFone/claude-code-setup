# Technology Stack Preferences

## Language Hierarchy

1. **TypeScript** - Primary language for all new development
2. **Python** - Only when explicitly required (ML, data science)
3. **Bash** - For simple scripts and automation
4. **Go** - For performance-critical CLI tools

## Runtime Preferences

| Category | Preferred | Alternative | Avoid |
|----------|-----------|-------------|-------|
| **JS Runtime** | Bun | Node.js | Deno |
| **Package Manager** | bun | pnpm | npm/yarn |
| **Python Env** | uv | poetry | pip |
| **Containers** | Docker | Podman | - |

## Framework Preferences

### Frontend
- **React** with TypeScript
- **Tailwind CSS** for styling
- **Vite** for bundling

### Backend
- **Bun.serve** for HTTP servers
- **FastAPI** when Python required
- **PostgreSQL** for databases

### Testing
- **Bun test** for TypeScript
- **pytest** for Python
- **Playwright** for E2E

## Code Style

- **Functional** > Object-oriented (prefer composition)
- **Explicit** > Implicit (clear over clever)
- **Simple** > Complex (avoid over-engineering)
- **Types** everywhere (no `any` in TypeScript)

## Infrastructure

| Service | Provider | Purpose |
|---------|----------|---------|
| Serverless | Cloudflare Workers | Edge functions |
| Database | Supabase | PostgreSQL + Auth |
| Storage | S3/R2 | File storage |
| CI/CD | GitHub Actions | Automation |

## Security Defaults

- No secrets in code (use env vars)
- No `eval()` or dynamic code execution
- Validate all external input
- Use parameterized queries (no SQL string concat)

## Notes

- Override these preferences only with explicit approval
- Document any deviations in project README
- Prefer ecosystem consistency within projects
