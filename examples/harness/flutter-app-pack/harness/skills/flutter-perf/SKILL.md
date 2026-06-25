---
name: flutter-perf
description: "Flutter performance optimization. Trigger: slow, lag, jank, FPS, memory, rebuild, performance, optimization."
context: auto
allowed-tools: Read, Bash, Grep, Glob, Edit
---

# Flutter Performance Skill

## Auto-trigger conditions
- Keywords: slow, lag, jank, FPS, memory, rebuild, performance, optimization.
- Widget rebuild issues detected.
- Large list or custom-painted surface rendering.

## Common Performance Patterns

### 1. Avoid Unnecessary Rebuilds
```dart
// BAD: entire tree rebuilds
ref.watch(someProvider);

// GOOD: select specific field
ref.watch(someProvider.select((s) => s.relevantField));
```

### 2. const Constructors
```dart
// Always use const where possible
const SizedBox(height: 16),
const Text('Static text'),
```

### 3. RepaintBoundary for CustomPainter
```dart
// Wrap heavy painters
RepaintBoundary(
  child: CustomPaint(painter: MyPainter(...)),
)
```

### 4. ListView.builder for Large Lists
```dart
// Never use Column + children for lists
ListView.builder(
  itemCount: items.length,
  itemBuilder: (ctx, i) => ItemWidget(items[i]),
)
```

### 5. Image/Asset Caching
```dart
// Pre-cache images
precacheImage(AssetImage('assets/icon.png'), context);
```

### 6. CustomPainter Optimization
- Only repaint when the painted state actually changed.
- Implement `shouldRepaint` correctly in CustomPainter.
- Move heavy computation off the UI thread with an isolate.

## Diagnostic Commands
```bash
flutter run --profile                    # Profile mode
flutter run --profile --trace-startup    # Startup trace
flutter analyze --no-pub                 # Static analysis only
```

## Metrics
- Target: 60 FPS on mid-range devices.
- Frame build + raster: < 16ms per frame.
- App cold start: < 1s.
- Heavy background computation: keep off the UI thread (isolate).
