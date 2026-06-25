# flutter-app-pack

Opt-in example-harness for **Flutter app development**. Five `.claude/skills`
distilled from real Flutter projects, covering the build → test → ship loop.

## Suited repo type

`flutter_se_product` — a Flutter / Dart application (mobile or multi-platform)
where you want build-recovery, performance, security, testing, and local-storage
guidance wired into the harness.

## What it provides

| skill | purpose |
|---|---|
| `flutter-build` | Build-error recovery; pub / gradle / build_runner fixes |
| `flutter-perf` | Rebuild avoidance, `const`, RepaintBoundary, list / painter perf |
| `flutter-security` | Token & secure storage, `.gitignore` secrets, TLS, PII rules |
| `flutter-test` | Unit / widget / integration test structure + runner commands |
| `flutter-hive` | Hive local-DB patterns, TypeId rules, build_runner workflow |

## How to apply

1. Copy `harness/skills/*` into your repo's `.claude/skills/`.
2. The skills auto-trigger on their keywords (build errors, `_test.dart`,
   performance keywords, etc.) — no extra wiring needed.
3. Adjust the example class / provider names in each skill to your app's domain.

The examples assume a Riverpod + Hive + Firebase-style stack, but the rules and
workflows are stack-agnostic — generalize the snippets to your own packages.

## Notes

The source app's `ui-design` and `reader` skills were intentionally left out:
they were too domain-specific (game visuals / reading-app patterns) to
generalize cleanly. Build your own UI skill from the common base's `ui-design`.
