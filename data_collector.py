import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import List, Dict
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class DataCollector:
    
    DEFAULT_CITIES = [
        {'name': 'Москва', 'lat': 55.7558, 'lon': 37.6173},
        {'name': 'Санкт-Петербург', 'lat': 59.9404, 'lon': 30.2639},
        {'name': 'Новосибирск', 'lat': 55.0412, 'lon': 82.8463},
        {'name': 'Екатеринбург', 'lat': 56.8389, 'lon': 60.6057},
        {'name': 'Владивосток', 'lat': 43.1196, 'lon': 131.8728},
        {'name': 'Сочи', 'lat': 43.6028, 'lon': 39.7314},
        {'name': 'Казань', 'lat': 55.7964, 'lon': 49.1061},
        {'name': 'Красноярск', 'lat': 56.0153, 'lon': 92.8932},
        {'name': 'Омск', 'lat': 54.9885, 'lon': 73.3242},
        {'name': 'Самара', 'lat': 53.1956, 'lon': 50.1019},
    ]
    
    def __init__(self, forecast_days: int = 10):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.forecast_days = min(max(forecast_days, 1), 16)
        self.db_path = Path('data/weather_data.db')
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS weather_current (
                    id INTEGER PRIMARY KEY,
                    city TEXT UNIQUE,
                    temperature REAL,
                    humidity INTEGER,
                    wind_speed REAL,
                    collected_at TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS weather_daily (
                    id INTEGER PRIMARY KEY,
                    city TEXT,
                    date DATE,
                    temp_max REAL,
                    temp_min REAL,
                    precipitation REAL,
                    collected_at TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS weather_hourly (
                    id INTEGER PRIMARY KEY,
                    city TEXT,
                    hour TEXT,
                    temperature REAL,
                    collected_at TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    async def fetch_city_weather(self, session: aiohttp.ClientSession, 
                                 city: Dict) -> Dict:
        params = {
            'latitude': city['lat'],
            'longitude': city['lon'],
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m',
            'hourly': 'temperature_2m',
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
            'timezone': 'auto',
            'forecast_days': self.forecast_days
        }
        
        try:
            async with session.get(self.base_url, params=params, 
                                  timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'city': city['name'],
                        'data': data,
                        'collected_at': datetime.now().isoformat()
                    }
                else:
                    logger.warning(f"Ошибка API для {city['name']}: {response.status}")
                    return None
        except Exception as e:
            logger.warning(f"Ошибка получения данных для {city['name']}: {e}")
            return None
    
    async def collect_batch(self, cities: List[Dict]) -> List[Dict]:
        logger.info(f"Сбор данных для {len(cities)} городов ({self.forecast_days} дней)...")
        
        collected = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_city_weather(session, city) for city in cities]
            results = await asyncio.gather(*tasks, return_exceptions=False)
            collected = [r for r in results if r is not None]
        
        self._save_to_db(collected)
        logger.info(f"Собрано {len(collected)}/{len(cities)} городов")
        
        return collected
    
    def _save_to_db(self, collected_data: List[Dict]):
        with sqlite3.connect(self.db_path) as conn:
            for item in collected_data:
                city = item['city']
                data = item['data']
                collected_at = item['collected_at']
                
                if 'current' in data:
                    current = data['current']
                    conn.execute('''
                        INSERT OR REPLACE INTO weather_current 
                        (city, temperature, humidity, wind_speed, collected_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        city,
                        current.get('temperature_2m'),
                        current.get('relative_humidity_2m'),
                        current.get('wind_speed_10m'),
                        collected_at
                    ))
                
                if 'daily' in data:
                    daily = data['daily']
                    times = daily.get('time', [])
                    max_temps = daily.get('temperature_2m_max', [])
                    min_temps = daily.get('temperature_2m_min', [])
                    precips = daily.get('precipitation_sum', [])
                    
                    for i, date in enumerate(times):
                        conn.execute('''
                            INSERT INTO weather_daily
                            (city, date, temp_max, temp_min, precipitation, collected_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            city, date,
                            max_temps[i] if i < len(max_temps) else None,
                            min_temps[i] if i < len(min_temps) else None,
                            precips[i] if i < len(precips) else None,
                            collected_at
                        ))
                
                if 'hourly' in data:
                    hourly = data['hourly']
                    times = hourly.get('time', [])
                    temps = hourly.get('temperature_2m', [])
                    
                    for i, hour in enumerate(times):
                        conn.execute('''
                            INSERT INTO weather_hourly
                            (city, hour, temperature, collected_at)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            city,
                            hour,
                            temps[i] if i < len(temps) else None,
                            collected_at
                        ))
            
            conn.commit()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    collector = DataCollector()
    asyncio.run(collector.collect_batch(collector.DEFAULT_CITIES))