# Security

JobFit's public application processes resume text in the browser and does not require a JobFit application backend to store uploaded resumes.

## Reporting a vulnerability

If you discover a security or privacy issue, please do not include real resume data, credentials, access tokens, or other sensitive personal information in a public GitHub issue.

Instead, use GitHub's private vulnerability reporting feature for this repository when available.

Include:

- the affected component
- reproduction steps using synthetic data
- expected vs. observed behavior
- browser / environment details when relevant

## Scope

Security-sensitive areas include:

- client-side document parsing
- third-party browser dependencies
- model and asset loading
- GitHub Pages deployment
- accidental transmission or persistence of resume content

## Privacy principle

JobFit is designed so that the public application can perform document parsing and matching without a JobFit backend storing candidate documents. Any future architecture change that introduces server-side resume handling should update both this policy and the product disclosure before release.
