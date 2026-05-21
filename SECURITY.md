# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported |
|---------|-----------|
| >= 2.0.0 | :white_check_mark: |
| < 2.0.0 | :x: |

## Reporting a Vulnerability

We take security issues seriously. Please do **not** report security
vulnerabilities via public GitHub issues.

Instead, report them privately by emailing the maintainer at
**[hopcy.forcy@gamil.com](mailto:hopcy.forcy@gamil.com)**.

You should receive a response within **48 hours**. If for some reason you
do not, please follow up to ensure we received your original message.

### What to include

- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if any)
- Your contact information for follow-up

### Disclosure policy

When we receive a security report, we will:

1. Confirm receipt within 48 hours.
2. Assess the issue and determine affected versions.
3. Develop and test a fix.
4. Release a security patch as soon as possible, coordinated
   with the disclosure date (typically 90 days after the report).

We believe in coordinated disclosure and will work with reporters to
determine an appropriate timeline for public disclosure.

## Security-related configuration

### Production deployment

- Always use environment variables for secrets (database URLs, API keys).
- Set `DEBUG=False` in production (`nexyconfig.py`).
- Use HTTPS in production (configure via `nexyconfig.py` or a reverse proxy).
- Keep your Nexy version up to date.

### Reporting non-security bugs

For non-security bugs, please open a [GitHub issue](https://github.com/NexyPy/nexy/issues/new/choose).
