import sqlite3
import logging
from pathlib import Path
from typing import Dict, List
import json

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

logger = logging.getLogger(__name__)


class TemperatureChartGenerator:
    
    def __init__(self, db_path: str = 'data/weather_data.db'):
        self.db_path = Path(db_path)
    
    def generate_hourly_charts(self) -> List[str]:
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlib не установлен. Выполните: pip install matplotlib")
            return []
        
        logger.info("Генерация часовых графиков температуры...")
        
        hourly_data = self._get_hourly_data()
        if not hourly_data:
            logger.warning("Часовые данные не найдены")
            return []
        
        Path('results').mkdir(exist_ok=True)
        generated_files = []
        
        for city, data in hourly_data.items():
            try:
                chart_file = self._create_hourly_chart(city, data)
                generated_files.append(chart_file)
                logger.info(f"{city}: {chart_file}")
            except Exception as e:
                logger.error(f"Ошибка создания графика для {city}: {e}")
        
        return generated_files
    
    def generate_daily_charts(self) -> List[str]:
        if not MATPLOTLIB_AVAILABLE:
            logger.error("matplotlib не установлен. Выполните: pip install matplotlib")
            return []
        
        logger.info("Генерация дневных графиков температуры...")
        
        daily_data = self._get_daily_data()
        if not daily_data:
            logger.warning("Дневные данные не найдены")
            return []
        
        Path('results').mkdir(exist_ok=True)
        generated_files = []
        
        for city, data in daily_data.items():
            try:
                chart_file = self._create_daily_chart(city, data)
                generated_files.append(chart_file)
                logger.info(f"{city}: {chart_file}")
            except Exception as e:
                logger.error(f"Ошибка создания дневного графика для {city}: {e}")
        
        return generated_files
    
    def _get_hourly_data(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT city, hour, temperature
                FROM weather_hourly
                ORDER BY city, hour
            ''')
            
            data = {}
            for city, hour, temp in cursor.fetchall():
                if city not in data:
                    data[city] = {'hours': [], 'temps': []}
                
                data[city]['hours'].append(hour)
                data[city]['temps'].append(temp)
            
            return data
    
    def _get_daily_data(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT city, date, temp_max, temp_min, (temp_max + temp_min) / 2 as temp_avg
                FROM weather_daily
                ORDER BY city, date
            ''')
            
            data = {}
            for city, date, temp_max, temp_min, temp_avg in cursor.fetchall():
                if city not in data:
                    data[city] = {'dates': [], 'max': [], 'min': [], 'avg': []}
                
                data[city]['dates'].append(date)
                data[city]['max'].append(temp_max)
                data[city]['min'].append(temp_min)
                data[city]['avg'].append(temp_avg)
            
            return data
    
    def _create_hourly_chart(self, city: str, data: Dict) -> str:
        fig, ax = plt.subplots(figsize=(16, 7))
        
        hours = data['hours']
        temps = data['temps']
        
        ax.plot(hours, temps, linewidth=2, color='#3498db', marker='o', markersize=4)
        ax.fill_between(range(len(temps)), temps, alpha=0.3, color='#3498db')
        
        ax.set_title(f'Изменение температуры по часам - {city}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Время (час)', fontsize=12)
        ax.set_ylabel('Температура (°C)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        step = max(1, len(hours) // 12)
        ax.set_xticks(range(0, len(hours), step))
        ax.set_xticklabels([hours[i] for i in range(0, len(hours), step)], rotation=45, ha='right')
        
        min_temp = min(temps)
        max_temp = max(temps)
        min_idx = temps.index(min_temp)
        max_idx = temps.index(max_temp)
        
        ax.annotate(f'Мин: {min_temp:.1f}°C', 
                   xy=(min_idx, min_temp), 
                   xytext=(10, -20),
                   textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='#e74c3c', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', color='#e74c3c'))
        
        ax.annotate(f'Макс: {max_temp:.1f}°C', 
                   xy=(max_idx, max_temp), 
                   xytext=(10, 20),
                   textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='#2ecc71', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', color='#2ecc71'))
        
        plt.tight_layout()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/hourly_{city.replace(' ', '_')}_{timestamp}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename
    
    def _create_daily_chart(self, city: str, data: Dict) -> str:
        fig, ax = plt.subplots(figsize=(16, 7))
        
        dates = data['dates']
        max_temps = data['max']
        min_temps = data['min']
        avg_temps = data['avg']
        
        x = range(len(dates))
        
        ax.plot(x, max_temps, linewidth=2, color='#e74c3c', marker='o', label='Макс', markersize=5)
        ax.plot(x, min_temps, linewidth=2, color='#3498db', marker='o', label='Мин', markersize=5)
        ax.plot(x, avg_temps, linewidth=2, color='#2ecc71', marker='s', label='Сред', markersize=5)
        
        ax.fill_between(x, min_temps, max_temps, alpha=0.2, color='#95a5a6')
        
        ax.set_title(f'Дневные температурные тренды - {city}', fontsize=16, fontweight='bold')
        ax.set_xlabel('Дата', fontsize=12)
        ax.set_ylabel('Температура (°C)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=11)
        
        step = max(1, len(x) // 8)
        ax.set_xticks(x[::step])
        ax.set_xticklabels([dates[i] for i in x[::step]], rotation=45, ha='right')
        
        plt.tight_layout()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/daily_{city.replace(' ', '_')}_{timestamp}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        return filename


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    generator = TemperatureChartGenerator()
    
    print("\n" + "="*70)
    print(" ГЕНЕРАТОР ТЕМПЕРАТУРНЫХ ГРАФИКОВ ".center(70))
    print("="*70 + "\n")
    
    hourly_files = generator.generate_hourly_charts()
    daily_files = generator.generate_daily_charts()
    
    print("\n" + "="*70)
    print(f"Сгенерировано {len(hourly_files)} часовых графиков")
    print(f"Сгенерировано {len(daily_files)} дневных графиков")
    print("="*70 + "\n")
    
    if hourly_files or daily_files:
        print("Графики сохранены в папке results/:")
        for f in hourly_files + daily_files:
            print(f"   - {f}")
    else:
        print("Графики не сгенерированы. Сначала выполните 'python main.py --collect'")
    
    print("\n")