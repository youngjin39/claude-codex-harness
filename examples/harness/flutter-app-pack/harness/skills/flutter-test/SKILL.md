---
name: flutter-test
description: "Flutter test patterns and runner. Trigger: test, _test.dart, TDD, coverage, widget test, unit test, integration test."
context: auto
allowed-tools: Read, Bash, Edit, Write, Grep, Glob
---

# Flutter Test Skill

## Auto-trigger conditions
- Files ending in `_test.dart` created or modified.
- Keywords: test, TDD, coverage, verify, validate.
- After feature implementation (post-completion hook).

## Test structure

```
test/
├── core/           # Shared utilities / helpers
├── domain/         # Entity and value-object tests
├── usecases/       # Use-case unit tests
├── widgets/        # Widget unit tests
├── pages/          # Page smoke tests
└── integration/    # Integration-level scenarios

integration_test/
└── app_test.dart   # Full flow (emulator required)
```

## Test patterns

### Unit test (domain/data)
```dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('StringUtils', () {
    test('capitalizes the first letter', () {
      expect(StringUtils.capitalize('hello'), 'Hello');
    });
  });
}
```

### Widget test (presentation)
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('MyWidget renders its label', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(home: MyWidget(label: 'Hello')),
      ),
    );
    expect(find.text('Hello'), findsOneWidget);
  });
}
```

### Provider override in tests
```dart
await tester.pumpWidget(
  ProviderScope(
    overrides: [
      userRepositoryProvider.overrideWithValue(MockUserRepo()),
      dataRepositoryProvider.overrideWithValue(MockDataRepo()),
    ],
    child: const MaterialApp(home: LoginPage()),
  ),
);
```

## Test commands
```bash
flutter test                          # All tests
flutter test --reporter expanded      # Verbose output
flutter test test/core/               # Specific directory
flutter test integration_test/        # Integration (needs emulator)
```

## Rules
- Every new feature needs at least 1 test.
- Security-related code needs dedicated security tests.
- Test names describe behavior, not implementation.
- Use `group()` to organize related tests.
- Mock external dependencies (local DB, backend) in tests.
