# BigQuery Domain Analysis - Quick Start

This project contains an automated data pipeline script that extracts domain performance data from BigQuery and generates day-over-day analysis reports.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Configure credentials:**
   - Place your credentials file `iab-5d3c53b40c41.json` in your home directory:
     ```bash
     # The file should be at: /Users/geoffcohen/iab-5d3c53b40c41.json
     # If it's elsewhere, move it to your home directory:
     mv /path/to/iab-5d3c53b40c41.json ~/iab-5d3c53b40c41.json
     chmod 600 ~/iab-5d3c53b40c41.json
     ```

3. **Test the script:**
   ```bash
   ./bigquery_domain_analysis.py
   ```

4. **Set up automated execution:**
   ```bash
   crontab -e
   ```
   Add this line for daily 8 AM execution:
   ```cron
   0 8 * * * /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1
   ```

## What It Does

- Connects to BigQuery (`iab-publisher-data.dap_daily.dap_domain`)
- Extracts data for the two most recent dates
- Aggregates metrics by domain (across all platforms)
- Calculates day-over-day changes for active users and pageviews
- Generates formatted reports (TXT and CSV)
- Maintains 30-day file retention
- Logs all operations for monitoring

## Output

Reports are saved to `~/Downloads/domain_reports/`:

- **TXT files**: Human-readable formatted tables
- **CSV files**: Machine-readable data for analysis
- **Logs**: Execution logs in `logs/` subdirectory

## Files

- `bigquery_domain_analysis.py` - Main script
- `requirements.txt` - Python dependencies
- `SETUP.md` - Detailed setup and troubleshooting guide
- `env.example` - Optional environment configuration

## Requirements

- Python 3.7+
- BigQuery service account with read access
- macOS with cron support

## Documentation

See [SETUP.md](SETUP.md) for:
- Detailed installation instructions
- Service account configuration
- Cron setup examples
- Troubleshooting guide
- Monitoring tips

## Example Cron Schedules

```cron
# Daily at 8:00 AM
0 8 * * * /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1

# Weekdays at 7:30 AM
30 7 * * 1-5 /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1

# Twice daily (8 AM and 6 PM)
0 8,18 * * * /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1
```

## Monitoring

Check recent execution:
```bash
# View latest log
tail -50 ~/Downloads/domain_reports/logs/cron_log_$(date +%Y-%m).log

# List recent reports
ls -lt ~/Downloads/domain_reports/domain_analysis_*.txt | head -5
```

## Support

For issues, check:
1. Log files in `~/Downloads/domain_reports/logs/`
2. Credentials file path and permissions
3. BigQuery service account permissions
4. [SETUP.md](SETUP.md) troubleshooting section
