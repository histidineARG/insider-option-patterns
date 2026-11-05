"""Read-only, daily OTM call volume anomaly screening."""
import argparse
import csv
from dataclasses import asdict, dataclass
from datetime import date, timedelta
import getpass
import json
import os
import statistics
import sys


@dataclass(frozen=True)
class Settings:
    lookback: int = 20
    min_history: int = 10
    min_volume: int = 500
    min_ratio: float = 5.0
    min_zscore: float = 3.0
    min_volume_oi: float = 1.0
    min_otm: float = 0.03
    max_otm: float = 0.50
    min_dte: int = 3
    max_dte: int = 45


def score(days, target, settings):
    """Days must include every observed chain session, including zero OTM volume."""
    current = next((r for r in days if r['qdate'] == target), None)
    history = sorted((r for r in days if r['qdate'] < target),
                     key=lambda r: r['qdate'])[-settings.lookback:]
    if current is None or len(history) < settings.min_history:
        return None
    volumes = [float(r['volume']) for r in history]
    mean = statistics.mean(volumes)
    std = statistics.pstdev(volumes)
    volume = int(current['volume'])
    oi = int(current['oi'])
    ratio = volume / mean if mean else None
    zscore = (volume - mean) / std if std else None
    volume_oi = volume / oi if oi else None
    # Zero baselines and zero OI are explicit states, never infinite JSON numbers.
    surge = volume > 0 if mean == 0 else ratio >= settings.min_ratio
    unusual = volume > mean if std == 0 else zscore >= settings.min_zscore
    oi_pass = volume > 0 if oi == 0 else volume_oi >= settings.min_volume_oi
    if not (volume >= settings.min_volume and surge and unusual and oi_pass):
        return None
    return dict(date=target.isoformat(), volume=volume, open_interest=oi,
                baseline_sessions=len(history), baseline_mean=round(mean, 4),
                baseline_std=round(std, 4), volume_ratio=ratio, zscore=zscore,
                volume_oi=volume_oi, zero_baseline=mean == 0, zero_oi=oi == 0,
                estimated_premium=float(current['premium']))


def load_days(connection, symbol, target, settings, table='optiondaily'):
    if table not in ('optiondaily', 'optiondaily3'):
        raise ValueError('Unsupported table')
    # Leading underlying column matches the existing composite index.
    # CASE retains observed sessions with no qualifying OTM calls as zero days.
    sql = f'''SELECT qdate,
        SUM(CASE WHEN eligible THEN volume ELSE 0 END) AS volume,
        SUM(CASE WHEN eligible THEN oi ELSE 0 END) AS oi,
        SUM(CASE WHEN eligible AND bid >= 0 AND ask >= bid
                 THEN volume * (bid + ask) / 2 * 100 ELSE 0 END) AS premium
      FROM (
        SELECT qdate, volume, oi, bid, ask,
          (`type` = 'call' AND underlying_last > 0
           AND strike > underlying_last
           AND strike >= underlying_last * %s
           AND strike <= underlying_last * %s
           AND DATEDIFF(edate, qdate) BETWEEN %s AND %s
           AND volume >= 0 AND oi >= 0) AS eligible
        FROM `{table}` WHERE underlying = %s AND qdate BETWEEN %s AND %s
      ) AS contracts GROUP BY qdate ORDER BY qdate'''
    start = target - timedelta(days=max(90, settings.lookback * 4))
    with connection.cursor() as cursor:
        cursor.execute(sql, (1 + settings.min_otm, 1 + settings.max_otm,
                            settings.min_dte, settings.max_dte, symbol, start, target))
        return cursor.fetchall()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--symbols', nargs='+', required=True)
    parser.add_argument('--date', type=date.fromisoformat, required=True)
    parser.add_argument('--table', choices=['optiondaily', 'optiondaily3'], default='optiondaily')
    parser.add_argument('--format', choices=['json', 'csv'], default='json')
    for name, field in Settings.__dataclass_fields__.items():
        parser.add_argument('--' + name.replace('_', '-'), type=field.type, default=field.default)
    args = parser.parse_args()
    settings = Settings(**{name: getattr(args, name) for name in Settings.__dataclass_fields__})
    if not (1 <= settings.min_history <= settings.lookback and
            0 <= settings.min_otm <= settings.max_otm and
            0 <= settings.min_dte <= settings.max_dte and
            settings.min_volume > 0 and settings.min_ratio > 0 and
            settings.min_zscore >= 0 and settings.min_volume_oi >= 0):
        parser.error('Invalid history, threshold, OTM, or expiration settings')
    import pymysql
    password = os.environ.get('OPTIONDB_PASSWORD')
    if password is None:
        password = getpass.getpass('MySQL password: ')
    config = dict(user=os.environ.get('OPTIONDB_USER', 'bill'), password=password,
                  database=os.environ.get('OPTIONDB_DATABASE', 'optiondb'),
                  cursorclass=pymysql.cursors.DictCursor, connect_timeout=5,
                  read_timeout=60, write_timeout=5, autocommit=False)
    if os.environ.get('OPTIONDB_HOST'):
        config['host'] = os.environ['OPTIONDB_HOST']
        config['port'] = int(os.environ.get('OPTIONDB_PORT', '3306'))
    else:
        config['unix_socket'] = os.environ.get('OPTIONDB_SOCKET', '/run/mysqld/mysqld.sock')
    alerts = []
    try:
        with pymysql.connect(**config) as connection:
            with connection.cursor() as cursor:
                cursor.execute('SET SESSION MAX_EXECUTION_TIME=60000')
                cursor.execute('START TRANSACTION READ ONLY')
            for symbol in dict.fromkeys(s.upper() for s in args.symbols):
                days = load_days(connection, symbol, args.date, settings, args.table)
                if not any(r['qdate'] == args.date for r in days):
                    print(f'{symbol}: no chain data on {args.date}', file=sys.stderr)
                elif sum(r['qdate'] < args.date for r in days) < settings.min_history:
                    print(f'{symbol}: insufficient historical sessions', file=sys.stderr)
                alert = score(days, args.date, settings)
                if alert:
                    alerts.append(dict(symbol=symbol, **alert))
            connection.rollback()
    except pymysql.MySQLError as error:
        print(f'Database error: {error}', file=sys.stderr)
        return 1
    alerts.sort(key=lambda r: (r['volume_ratio'] is None, r['volume_ratio'] or 0, r['volume']), reverse=True)
    if args.format == 'json':
        print(json.dumps(dict(settings=asdict(settings), alerts=alerts), indent=2, allow_nan=False))
    else:
        fields = ['symbol', 'date', 'volume', 'open_interest', 'baseline_sessions',
                  'baseline_mean', 'baseline_std', 'volume_ratio', 'zscore',
                  'volume_oi', 'zero_baseline', 'zero_oi', 'estimated_premium']
        writer = csv.DictWriter(sys.stdout, fieldnames=fields)
        writer.writeheader()
        writer.writerows(alerts)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
