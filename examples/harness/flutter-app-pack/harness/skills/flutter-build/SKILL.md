---
name: flutter-build
description: "Flutter build recovery and environment setup. Trigger: build error, pub get, gradle, android/, ios/, compile error, version conflict."
context: auto
allowed-tools: Read, Bash, Edit, Write, Grep, Glob
---

# Flutter Build Skill

## Auto-trigger conditions
- Build errors or compile failures.
- `flutter pub get` failures.
- Files in `android/` or `ios/` modified.
- Keywords: build, gradle, compile, version conflict, dependency.

## Common error patterns and fixes

| Error | Fix |
|---|---|
| `version solving failed` | Check pubspec.yaml constraints. Try `flutter pub upgrade --major-versions`. |
| `*.g.dart not found` | Run `dart run build_runner build --delete-conflicting-outputs`. |
| `Gradle build failed` | Check build.gradle.kts: minSdk, compileSdk, signing config. |
| `riverpod_generator conflict` | Pin to `^2.4.0` (known analyzer issue). |
| `Hive TypeAdapter missing` | Verify `@HiveType` annotation, run build_runner. |
| `google-services.json not found` | Verify file exists at `android/app/google-services.json`. |
| `Firebase initialization failed` | Check `Firebase.initializeApp()` in main.dart. |
| `R8/ProGuard error` | Check proguard-rules.pro for missing keep rules. |

## Recovery procedure
1. Run `flutter clean`.
2. Run `flutter pub get`.
3. Run `dart run build_runner build --delete-conflicting-outputs` (if generated files involved).
4. Run `flutter analyze`.
5. Run `flutter build apk --debug`.
6. Report result.

## Post-build
- Update your project's change log if files were modified.
- Report the result with an error count summary.
