# Security Plan

## Threat Model
Primary threats:
- prompt injection from project content
- malicious .blend files
- malicious Python scripts
- arbitrary code execution
- credential theft
- cross-project data leakage
- unauthorized tool execution
- compromised coding agent
- provider abuse
- runaway costs

## Controls
1. Least privilege.
2. Structured tools.
3. Input validation.
4. Dual validation in backend and add-on.
5. Approval gates.
6. Project isolation.
7. Credential encryption.
8. Secret redaction.
9. Audit logging.
10. Rate and usage limits.
11. Coding-agent sandboxing.
12. File/path allowlists.
13. Network restrictions.
14. Signed/versioned tool definitions.
15. Secure streaming connections.

## Blender-Specific
Blender documentation explicitly warns that Python scripts embedded in blend files can execute code and pose a security risk. Treat all external project files as untrusted input.

## High Risk
Arbitrary scripts, shell commands, external file changes and destructive bulk operations require explicit confirmation and should be disabled by default in MVP.
