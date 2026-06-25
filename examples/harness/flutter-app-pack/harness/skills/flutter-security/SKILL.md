---
name: flutter-security
description: "Security patterns for Flutter. Trigger: auth, token, secure, encrypt, firebase auth, login, logout, keystore, certificate, .gitignore secrets."
context: auto
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
---

# Flutter Security Skill

## Auto-trigger conditions
- Files in `lib/core/security/` or `lib/data/datasources/auth_*.dart` modified.
- Keywords: auth, token, secure, encrypt, login, logout, sign-in, sign-out.
- Patterns: `SharedPreferences`, `hardcoded`, `http://`, plaintext password storage.

## Reference docs
Keep detailed security playbooks in your own project docs (for example
`docs/security/`) and link them here — auth flow + token storage, network/TLS
config, and encrypted local-storage setup. This skill enforces the rules below;
the project docs hold the implementation detail.

## Enforcement rules
1. OAuth tokens → SecureStorage only (never Hive/SharedPreferences).
2. Local-DB encryption key → SecureStorage (never hardcoded).
3. Personal-data local-DB boxes → opened with an AES cipher.
4. google-services.json, *.jks, key.properties → must be in .gitignore.
5. Ad SDK IDs and third-party keys → injected via `--dart-define`, not hardcoded.
6. Logout → full secure cleanup of tokens and cached user data.
7. Backend rules → enforce `auth.uid == userId` ownership checks.
8. Network → cleartext traffic blocked, TLS 1.2+ enforced.
9. Input → sanitized before storage.
10. Minimize PII stored locally — keep only what the app strictly requires.

## On trigger
1. Load your project's security docs (if any).
2. Check current code against the enforcement rules above.
3. Report violations with severity and a fix suggestion.
