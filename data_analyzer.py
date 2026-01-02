import sqlite3
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataAnalyzer:
    
    def __init__(self, db_path: str = 'data/weather_data.db'):
        self.db_path = Path(db_path)
    
    def analyze_temperature_trends(self) -> Dict:
        logger.info("Анализ температурных трендов...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT city, date, temp_max, temp_min
                FROM weather_daily
                ORDER BY city, date
            ''')
            
            trends = {}
            for city, date, max_t, min_t in cursor.fetchall():
                if city not in trends:
                    trends[city] = []
                
                avg_t = (max_t + min_t) / 2 if max_t and min_t else None
                trends[city].append({
                    'date': date,
                    'max': max_t,
                    'min': min_t,
                    'avg': avg_t
                })
        
        return trends
    
    def analyze_precipitation(self) -> Dict:
        logger.info("Анализ осадков...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT city, date, precipitation
                FROM weather_daily
                WHERE precipitation > 0
                ORDER BY city, date
            ''')
            
            precip_data = {}
            for city, date, precip in cursor.fetchall():
                if city not in precip_data:
                    precip_data[city] = {
                        'total': 0,
                        'days': 0,
                        'records': []
                    }
                
                precip_data[city]['total'] += precip
                precip_data[city]['days'] += 1
                precip_data[city]['records'].append({
                    'date': date,
                    'amount': precip
                })
        
        return precip_data
    
    def generate_insights(self) -> List[Dict]:
        logger.info("Генерация аналитических выводов...")
        
        insights = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT city, AVG(temp_max) as avg_max, MIN(temp_min) as min_temp
                FROM weather_daily
                GROUP BY city
            ''')
            
            for city, avg_max, min_temp in cursor.fetchall():
                if avg_max and avg_max > 25:
                    insights.append({
                        'type': 'temperature',
                        'city': city,
                        'severity': 'HIGH',
                        'message': f'Высокая средняя максимальная температура: {avg_max:.1f}°C',
                        'recommendation': 'Подготовить системы охлаждения'
                    })
                
                if min_temp and min_temp < -10:
                    insights.append({
                        'type': 'temperature',
                        'city': city,
                        'severity': 'HIGH',
                        'message': f'Сильные морозы: {min_temp:.1f}°C',
                        'recommendation': 'Обеспечить готовность систем отопления'
                    })
            
            cursor = conn.execute('''
                SELECT city, SUM(precipitation) as total_precip, COUNT(*) as rainy_days
                FROM weather_daily
                WHERE precipitation > 0
                GROUP BY city
            ''')
            
            for city, total_precip, rainy_days in cursor.fetchall():
                if total_precip and total_precip > 50:
                    insights.append({
                        'type': 'precipitation',
                        'city': city,
                        'severity': 'MEDIUM',
                        'message': f'Сильные осадки: {total_precip:.1f}мм за {rainy_days} дней',
                        'recommendation': 'Мониторить риски наводнений'
                    })
            
            cursor = conn.execute('''
                SELECT city, AVG(temp_max) as avg_temp
                FROM weather_daily
                GROUP BY city
            ''')
            
            cities_data = cursor.fetchall()
            if cities_data:
                temps = [t[1] for t in cities_data if t[1]]
                if temps:
                    avg_global = sum(temps) / len(temps)
                    
                    for city, city_temp in cities_data:
                        if city_temp and abs(city_temp - avg_global) > 10:
                            deviation = "теплее" if city_temp > avg_global else "холоднее"
                            insights.append({
                                'type': 'climate_comparison',
                                'city': city,
                                'severity': 'LOW',
                                'message': f'{city} значительно {deviation} среднего',
                                'recommendation': 'Отслеживать сезонные изменения'
                            })
        
        return insights


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = DataAnalyzer()
    temps = analyzer.analyze_temperature_trends()
    precip = analyzer.analyze_precipitation()
    insights = analyzer.generate_insights()
    
    print(f"\nСгенерировано {len(insights)} выводов")
    for insight in insights:
        print(f"  - {insight['city']}: {insight['message']}")