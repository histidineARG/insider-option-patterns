"""Exclude ETFs, ETNs, and other exchange-traded products from candidate universes.

The committed snapshot in ``data/etp/etp_universe.json`` is the runtime source.
Refresh it with ``python3 etp_exclusion.py --refresh`` when optiondb is available.
That command rebuilds the snapshot from:

- ``optiondb.stock`` rows whose industry is ``Exchange Traded Fund``
- ``optiondb.stock`` rows flagged ``is_etf=1`` whose company name is the ETN
  wrapper ``Barclays PLC`` or ``Credit Suisse AG`` (the common stocks BCS and CS
  are not flagged and stay in the universe)
- names on ``stock``, ``stockbasics``, and ``company`` that match an ETF/ETN
  token, an exchange-traded phrase, or a known product sponsor
- ``optiondb.sectoretf`` symbols
- the maintained symbol list in ``data/event_review_overrides.json``
  (``etf_etn_denylist``), which keeps delisted products such as VXZ
- the NASDAQ Trader symbol directories (``ETF`` column ``Y``, test issues
  skipped), plus the same name rule on those security names. A current
  exchange flag is ignored when ``stock`` already describes that ticker as
  an operating company. That avoids treating a reused ticker as an ETP for
  the years it was an operating company in this database.

A CIK is stored only when every ``cik2symbol`` ticker for that CIK is already
an excluded symbol. A symbol is excluded when its ticker or such a CIK matches.
Closed-end funds stay in the universe unless a rule above identifies them as
exchange-traded products. The bare ticker ``ETF`` is the Aberdeen closed-end
fund and is not excluded by its ticker alone.

``SPY`` is an excluded product when it is a candidate. Scripts that load SPY
only as a market benchmark should keep that query outside this filter.

``--include-etp`` on a script keeps products in that run. The default is to
drop them, including for random and matched draws taken from the same list.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

SNAPSHOT_NAME = 'etp_universe.json'
DENYLIST_KEY = 'etf_etn_denylist'
NASDAQ_URLS = (
    'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt',
    'https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt',
)
WRAPPER_COMPANIES = {'BARCLAYS PLC', 'CREDIT SUISSE AG'}

_TOKEN = re.compile(r'(?i)(?:^|[^A-Za-z])(?:ETF|ETN)(?:[^A-Za-z]|$)')
_PHRASE = re.compile(r'(?i)Exchange[\s-]Traded')
_ISSUER = re.compile(
    r'(?i)ProShares|Direxion|(?:^|[^A-Za-z])iShares(?:[^A-Za-z]|$)|'
    r'\bSPDR\b|(?:^|[^A-Za-z])iPath(?:[^A-Za-z]|$)|VelocityShares|'
    r'UltraPro|Ultra[\s-]?Short|PowerShares|\bBLDRS\b'
)
_SPONSOR_FUND = re.compile(
    r'(?i)(?:(?:Vanguard|Invesco|Schwab|First Trust|WisdomTree|VanEck|Global X|\bARK\b)'
    r'.{0,80}(?:Index Fund|(?:^|[^A-Za-z])(?:ETF|ETN)(?:[^A-Za-z]|$))'
    r'|Invesco QQQ Trust)'
)

_UNIVERSE = None


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def snapshot_path(root: Path | None = None) -> Path:
    if root is not None:
        candidate = Path(root) / 'data' / 'etp' / SNAPSHOT_NAME
        if candidate.exists():
            return candidate
    return repo_root() / 'data' / 'etp' / SNAPSHOT_NAME


def normalize_symbol(symbol) -> str:
    return str(symbol or '').strip().upper()


def normalize_cik(cik) -> str | None:
    digits = ''.join(ch for ch in str(cik or '') if ch.isdigit())
    if not digits:
        return None
    return digits.zfill(10)


def name_is_exchange_product(name: str | None) -> bool:
    """True when a security name reads as an ETF, ETN, or sponsored fund product."""
    text = str(name or '').strip()
    if not text or text.upper() in {'N/A', 'NA', 'NULL'}:
        return False
    return bool(_TOKEN.search(text) or _PHRASE.search(text) or _ISSUER.search(text) or _SPONSOR_FUND.search(text))


class EtpUniverse:
    def __init__(self, payload: dict):
        self.payload = payload
        self.symbols = frozenset(normalize_symbol(s) for s in payload.get('symbols') or [] if normalize_symbol(s))
        self.ciks = frozenset(c for c in (normalize_cik(c) for c in payload.get('ciks') or []) if c)
        self.version = str(payload.get('version') or '')

    def is_symbol(self, symbol) -> bool:
        return normalize_symbol(symbol) in self.symbols

    def is_cik(self, cik) -> bool:
        normalized = normalize_cik(cik)
        return bool(normalized and normalized in self.ciks)

    def is_etp(self, symbol=None, cik=None) -> bool:
        if symbol is not None and self.is_symbol(symbol):
            return True
        return self.is_cik(cik)


def load_universe(root: Path | None = None, refresh: bool = False) -> EtpUniverse:
    """Load the snapshot. Pass ``refresh=True`` to ignore the process cache."""
    global _UNIVERSE
    if _UNIVERSE is not None and not refresh and root is None:
        return _UNIVERSE
    path = snapshot_path(root)
    payload = json.loads(path.read_text())
    universe = EtpUniverse(payload)
    if root is None:
        _UNIVERSE = universe
    return universe


def is_etp(symbol=None, cik=None, root: Path | None = None) -> bool:
    return load_universe(root).is_etp(symbol, cik)


def _stats(universe: EtpUniverse, input_count: int, kept_count: int, removed: list, *, include_etp: bool, kind: str) -> dict:
    return dict(
        excluded=not include_etp,
        kind=kind,
        universe_version=universe.version,
        universe_symbols=len(universe.symbols),
        universe_ciks=len(universe.ciks),
        input=input_count,
        kept=kept_count,
        removed=len(removed),
        removed_sample=removed[:20],
    )


def stats_line(stats: dict) -> str:
    if not stats.get('excluded'):
        return f"ETP exclusion off ({stats.get('universe_version')}): kept {stats.get('kept')} {stats.get('kind')}."
    return (
        f"ETP exclusion {stats.get('universe_version')}: removed {stats.get('removed')} "
        f"of {stats.get('input')} {stats.get('kind')}."
    )


def partition_symbols(symbols, *, include_etp: bool = False, root: Path | None = None):
    """Return ``(kept, stats)``. Kept values keep their original spelling."""
    universe = load_universe(root)
    kept, removed = [], []
    values = list(symbols)
    for raw in values:
        text = str(raw).strip()
        if not text:
            continue
        if include_etp or not universe.is_symbol(text):
            kept.append(text)
        else:
            removed.append(normalize_symbol(text))
    return kept, _stats(universe, len(values), len(kept), removed, include_etp=include_etp, kind='symbols')


def partition_rows(rows, *, symbol_key: str = 'symbol', cik_key: str | None = None,
                   include_etp: bool = False, root: Path | None = None):
    """Return ``(kept_rows, stats)``. A row is removed when its symbol or CIK is an ETP."""
    universe = load_universe(root)
    kept, removed = [], []
    for row in rows:
        symbol = row.get(symbol_key) if isinstance(row, dict) else None
        cik = row.get(cik_key) if cik_key and isinstance(row, dict) else None
        if include_etp or not universe.is_etp(symbol, cik):
            kept.append(row)
        else:
            removed.append(normalize_symbol(symbol) or normalize_cik(cik) or '')
    return kept, _stats(universe, len(rows), len(kept), [item for item in removed if item],
                        include_etp=include_etp, kind='rows')


def read_symbol_file(path, *, include_etp: bool = False, root: Path | None = None):
    symbols = [line.strip() for line in Path(path).read_text().splitlines() if line.strip()]
    return partition_symbols(symbols, include_etp=include_etp, root=root)


def add_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--include-etp',
        action='store_true',
        help='Keep ETFs, ETNs, and other exchange-traded products in this run.',
    )


def _denylist_symbols(root: Path) -> list[str]:
    path = root / 'data' / 'event_review_overrides.json'
    if not path.exists():
        return []
    block = (json.loads(path.read_text()).get(DENYLIST_KEY) or {})
    return [normalize_symbol(s) for s in (block.get('symbols') or []) if normalize_symbol(s)]


def _connect():
    import pymysql
    password = os.environ.get('OPTIONDB_PASSWORD')
    if not password:
        raise RuntimeError('OPTIONDB_PASSWORD is required to refresh the ETP snapshot')
    config = dict(
        user=os.environ.get('OPTIONDB_USER') or 'optiondb',
        password=password,
        database=os.environ.get('OPTIONDB_DATABASE', 'optiondb'),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=120,
        autocommit=True,
    )
    if os.environ.get('OPTIONDB_HOST'):
        config['host'] = os.environ['OPTIONDB_HOST']
        config['port'] = int(os.environ.get('OPTIONDB_PORT', '3306'))
    else:
        config['unix_socket'] = os.environ.get('OPTIONDB_SOCKET', '/run/mysqld/mysqld.sock')
    return pymysql.connect(**config)


def _fetch_nasdaq() -> tuple[set[str], dict]:
    found = set()
    meta = {'urls': list(NASDAQ_URLS), 'files': [], 'downloaded': datetime.now(timezone.utc).isoformat()}
    for url in NASDAQ_URLS:
        request = urllib.request.Request(url, headers={'User-Agent': 'insider-option-patterns etp refresh'})
        with urllib.request.urlopen(request, timeout=60) as response:
            text = response.read().decode('utf-8', errors='replace')
        lines = [line for line in text.splitlines() if line and not line.startswith('File Creation Time')]
        created = next((line for line in text.splitlines() if line.startswith('File Creation Time')), '')
        header = lines[0].split('|')
        indexes = {name.strip(): i for i, name in enumerate(header)}
        symbol_key = 'Symbol' if 'Symbol' in indexes else 'ACT Symbol'
        etf_i = indexes['ETF']
        test_i = indexes.get('Test Issue')
        name_i = indexes.get('Security Name')
        count = 0
        for line in lines[1:]:
            if line.startswith('File Creation Time'):
                continue
            parts = line.split('|')
            if len(parts) <= etf_i:
                continue
            if test_i is not None and test_i < len(parts) and parts[test_i].strip().upper() == 'Y':
                continue
            symbol = normalize_symbol(parts[indexes[symbol_key]] if symbol_key in indexes else parts[0])
            if not symbol:
                continue
            name = parts[name_i] if name_i is not None and name_i < len(parts) else ''
            if parts[etf_i].strip().upper() == 'Y' or name_is_exchange_product(name):
                found.add(symbol)
                count += 1
        meta['files'].append(dict(url=url, rows=len(lines) - 1, flagged=count, file_creation_time=created))
    meta['symbols'] = len(found)
    return found, meta


def refresh_snapshot(root: Path | None = None) -> dict:
    """Rebuild ``data/etp/etp_universe.json`` from optiondb and NASDAQ Trader."""
    root = Path(root or repo_root())
    reasons = {
        'stock_industry': set(),
        'wrapper_etn': set(),
        'name': set(),
        'sectoretf': set(),
        'denylist': set(),
        'nasdaq': set(),
    }
    connection = _connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT symbol, company, industry, is_etf FROM stock')
            stock_rows = cursor.fetchall()
            cursor.execute('SELECT symbol, name FROM stockbasics')
            basics_rows = cursor.fetchall()
            cursor.execute('SELECT symbol, name FROM company')
            company_rows = cursor.fetchall()
            cursor.execute('SELECT symbol FROM sectoretf')
            sector_rows = cursor.fetchall()
            cursor.execute('SELECT symbol, cik FROM cik2symbol')
            cik_rows = cursor.fetchall()
    finally:
        connection.close()

    for row in stock_rows:
        symbol = normalize_symbol(row.get('symbol'))
        if not symbol:
            continue
        industry = (row.get('industry') or '').strip()
        company = row.get('company') or ''
        if industry == 'Exchange Traded Fund':
            reasons['stock_industry'].add(symbol)
        if int(row.get('is_etf') or 0) == 1 and str(company).strip().upper() in WRAPPER_COMPANIES:
            reasons['wrapper_etn'].add(symbol)
        if name_is_exchange_product(company):
            reasons['name'].add(symbol)
    operating = set()
    for row in stock_rows:
        symbol = normalize_symbol(row.get('symbol'))
        if not symbol or symbol in reasons['stock_industry'] or symbol in reasons['wrapper_etn']:
            continue
        if name_is_exchange_product(row.get('company')):
            continue
        industry = (row.get('industry') or '').strip()
        company = str(row.get('company') or '').strip()
        if industry or (company and company.upper() not in {'N/A', 'NA', 'NULL'}):
            operating.add(symbol)
    for row in list(basics_rows) + list(company_rows):
        symbol = normalize_symbol(row.get('symbol'))
        if symbol and name_is_exchange_product(row.get('name')):
            reasons['name'].add(symbol)
    for row in sector_rows:
        symbol = normalize_symbol(row.get('symbol'))
        if symbol:
            reasons['sectoretf'].add(symbol)
    reasons['denylist'].update(_denylist_symbols(root))

    nasdaq_meta = {'symbols': 0, 'error': None}
    try:
        nasdaq, nasdaq_meta = _fetch_nasdaq()
        reasons['nasdaq'].update(nasdaq - operating)
        nasdaq_meta['vetoed_operating_identity'] = len(nasdaq & operating)
    except Exception as exc:  # noqa: BLE001 — snapshot still refreshes from optiondb
        nasdaq_meta = {'symbols': 0, 'error': str(exc)}

    symbols = set().union(*reasons.values())
    by_cik: dict[str, set[str]] = {}
    for row in cik_rows:
        symbol = normalize_symbol(row.get('symbol'))
        cik = normalize_cik(row.get('cik'))
        if symbol and cik:
            by_cik.setdefault(cik, set()).add(symbol)
    ciks = sorted(cik for cik, tickers in by_cik.items() if tickers and tickers <= symbols)
    ordered = sorted(symbols)
    digest = hashlib.sha256('\n'.join(ordered).encode()).hexdigest()
    version = f"{date.today().isoformat()}+{digest[:12]}"
    payload = dict(
        version=version,
        as_of=date.today().isoformat(),
        sha256=digest,
        description=(
            'Symbols and CIKs treated as ETFs, ETNs, or other exchange-traded products. '
            'Closed-end funds are not included unless a name, industry, exchange flag, or denylist entry says they are ETPs. '
            'See data/etp/README.md for the refresh procedure.'
        ),
        counts={key: len(values) for key, values in reasons.items()},
        total_symbols=len(ordered),
        total_ciks=len(ciks),
        nasdaq=nasdaq_meta,
        sources=[
            'optiondb.stock industry = Exchange Traded Fund',
            'optiondb.stock is_etf=1 and company in (Barclays PLC, Credit Suisse AG)',
            'name rule on optiondb.stock.company, stockbasics.name, company.name',
            'optiondb.sectoretf',
            'data/event_review_overrides.json etf_etn_denylist',
            'NASDAQ Trader nasdaqlisted.txt and otherlisted.txt ETF=Y, plus the name rule',
            'optiondb.cik2symbol CIKs whose tickers are all in the symbol set',
        ],
        refresh='python3 etp_exclusion.py --refresh',
        symbols=ordered,
        ciks=ciks,
    )
    path = root / 'data' / 'etp' / SNAPSHOT_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n')
    global _UNIVERSE
    _UNIVERSE = None
    return payload


def _optionstat_symbols(cursor, where_sql: str, params: tuple = ()) -> list[str]:
    cursor.execute(f'SELECT DISTINCT symbol FROM optionstat WHERE {where_sql}', params)
    return [normalize_symbol(row['symbol']) for row in cursor.fetchall() if normalize_symbol(row['symbol'])]


def write_census(root: Path | None = None) -> Path:
    """Count ETP symbols in each saved universe. Does not refit experiments."""
    root = Path(root or repo_root())
    universe = load_universe(root, refresh=True)
    sections = ['# ETP exclusion census', '',
                f"Snapshot `{universe.version}` has {len(universe.symbols)} symbols and {len(universe.ciks)} CIKs.",
                '',
                'Headline metrics in the experiment reports were not refit in this pass when the scan walks thousands of option chains. Counts below are membership counts, not new returns.',
                '']
    list_path = Path('/tmp/anomaly_symbol_list.txt')
    if list_path.exists():
        symbols = [normalize_symbol(line) for line in list_path.read_text().splitlines() if line.strip()]
        removed = [symbol for symbol in symbols if universe.is_symbol(symbol)]
        sections += [
            '## Anomaly symbol list',
            '',
            f"`/tmp/anomaly_symbol_list.txt` has {len(symbols)} symbols, of which {len(removed)} are exchange-traded products.",
            'anomaly_flow, straddle_test, bracket_test, jump30_test, and gb30_trade_test read this file.',
            '',
        ]
    try:
        connection = _connect()
    except Exception as exc:  # noqa: BLE001
        sections += ['## optiondb', '', f'Not queried: {exc}', '']
        connection = None
    if connection is not None:
        queries = [
            ('direction_test optionstat 2014-01-01..2026-11-13',
             "symbol <> '' AND qdate BETWEEN '2014-01-01' AND '2026-11-13'"),
            ('quiet_screen / walkforward optionstat 2022-01-01..2026-11-12',
             "qdate BETWEEN '2022-01-01' AND '2026-11-12'"),
            ('all optionstat symbols', "symbol <> ''"),
        ]
        sections += ['## optionstat universes', '', '| Query | Symbols | ETP symbols |', '| --- | ---: | ---: |']
        try:
            with connection.cursor() as cursor:
                for label, where in queries:
                    symbols = _optionstat_symbols(cursor, where)
                    removed = sum(1 for symbol in symbols if universe.is_symbol(symbol))
                    sections.append(f'| {label} | {len(symbols)} | {removed} |')
        finally:
            connection.close()
        sections.append('')
    out = root / 'results' / 'etp_exclusion' / 'CENSUS.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(sections) + '\n')
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh', action='store_true', help='Rebuild data/etp/etp_universe.json')
    parser.add_argument('--census', action='store_true', help='Write results/etp_exclusion/CENSUS.md')
    args = parser.parse_args(argv)
    if args.refresh:
        payload = refresh_snapshot()
        print(f"wrote {payload['total_symbols']} symbols {payload['total_ciks']} ciks version {payload['version']}")
        print(json.dumps(payload['counts'], indent=2))
        if payload['nasdaq'].get('error'):
            print(f"nasdaq unavailable: {payload['nasdaq']['error']}")
    if args.census or not args.refresh:
        if not args.refresh and not args.census:
            parser.print_help()
            return 0
        if args.census:
            path = write_census()
            print(path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
