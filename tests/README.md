# Tests for Body-to-Behavior Recommender

This directory contains comprehensive unit tests for the Body-to-Behavior Recommender project.

## Test Structure

### `conftest.py`
- Common test fixtures for all test modules
- Sample data objects (users, sleep entries, nutrition, etc.)
- Shared test configuration

### `test_models.py`
- Tests for all Pydantic models in `models.py`
- Validates data structures and validation logic
- Tests for UserProfile, SleepEntry, NutritionEntry, ActivityEntry, MeasurementEntry
- Tests for catalog models (MusicTrack, MealTemplate, WorkoutTemplate)
- Tests for request/response DTOs (RecommendRequest, RecommendResponse, Feedback)

### `test_utils.py`
- Tests for pure utility functions in `utils.py`
- Mathematical helpers (clamp01, normalize01, mean_std)
- Time utilities (get_today_iso)
- Heart rate calculations (compute_hr_max, target_bpm_from_state)
- State-based helpers (energy_cap_from_state, zone_from_state)
- Preference and penalty calculations

### `test_services_isolated.py`
- Tests for core business logic functions
- Isolated tests that avoid circular import issues
- Domain selection logic
- Reward calculation algorithms
- Preference update mechanisms
- State computation components

### `test_endpoints.py`
- Integration tests for FastAPI endpoints (Note: Requires fixing circular imports)
- API endpoint behavior validation
- Request/response handling
- Error scenarios

## Running Tests

Run all working tests:
```bash
uv run pytest tests/test_models.py tests/test_utils.py tests/test_services_isolated.py -v
```

Run specific test files:
```bash
uv run pytest tests/test_models.py -v
uv run pytest tests/test_utils.py -v
uv run pytest tests/test_services_isolated.py -v
```

Run with coverage (if coverage tools are installed):
```bash
uv run pytest --cov=body_behavior_recommender tests/
```

## Test Coverage

The current test suite covers:
- ✅ **Models**: Comprehensive validation of all Pydantic models
- ✅ **Utils**: All pure utility functions and mathematical helpers
- ✅ **Services**: Core business logic (domain selection, rewards, preferences)
- ⚠️ **Endpoints**: Partial coverage (circular import issues need resolution)
- ❌ **Data Loader**: Not yet implemented
- ❌ **Database Layer**: Not yet implemented

## Known Issues

1. **Circular Import**: The services and endpoints modules have circular dependencies that prevent testing of some ranking functions and full endpoint testing.

2. **Database Tests**: Tests requiring MongoDB connections are not yet implemented.

## Future Improvements

1. Resolve circular import issues by refactoring module dependencies
2. Add MongoDB integration tests with test database
3. Add performance/load tests for recommendation endpoints
4. Add property-based testing with Hypothesis
5. Add tests for bandit algorithm behavior
6. Add end-to-end workflow tests

## Test Guidelines

- Use descriptive test names that explain the scenario
- Include both positive and negative test cases
- Mock external dependencies (database, file system)
- Keep tests isolated and independent
- Use fixtures for common test data
- Document complex test scenarios with comments