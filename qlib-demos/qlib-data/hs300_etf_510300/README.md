# HS300 ETF Qlib-ready data

Source: AkShare `fund_etf_hist_em`

- ETF symbol: `510300`
- Qlib instrument: `SH510300`
- Rows: `2800`
- Date range: `2015-01-05` to `2026-07-14`
- Normalized CSV: `/Users/neil/python-project/langgraph-finance-roadmap/qlib-demos/qlib-data/hs300_etf_510300/csv/SH510300.csv`

Convert to Qlib bin format from a Qlib checkout:

```bash
python scripts/dump_bin.py dump_all --data_path /Users/neil/python-project/langgraph-finance-roadmap/qlib-demos/qlib-data/hs300_etf_510300/csv --qlib_dir /Users/neil/python-project/langgraph-finance-roadmap/qlib-demos/qlib-data/hs300_etf_510300/qlib_bin --include_fields open,high,low,close,volume,amount,factor --symbol_field_name symbol --date_field_name date --file_suffix .csv
```

Then use:

```bash
export QLIB_PROVIDER_URI=/Users/neil/python-project/langgraph-finance-roadmap/qlib-demos/qlib-data/hs300_etf_510300/qlib_bin
```
