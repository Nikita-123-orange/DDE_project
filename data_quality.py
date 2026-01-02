import sqlite3
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class DataQuality:
    
    def __init__(self, db_path: str = 'data/weather_data.db'):
        self.db_path = Path(db_path)
    
    def check_completeness(self) -> Dict:
        logger.info("Проверка полноты данных...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    city,
                    COUNT(*) as total,
                    COUNT(temperature) as temp_filled,
                    COUNT(humidity) as humid_filled,
                    COUNT(wind_speed) as wind_filled,
                    ROUND(COUNT(temperature)*100.0/COUNT(*), 1) as completeness_percent
                FROM weather_current
                GROUP BY city
            ''')
            
            results = {}
            for row in cursor.fetchall():
                city, total, temp_filled, humid_filled, wind_filled, completeness = row
                results[city] = {
                    'total_records': total,
                    'temperature_filled': temp_filled,
                    'humidity_filled': humid_filled,
                    'wind_filled': wind_filled,
                    'completeness_percent': completeness
                }
                
                status = "OK" if completeness >= 95 else "ВНИМАНИЕ"
                logger.info(f"{status} {city}: {completeness:.1f}% заполнено")
        
        return results
    
    def check_outliers(self) -> Dict:
        logger.info("Поиск аномалий...")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    city,
                    COUNT(*) as records,
                    AVG(temperature) as avg_temp,
                    MIN(temperature) as min_temp,
                    MAX(temperature) as max_temp,
                    (MAX(temperature) - MIN(temperature)) as temp_range
                FROM weather_current
                GROUP BY city
            ''')
            
            anomalies = {}
            for row in cursor.fetchall():
                city, records, avg_temp, min_temp, max_temp, temp_range = row
                
                outliers = []
                
                if temp_range and temp_range > 40:
                    outliers.append({
                        'type': 'extreme_range',
                        'value': temp_range,
                        'message': f'Экстремальный диапазон температур: {temp_range:.1f}°C'
                    })
                
                if min_temp and min_temp < -60:
                    outliers.append({
                        'type': 'extreme_cold',
                        'value': min_temp,
                        'message': f'Нереалистичный холод: {min_temp:.1f}°C'
                    })
                
                if max_temp and max_temp > 60:
                    outliers.append({
                        'type': 'extreme_heat',
                        'value': max_temp,
                        'message': f'Нереалистичная жара: {max_temp:.1f}°C'
                    })
                
                anomalies[city] = {
                    'records': records,
                    'avg_temp': avg_temp,
                    'min_temp': min_temp,
                    'max_temp': max_temp,
                    'range': temp_range,
                    'anomalies': outliers,
                    'has_issues': len(outliers) > 0
                }
                
                if outliers:
                    logger.warning(f"ВНИМАНИЕ {city}: Найдено {len(outliers)} аномалий")
                    for outlier in outliers:
                        logger.warning(f"    - {outlier['message']}")
        
        return anomalies
    
    def check_validity(self) -> Dict:
        logger.info("Проверка корректности данных...")
        
        validity = {
            'temperature': {'min': -50, 'max': 50},
            'humidity': {'min': 0, 'max': 100},
            'wind_speed': {'min': 0, 'max': 50}
        }
        
        with sqlite3.connect(self.db_path) as conn:
            issues = {}
            
            cursor = conn.execute('''
                SELECT city, COUNT(*) as invalid
                FROM weather_current
                WHERE temperature < ? OR temperature > ?
            ''', (validity['temperature']['min'], validity['temperature']['max']))
            
            for city, invalid in cursor.fetchall():
                if city not in issues:
                    issues[city] = []
                if invalid > 0:
                    issues[city].append(f'{invalid} некорректных значений температуры')
            
            cursor = conn.execute('''
                SELECT city, COUNT(*) as invalid
                FROM weather_current
                WHERE humidity < ? OR humidity > ?
            ''', (validity['humidity']['min'], validity['humidity']['max']))
            
            for city, invalid in cursor.fetchall():
                if city not in issues:
                    issues[city] = []
                if invalid > 0:
                    issues[city].append(f'{invalid} некорректных значений влажности')
        
        for city, problems in issues.items():
            logger.warning(f"ВНИМАНИЕ {city}: {', '.join(problems)}")
        
        return {'validity_check': issues if issues else 'Проблемы не найдены'}
    
    def generate_quality_report(self) -> Dict:
        logger.info("\n" + "="*70)
        logger.info("ОТЧЕТ О КАЧЕСТВЕ ДАННЫХ")
        logger.info("="*70)
        
        completeness = self.check_completeness()
        anomalies = self.check_outliers()
        validity = self.check_validity()
        
        completeness_scores = [c['completeness_percent'] for c in completeness.values()]
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0
        
        anomaly_count = sum(len(a['anomalies']) for a in anomalies.values())
        
        quality_score = avg_completeness - (anomaly_count * 2)
        quality_score = max(0, min(100, quality_score))
        
        report = {
            'report_date': datetime.now().isoformat(),
            'completeness': completeness,
            'anomalies': anomalies,
            'validity': validity,
            'quality_score': quality_score,
            'metrics': {
                'avg_completeness': avg_completeness,
                'total_anomalies': anomaly_count,
                'cities_analyzed': len(completeness)
            }
        }
        
        logger.info(f"\nПоказатель качества: {quality_score:.1f}%")
        logger.info(f"Средняя полнота: {avg_completeness:.1f}%")
        logger.info(f"Всего аномалий: {anomaly_count}")
        logger.info("="*70)
        
        return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    quality = DataQuality()
    report = quality.generate_quality_report()
    
    print(f"\nПроверка качества завершена")
    print(f"   Общий показатель: {report['quality_score']:.1f}%")