# Weather Data Analytics Platform

**Complete weather data analysis system with data collection, quality assurance, insights generation, and interactive visualization.**

## 🚀 Quick Start

### Requirements
```bash
pip install aiohttp matplotlib
```

### Generate Temperature Charts
```bash
# Collect data and generate charts
python main.py

# Or just generate charts from existing data
python generate_charts.py
```

### View Results
Charts are saved as PNG images in the `results/` folder:
- `hourly_*.png` - Temperature changes by hour for each city
- `daily_*.png` - Daily temperature trends for each city

### Run Specific Stages
```bash
python main.py --collect                    # Collect data only
python main.py --analyze                    # Analyze data only  
python main.py --quality                    # Quality check only
python main.py --visualize                  # Generate charts only
```

### Customize
```bash
python main.py --days 14 --cities Moscow Sochi  # 14 days, specific cities
```

---

## 📊 Project Structure

```
weather-platform/
├── main.py                   # Main orchestrator (RUN THIS)
├── data_collector.py         # Stage 1: Async data collection
├── data_analyzer.py          # Stage 2: Insights & patterns
├── data_quality.py           # Stage 3: Quality validation
├── data_visualizer.py        # Stage 4: Generate charts
├── chart_generator.py        # PNG chart generator
├── README.md                 # This file
│
├── data/
│   └── weather_data.db      # SQLite database
├── logs/
│   └── weather_platform.log # Execution logs
└── results/
    ├── hourly_*.png          # ⭐ Hourly temperature charts
    ├── daily_*.png           # ⭐ Daily temperature trends
    ├── report_*.txt          # ASCII text report
    ├── analytics_*.json      # Analysis results
    └── quality_report_*.json # Quality metrics
```

---

## 📋 Pipeline Stages

### Stage 1: Data Collection (`data_collector.py`)
- **Async parallel collection** from Open-Meteo API (10+ cities simultaneously)
- **No API keys required** - completely free
- **Configurable period** (1-16 days, default: 10)
- **SQLite storage** with 3 tables:
  - `weather_current`: Current conditions
  - `weather_daily`: Daily forecasts
  - `weather_hourly`: Hourly data

**Usage:**
```bash
python data_collector.py
```

**Or in code:**
```python
from data_collector import DataCollector
import asyncio

collector = DataCollector(forecast_days=10)
data = asyncio.run(collector.collect_batch(collector.DEFAULT_CITIES))
```

---

### Stage 2: Data Analysis (`data_analyzer.py`)
- **Temperature trend analysis** (min/max/avg, daily changes)
- **Precipitation patterns** (total, rainy days, intensity)
- **Actionable insights** with severity levels and recommendations
- **Pattern detection** (climate comparison, extremes, anomalies)

**Output insights include:**
- 🌡️ High/Low temperature warnings
- 💧 Heavy rainfall alerts
- 📊 Climate anomalies
- 🎯 Actionable recommendations

**Usage:**
```bash
python data_analyzer.py
```

**Or in code:**
```python
from data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()
trends = analyzer.analyze_temperature_trends()
precip = analyzer.analyze_precipitation()
insights = analyzer.generate_insights()

for insight in insights:
    print(f"{insight['city']}: {insight['message']}")
    print(f"Action: {insight['recommendation']}")
```

---

### Stage 3: Data Quality (`data_quality.py`)
- **Completeness check** (% of filled fields, target: 95%+)
- **Anomaly detection** (unrealistic values, extreme ranges)
- **Validity validation** (temperature -50 to 50°C, humidity 0-100%)
- **Quality score** (0-100%) considering all metrics

**Quality Report includes:**
```json
{
  "quality_score": 95.3,
  "avg_completeness": 98.0,
  "anomalies_detected": 2,
  "metrics": {
    "cities_analyzed": 10,
    "data_issues": "minimal"
  }
}
```

**Usage:**
```bash
python data_quality.py
```

**Or in code:**
```python
from data_quality import DataQuality

quality = DataQuality()
report = quality.generate_quality_report()

print(f"Quality Score: {report['quality_score']:.1f}%")
print(f"Completeness: {report['metrics']['avg_completeness']:.1f}%")
```

---

### Stage 4: Visualization (`data_visualizer.py` + `chart_generator.py`)
- **PNG Temperature Charts** for hourly and daily data
- **Automatic chart generation** with min/max annotations
- **Multiple charts** - one per city
- **Professional styling** with grid, legends, and labels

**Generated Files:**
- `hourly_*.png`: Hourly temperature changes with min/max points marked
- `daily_*.png`: Daily temperature trends (max, min, average)
- `report_*.txt`: ASCII formatted statistics

**Usage:**
```bash
# Generate charts after collecting data
python main.py

# Or just generate charts from existing data
python generate_charts.py
```

**Or in code:**
```python
from chart_generator import TemperatureChartGenerator

generator = TemperatureChartGenerator('data/weather_data.db')
hourly_files = generator.generate_hourly_charts()
daily_files = generator.generate_daily_charts()

for chart_file in hourly_files + daily_files:
    print(f"Generated: {chart_file}")
```

---

## 🎯 Main Entry Point (`main.py`)

Orchestrates all stages with options:

```
Options:
  --days N              Forecast days (1-16, default: 10)
  --cities C1 C2 ...   Specific cities (default: all)
  --collect            Run collection only
  --analyze            Run analysis only
  --quality            Quality check only
  --visualize          Visualization only
  --all                Run all stages (default)
```

**Examples:**
```bash
# Full pipeline
python main.py

# Specific days and cities
python main.py --days 7 --cities Moscow Sochi Omsk

# Only quality check
python main.py --quality

# Collection + visualization
python main.py --collect --visualize
```

---

## 📊 Supported Cities (Default)

| City | Region | Coordinates |
|------|--------|-------------|
| **Moscow** | Central | 55.76°N, 37.62°E |
| **Saint-Petersburg** | Northwest | 59.94°N, 30.26°E |
| **Novosibirsk** | Siberia | 55.04°N, 82.85°E |
| **Yekaterinburg** | Urals | 56.84°N, 60.61°E |
| **Vladivostok** | Far East | 43.12°N, 131.87°E |
| **Sochi** | South | 43.60°N, 39.73°E |
| **Kazan** | Volga | 55.80°N, 49.11°E |
| **Krasnoyarsk** | Central Siberia | 56.02°N, 92.89°E |
| **Omsk** | West Siberia | 54.99°N, 73.32°E |
| **Samara** | Volga | 53.20°N, 50.10°E |

**Add custom cities:**
```python
cities = [
    {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
    {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
]
```

---

## 💾 Data Storage

**SQLite Database:** `data/weather_data.db`

### weather_current
```sql
SELECT * FROM weather_current LIMIT 1;
-- city | temperature | humidity | wind_speed | collected_at
```

### weather_daily
```sql
SELECT * FROM weather_daily WHERE city='Moscow' LIMIT 3;
-- city | date | temp_max | temp_min | precipitation | collected_at
```

---

## 📈 Output Examples

### JSON Analytics Report
```json
{
  "temperature_analysis": {
    "Moscow": [
      {"date": "2024-01-15", "max": 6.5, "min": 2.1, "avg": 4.3},
      {"date": "2024-01-16", "max": 4.2, "min": -1.3, "avg": 1.45}
    ]
  },
  "insights": [
    {
      "type": "temperature",
      "city": "Moscow",
      "severity": "HIGH",
      "message": "High average max temperature: 25.0°C",
      "recommendation": "Prepare cooling systems"
    }
  ]
}
```

### Quality Report
```json
{
  "quality_score": 95.3,
  "completeness": {
    "Moscow": {
      "total_records": 100,
      "temperature_filled": 98,
      "completeness_percent": 98.0
    }
  },
  "anomalies": {
    "Moscow": {
      "has_issues": false,
      "anomalies": []
    }
  }
}
```

### Text Report
```
CITY STATISTICS:
----------------------------------------------------------------------
City                 Avg Temp     Max        Min        Records   
----------------------------------------------------------------------
Moscow               4.5°C        8.2°C      -2.1°C     100       
Saint-Petersburg     2.3°C        5.8°C      -3.5°C     100       
...
```

---

## 🔍 Performance Metrics

| Metric | Value |
|--------|-------|
| Collection Speed (10 cities) | 10-20 seconds |
| Data Completeness | 95-100% |
| Database Size Per Run | ~50 KB |
| Analysis Time | < 1 second |
| Report Generation | < 2 seconds |
| Quality Check | < 1 second |

---

## 🛠️ Advanced Usage

### Custom Analysis
```python
from data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()

# Get temperature trends
trends = analyzer.analyze_temperature_trends()
for city, data in trends.items():
    print(f"{city}: {len(data)} days of data")

# Get precipitation data
precip = analyzer.analyze_precipitation()
for city, stats in precip.items():
    print(f"{city}: {stats['total']}mm total, {stats['days']} rainy days")
```

### Direct Database Queries
```python
import sqlite3

with sqlite3.connect('data/weather_data.db') as conn:
    cursor = conn.execute('''
        SELECT city, AVG(temperature) as avg_temp
        FROM weather_current
        GROUP BY city
        ORDER BY avg_temp DESC
    ''')
    
    for city, avg_temp in cursor:
        print(f"{city}: {avg_temp:.1f}°C")
```

### Continuous Monitoring
```bash
# Run every hour
while true; do
    python main.py --collect
    sleep 3600
done
```

---

## 🎓 What You'll Learn

- ✅ Asynchronous Python (asyncio, aiohttp)
- ✅ REST API integration
- ✅ Database design & SQL
- ✅ Data analysis & insights generation
- ✅ Data quality metrics
- ✅ Data visualization (Plotly)
- ✅ Report generation

---

## 📝 Example Workflow

```bash
# 1. Collect data for 7 days
python main.py --days 7 --collect

# 2. Analyze and generate insights
python main.py --analyze

# 3. Check data quality
python main.py --quality

# 4. Create visualizations
python main.py --visualize

# 5. View results in results/ folder
ls results/
```

---

## ⚠️ Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'aiohttp'`
```bash
pip install aiohttp
```

**Problem:** API not responding
- Check internet connection
- API may be temporarily unavailable (try again later)

**Problem:** No data in database
- Ensure collection ran successfully: `python data_collector.py`
- Check logs: `cat logs/weather_platform.log`

**Problem:** Permission denied
- Run terminal as administrator (Windows)
- Or use: `sudo python main.py` (Linux/Mac)

---

## 📊 Data Flow Diagram

```
┌─────────────┐
│ Open-Meteo  │
│    API      │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│ data_collector.py        │ ◄─ Stage 1: Async Collection
│ (10 cities parallel)     │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ data/weather_data.db     │
│ (SQLite 3 tables)        │ ◄─ Stage 5: Storage
└──────┬───────────────────┘
       │
       ├──────────────────────────┐
       │                          │
       ▼                          ▼
┌──────────────────────┐  ┌──────────────────────┐
│ data_analyzer.py     │  │ data_quality.py      │
│ (Insights)           │  │ (Validation)         │
└──────┬───────────────┘  └──────┬───────────────┘
       │                         │
       ├─────────────┬───────────┤
       │             │           │
       ▼             ▼           ▼
    insights    quality_report  completeness
       │             │           │
       └─────────────┼───────────┘
                     │
                     ▼
         ┌──────────────────────────┐
         │ data_visualizer.py       │
         │ (HTML, TXT, JSON)        │ ◄─ Stage 4: Visualization
         └──────┬───────────────────┘
                │
                ├────────────────┬─────────────┐
                ▼                ▼             ▼
           dashboard.html   report.txt   analytics.json
           (Interactive)    (ASCII)      (Structured)
```

---

## 🎯 Use Cases

### 🚗 Transportation & Logistics
- Route optimization based on weather
- Frost/ice warnings for safety
- Fuel consumption prediction

### ⚡ Energy Management
- Heating/cooling demand forecasting
- Energy consumption optimization
- Peak load planning

### 🌾 Agriculture
- Irrigation scheduling
- Crop yield prediction
- Frost/hail damage prevention

### 🏥 Public Health
- Disease spread correlation
- Heat-related illness prevention
- Air quality monitoring

---

## 📞 Support & Documentation

- **Logs:** `logs/weather_platform.log`
- **Results:** `results/` folder
- **Database:** `data/weather_data.db` (SQLite viewer available online)

---

## ✨ Features Summary

| Feature | Status |
|---------|--------|
| Async data collection | ✅ |
| Multi-city support | ✅ |
| Configurable periods | ✅ |
| Temperature analysis | ✅ |
| Precipitation analysis | ✅ |
| Insight generation | ✅ |
| Quality validation | ✅ |
| Anomaly detection | ✅ |
| HTML dashboard | ✅ |
| Text reports | ✅ |
| JSON export | ✅ |
| SQL database | ✅ |
| Error handling | ✅ |
| Logging | ✅ |

---

## 📈 Version & Status

- **Version:** 2.0
- **Status:** ✅ Production Ready
- **Python:** 3.8+
- **License:** MIT
- **Last Updated:** 2024-01-15

---

## 🎉 Quick Commands Reference

```bash
# Full pipeline (collect + analyze + quality + charts)
python main.py

# Just generate PNG charts from existing data
python generate_charts.py

# Collect data for specific period and cities
python main.py --days 14 --cities Moscow Sochi Vladivostok

# Single stages
python data_collector.py      # Collect only
python data_analyzer.py       # Analyze only
python data_quality.py        # Quality check only
python generate_charts.py     # Generate PNG charts

# View logs
tail -f logs/weather_platform.log

# List generated charts
ls -la results/*.png
```

---

**Ready to analyze weather data? Start with `python main.py`!** 🌤️
