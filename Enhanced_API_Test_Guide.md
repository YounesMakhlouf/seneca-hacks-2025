# Enhanced Body-to-Behavior Recommender API - Postman Test Collection
# Server: http://127.0.0.1:8000

## 🚀 ENHANCED DATA INTEGRATION
Now using the largest and most comprehensive datasets available!

### Dataset Overview:
- **users.json**: ~100,000 users (vs 10,000 previously)
- **sleep.json**: ~29M sleep entries (vs 300k previously)
- **activities.json**: ~20M activity entries (vs 300k previously)
- **measurements.json**: ~960k body composition measurements (NEW!)
- **heart_rate.json**: ~131M heart rate readings (available but not loaded due to size)

## NEW ENHANCED ENDPOINTS

### 1. Enhanced Data Summary
**GET** `http://127.0.0.1:8000/data-summary`
- Shows the scale of enhanced data loading
- Includes measurement datasets and enhanced metrics
- Data source information

### 2. Enhanced User Summary
**GET** `http://127.0.0.1:8000/users/user_000001/summary`
- Now includes body measurement counts
- Enhanced date ranges for all data types
- Latest measurement information
- Try with: user_000001, user_001000, user_010000, user_050000

### 3. User Body Measurements (NEW!)
**GET** `http://127.0.0.1:8000/users/user_000001/measurements?limit=10`
- Body composition data: weight, body fat, muscle mass, BMI
- Waist, chest, bicep, thigh measurements
- Body water percentage
- Historical tracking data

### 4. Enhanced Recent Data
**GET** `http://127.0.0.1:8000/users/user_000001/recent?days=30`
- Now includes recent measurements
- More comprehensive activity tracking
- Enhanced sleep data with quality metrics

## EXISTING ENDPOINTS (NOW ENHANCED)

### 5. Enhanced User State
**GET** `http://127.0.0.1:8000/state?user_id=user_000001`
- More accurate physiological state computation
- Based on comprehensive historical data
- Better activity and recovery patterns

### 6. Enhanced Recommendations
**POST** `http://127.0.0.1:8000/recommend`
**Headers:** Content-Type: application/json
**Body:**
```json
{
    "user_id": "user_000001",
    "intent": "workout",
    "hours_since_last_meal": 2.5,
    "now": "2025-09-13T14:30:00"
}
```
- More personalized based on extensive user history
- Better contextual understanding

## SAMPLE USER IDs FOR TESTING
With ~100,000 users now available:
- **Beginner range**: user_000001 - user_010000
- **Mid range**: user_025000 - user_050000
- **Advanced range**: user_075000 - user_099999

## ENHANCED DATA INSIGHTS

### Sleep Data Enhancements:
- **Sleep quality scores** (Good, Fair, Poor)
- **Detailed sleep efficiency** percentages
- **Awakening counts** during night
- **Sleep stage transitions**

### Activity Data Enhancements:
- **Activity types**: Running, Cycling, Swimming, Pilates, Weight Training, etc.
- **Intensity levels**: Low, Moderate, High, Peak
- **Elevation gain** for outdoor activities
- **Heart rate zones** during activities

### Body Measurements:
- **Comprehensive body composition**: Body fat %, muscle mass, BMI
- **Body measurements**: Waist, chest, bicep, thigh circumferences
- **Metabolic indicators**: Body water percentage
- **Progress tracking** over time

## PERFORMANCE OPTIMIZATIONS
- **Memory-efficient loading**: 1M entry limits for large datasets
- **Chunked processing**: Handles massive files without memory overflow
- **Smart fallbacks**: Graceful degradation if enhanced data unavailable
- **User data calculated fields**: BMI and goals auto-calculated if missing

## TESTING STRATEGY
1. **Start with data-summary** to confirm enhanced loading
2. **Pick diverse user IDs** to see data variety
3. **Test measurements endpoint** for body composition insights
4. **Compare state calculations** between different user types
5. **Verify recommendations** reflect enhanced personalization

## ENHANCED FEATURES VERIFICATION
- ✅ Larger user base (100k vs 10k)
- ✅ Massive sleep dataset (29M vs 300k entries)
- ✅ Comprehensive activity data (20M vs 300k entries)
- ✅ New body measurements data (960k entries)
- ✅ Enhanced state computation accuracy
- ✅ Memory-optimized large dataset handling