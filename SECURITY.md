# Security Policy

## Supported state

This project is a local working build and has not been declared a hardened public release.

## Important privacy rule

Do not attach private photos, personal metadata, file-system paths containing private names, or session logs containing sensitive information to a public issue.

Use copied test images with private metadata removed whenever possible.

## Reporting a security problem

Report security concerns privately to the repository owner before opening a public issue.

Include:

- A plain description of the problem.
- The affected file or feature.
- Safe reproduction steps.
- The possible impact.
- Whether original photos or output files are at risk.

Do not include real personal photos unless the owner explicitly requests them through a trusted private method.

## Security boundaries

- The converter is intended to run locally.
- The project should not require administrator rights.
- No secrets or credentials should be stored in the repository.
- Dependencies should come from their normal package source.
- The unsigned executable may trigger Windows security warnings.
- A warning should not be bypassed for an executable obtained from an untrusted source.
