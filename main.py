import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import json

from data_collector import DataCollector
from data_analyzer import DataAnalyzer
from data_quality import DataQuality
from data_visualizer import DataVisualizer


def setup_directories():
    for directory in ['data', 'logs', 'results']:
        Path(directory).mkdir(exist_ok=True)


def setup_logging():
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/weather_platform.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


async def run_collection(args, logger):
    logger.info("\n" + "="*70)
    logger.info("[ЭТАП 1] СБОР ДАННЫХ")
    logger.info("="*70)
    
    collector = DataCollector(forecast_days=args.days)
    
    cities = collector.DEFAULT_CITIES
    if args.cities:
        cities = [c for c in collector.DEFAULT_CITIES 
                 if any(name.lower() in c['name'].lower() for name in args.cities)]
        if not cities:
            cities = collector.DEFAULT_CITIES
    
    collected_data = await collector.collect_batch(cities)
    logger.info(f"Собрано {len(collected_data)} городов")
    
    return collected_data


def run_analysis(collector_obj, logger):
    logger.info("\n" + "="*70)
    logger.info("[ЭТАП 2] АНАЛИЗ ДАННЫХ")
    logger.info("="*70)
    
    analyzer = DataAnalyzer('data/weather_data.db')
    
    logger.info("\nАнализ температурных трендов...")
    temp_analysis = analyzer.analyze_temperature_trends()
    
    logger.info("Анализ осадков...")
    precip_analysis = analyzer.analyze_precipitation()
    
    logger.info("Генерация аналитических выводов...")
    insights = analyzer.generate_insights()
    
    report = {
        'report_date': datetime.now().isoformat(),
        'temperature_analysis': temp_analysis,
        'precipitation_analysis': precip_analysis,
        'insights': insights
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    analytics_file = results_dir / f"analytics_{timestamp}.json"
    with open(analytics_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"Аналитика сохранена: {analytics_file}")
    
    return report


def run_quality_check(logger):
    logger.info("\n" + "="*70)
    logger.info("[ЭТАП 3] ПРОВЕРКА КАЧЕСТВА ДАННЫХ")
    logger.info("="*70)
    
    quality = DataQuality('data/weather_data.db')
    
    logger.info("\nПроверка полноты данных...")
    completeness = quality.check_completeness()
    
    logger.info("Поиск аномалий...")
    anomalies = quality.check_outliers()
    
    quality_report = quality.generate_quality_report()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path('results')
    quality_file = results_dir / f"quality_report_{timestamp}.json"
    
    with open(quality_file, 'w', encoding='utf-8') as f:
        json.dump(quality_report, f, ensure_ascii=False, indent=2, default=str)
    
    logger.info(f"Показатель качества: {quality_report['quality_score']:.1f}%")
    logger.info(f"Отчет о качестве сохранен: {quality_file}")
    
    return quality_report


def run_visualization(logger):
    logger.info("\n" + "="*70)
    logger.info("[ЭТАП 4] ВИЗУАЛИЗАЦИЯ")
    logger.info("="*70)
    
    visualizer = DataVisualizer('data/weather_data.db')
    
    logger.info("\nСоздание дашборда...")
    html_file = visualizer.generate_html_dashboard()
    logger.info(f"Дашборд: {html_file}")
    
    logger.info("Создание текстового отчета...")
    text_file = visualizer.generate_text_report()
    logger.info(f"Текстовый отчет: {text_file}")
    
    return {'html': html_file, 'text': text_file}


def main():
    parser = argparse.ArgumentParser(description='Платформа аналитики погодных данных')
    parser.add_argument('--days', type=int, default=10, help='Дни прогноза (1-16)')
    parser.add_argument('--cities', nargs='+', help='Конкретные города')
    parser.add_argument('--collect', action='store_true', help='Только сбор данных')
    parser.add_argument('--analyze', action='store_true', help='Только анализ данных')
    parser.add_argument('--quality', action='store_true', help='Только проверка качества')
    parser.add_argument('--visualize', action='store_true', help='Только визуализация')
    parser.add_argument('--all', action='store_true', help='Выполнить все этапы (по умолчанию)')
    
    args = parser.parse_args()
    
    setup_directories()
    logger = setup_logging()
    
    logger.info("\n" + "="*70)
    logger.info(" ПЛАТФОРМА АНАЛИТИКИ ПОГОДНЫХ ДАННЫХ ".center(70))
    logger.info("="*70)
    
    try:
        run_all = args.all or (not args.collect and not args.analyze and 
                               not args.quality and not args.visualize)
        
        collector_obj = None
        analysis_report = None
        quality_report = None
        viz_files = None
        
        if run_all or args.collect:
            collector_obj = asyncio.run(run_collection(args, logger))
        
        if run_all or args.analyze:
            if collector_obj is None:
                collector_obj = {}
            analysis_report = run_analysis(collector_obj, logger)
        
        if run_all or args.quality:
            quality_report = run_quality_check(logger)
        
        if run_all or args.visualize:
            viz_files = run_visualization(logger)
        
        logger.info("\n" + "="*70)
        logger.info(" ВСЕ ЭТАПЫ УСПЕШНО ЗАВЕРШЕНЫ ".center(70))
        logger.info("="*70)
        
        if analysis_report:
            logger.info(f"\nСгенерировано выводов: {len(analysis_report.get('insights', []))}")
        
        if quality_report:
            logger.info(f"Качество данных: {quality_report.get('quality_score', 0):.1f}%")
        
        if viz_files:
            logger.info(f"\nРезультаты сохранены в: results/")
        
        logger.info("\n" + "="*70 + "\n")
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("\nПрервано пользователем")
        return 130
    except Exception as e:
        logger.error(f"Ошибка: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())