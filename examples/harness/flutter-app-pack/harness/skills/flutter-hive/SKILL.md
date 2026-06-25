---
name: flutter-hive
description: Flutter Hive — Local Storage
---

# Flutter Hive — Local Storage

## Rules
- typeId: never change, never duplicate. New models = max+1.
- HiveField: never change/delete existing numbers. Add sequentially at end.
- Always run `dart run build_runner build --delete-conflicting-outputs` after model changes.
- `part 'filename.g.dart';` required in model file header.

## Repository Pattern
```dart
class EntityRepository {
  Box<Entity> get _box => Hive.box<Entity>('entities');
  Future<void> save(Entity e) => _box.put(e.id, e);
  Entity? getById(String id) => _box.get(id);
  List<Entity> getAll() => _box.values.toList();
  Future<void> delete(String id) => _box.delete(id);
}
```

## Checklist
- [ ] `part '*.g.dart'` in model
- [ ] Unique typeId per model
- [ ] build_runner → .g.dart generated
- [ ] Adapters registered in HiveService
- [ ] Repository via Hive.box() (no lazy opening)
