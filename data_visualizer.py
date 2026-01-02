
import json
import sqlite3
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class DataVisualizer:
    
    def __init__(self, db_path: str = 'data/weather_data.db'):
        self.db_path = Path(db_path)
    
    def generate_html_dashboard(self) -> str:
        logger.info("Создание графиков температуры...")
        
        try:
            from chart_generator import TemperatureChartGenerator
            
            generator = TemperatureChartGenerator(str(self.db_path))
            
            hourly_charts = generator.generate_hourly_charts()
            daily_charts = generator.generate_daily_charts()
            
            if hourly_charts or daily_charts:
                logger.info(f"Создано {len(hourly_charts)} часовых графиков температуры")
                logger.info(f"Создано {len(daily_charts)} дневных графиков температуры")
                return hourly_charts[0] if hourly_charts else daily_charts[0]
            else:
                logger.warning("Нет данных для создания графиков")
                return ""
        
        except ImportError:
            logger.error("matplotlib не установлен. Выполните: pip install matplotlib")
            return ""
        except Exception as e:
            logger.error(f"Ошибка создания графиков: {e}")
            return ""
    
    def generate_text_report(self) -> str:
        logger.info("Создание текстового отчета...")
        
        stats = self._get_stats()
        
        report = "="*70 + "\n"
        report += "АНАЛИТИКА ПОГОДНЫХ ДАННЫХ - ТЕКСТОВЫЙ ОТЧЕТ\n"
        report += "="*70 + "\n\n"
        report += f"Создано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += "СТАТИСТИКА ПО ГОРОДАМ:\n"
        report += "-"*70 + "\n"
        report += f"{'Город':<20} {'Ср. темп.':<12} {'Макс.':<10} {'Мин.':<10} {'Записей':<10}\n"
        report += "-"*70 + "\n"
        
        for stat in stats:
            city = stat['city'][:19]
            avg_t = f"{stat['avg_temp']:.1f}°C" if stat['avg_temp'] else "Н/Д"
            max_t = f"{stat['max_temp']:.1f}°C" if stat['max_temp'] else "Н/Д"
            min_t = f"{stat['min_temp']:.1f}°C" if stat['min_temp'] else "Н/Д"
            
            report += f"{city:<20} {avg_t:<12} {max_t:<10} {min_t:<10} {stat['records']:<10}\n"
        
        report += "\n" + "="*70 + "\n"
        
        Path('results').mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"results/report_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Текстовый отчет: {output_file}")
        return output_file
    
    def _get_stats(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT 
                    city,
                    COUNT(*) as records,
                    AVG(temperature) as avg_temp,
                    MAX(temperature) as max_temp,
                    MIN(temperature) as min_temp
                FROM weather_current
                GROUP BY city
                ORDER BY avg_temp DESC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _get_temperature_data(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT city, date, temp_max, temp_min
                FROM weather_daily
                ORDER BY city, date
            ''')
            
            data = {}
            for city, date, max_t, min_t in cursor.fetchall():
                if city not in data:
                    data[city] = []
                data[city].append({
                    'date': date,
                    'max': max_t,
                    'min': min_t,
                    'avg': (max_t + min_t) / 2 if max_t and min_t else None
                })
            
            return data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    visualizer = DataVisualizer()
    visualizer.generate_html_dashboard()
    visualizer.generate_text_report()