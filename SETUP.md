# BigQuery Domain Analysis - Setup Guide

This guide will help you set up and configure the BigQuery domain analysis script for automated cron execution on macOS.

## Prerequisites

- Python 3.7 or higher
- BigQuery service account with read access to `iab-publisher-data.dap_daily.dap_domain`
- macOS with cron support

## Installation Steps

### 1. Install Python Dependencies

```bash
cd /Users/geoffcohen/antig1
pip3 install -r requirements.txt
```

This will install:
- `google-cloud-bigquery` - BigQuery Python client
- `pandas` - Data manipulation library
- `db-dtypes` - BigQuery data type support

### 2. Set Up Service Account Credentials

#### Option A: Download from Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Select your service account (or create a new one)
4. Click **Keys** → **Add Key** → **Create New Key**
5. Choose **JSON** format and download

#### Option B: Use Existing Credentials

If you already have a service account JSON file, simply note its location.

#### Configure Credentials Path

Your credentials file `iab-5d3c53b40c41.json` should be placed in your home directory:

```bash
# Move your credentials file to home directory
mv /path/to/iab-5d3c53b40c41.json ~/iab-5d3c53b40c41.json

# Set secure permissions (user read/write only)
chmod 600 ~/iab-5d3c53b40c41.json

# Verify the file is in the correct location
ls -la ~/iab-5d3c53b40c41.json
```

The script is already configured to use this file at:
```python
CREDENTIALS_PATH = os.path.expanduser("~/iab-5d3c53b40c41.json")
```

**Final path should be:** `/Users/geoffcohen/iab-5d3c53b40c41.json`

> **Security Note:** The `chmod 600` command ensures only you can read/write the credentials file, which is a security best practice for sensitive credentials.

### 3. Make Script Executable

```bash
chmod +x /Users/geoffcohen/antig1/bigquery_domain_analysis.py
```

### 4. Test Manual Execution

Run the script manually to verify everything works:

```bash
cd /Users/geoffcohen/antig1
./bigquery_domain_analysis.py
```

Or:

```bash
python3 /Users/geoffcohen/antig1/bigquery_domain_analysis.py
```

**Expected output:**
- Script should connect to BigQuery
- Extract data for the two most recent dates
- Generate reports in `~/Downloads/domain_reports/`
- Create log file in `~/Downloads/domain_reports/logs/`

**Check the output:**
```bash
ls -la ~/Downloads/domain_reports/
cat ~/Downloads/domain_reports/domain_analysis_*.txt
```

### 5. Set Up Cron Job

#### Edit Crontab

```bash
crontab -e
```

#### Add Cron Entry

**Example 1: Run daily at 8:00 AM**
```cron
0 8 * * * /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1
```

**Example 2: Run daily at 6:00 AM (before business hours)**
```cron
0 6 * * * /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1
```

**Example 3: Run every weekday at 7:30 AM**
```cron
30 7 * * 1-5 /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1
```

**Example 4: Run twice daily (8 AM and 6 PM)**
```cron
0 8,18 * * * /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1
```

#### Cron Syntax Reference

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, Sunday = 0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

#### Verify Cron Entry

```bash
crontab -l
```

## Directory Structure

After setup, your directory structure will look like:

```
/Users/geoffcohen/antig1/
├── bigquery_domain_analysis.py    # Main script
├── requirements.txt                # Python dependencies
└── SETUP.md                        # This file

~/Downloads/domain_reports/
├── domain_analysis_2025-11-20_080001.txt
├── domain_analysis_2025-11-20_080001.csv
├── domain_analysis_2025-11-21_080001.txt
├── domain_analysis_2025-11-21_080001.csv
└── logs/
    ├── cron_log_2025-11.log       # Monthly log file
    └── cron_stdout.log            # Cron stdout/stderr
```

## Output Files

### TXT Report (`domain_analysis_YYYY-MM-DD_HHMMSS.txt`)

Human-readable formatted report with:
- Execution timestamp and data date range
- Table 1: Top 10 domains by active users change
- Table 2: Top 10 domains by pageviews change
- Summary statistics (gainers/decliners counts)

### CSV Report (`domain_analysis_YYYY-MM-DD_HHMMSS.csv`)

Machine-readable data file with columns:
- `domain_name`
- `prev_users`, `latest_users`, `users_change`, `users_pct_change`
- `prev_views`, `latest_views`, `views_change`, `views_pct_change`
- `report_date`, `previous_date`, `latest_date`

### Log Files

- **Monthly logs**: `logs/cron_log_YYYY-MM.log` - Detailed execution logs
- **Cron output**: `logs/cron_stdout.log` - Cron stdout/stderr capture

## File Retention

The script automatically maintains a **30-day retention policy**:
- Reports older than 30 days are automatically deleted
- Log files are rotated monthly
- No manual cleanup required

## Troubleshooting

### Script Doesn't Run in Cron

**Problem:** Script works manually but fails in cron.

**Solutions:**
1. Use absolute paths in crontab entry
2. Check cron has permission to run scripts (macOS Catalina+):
   - System Preferences → Security & Privacy → Privacy → Full Disk Access
   - Add `/usr/sbin/cron` to the list

### Authentication Errors

**Problem:** `Credentials file not found` or authentication failures.

**Solutions:**
1. Verify credentials file path is correct and absolute
2. Check file permissions: `chmod 600 ~/bigquery_credentials.json`
3. Verify service account has BigQuery read permissions
4. Test credentials manually: `gcloud auth activate-service-account --key-file=~/bigquery_credentials.json`

### No Output Files Generated

**Problem:** Script runs but no reports appear.

**Solutions:**
1. Check logs: `cat ~/Downloads/domain_reports/logs/cron_log_*.log`
2. Verify output directory permissions
3. Check for errors in cron output: `cat ~/Downloads/domain_reports/logs/cron_stdout.log`

### Insufficient Data Error

**Problem:** Script reports "Insufficient data: Found X dates, need at least 2".

**Solutions:**
1. Verify BigQuery table has data for at least 2 different dates
2. Check table name and dataset are correct
3. Verify service account has read access to the table

### Cron Not Running

**Problem:** Cron job doesn't execute at scheduled time.

**Solutions:**
1. Verify cron service is running: `sudo launchctl list | grep cron`
2. Check system logs: `log show --predicate 'process == "cron"' --last 1h`
3. Verify crontab syntax: `crontab -l`
4. Test with a simple cron job first:
   ```cron
   * * * * * date >> ~/cron_test.log
   ```

## Monitoring

### Check Recent Execution

```bash
# View latest log entries
tail -50 ~/Downloads/domain_reports/logs/cron_log_$(date +%Y-%m).log

# List recent reports
ls -lt ~/Downloads/domain_reports/domain_analysis_*.txt | head -5

# View latest report
cat ~/Downloads/domain_reports/domain_analysis_*.txt | tail -1
```

### Email Notifications (Optional)

To receive email notifications on cron failures, set `MAILTO` in crontab:

```cron
MAILTO=your.email@example.com
0 8 * * * /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1
```

## Advanced Configuration

### Custom Output Directory

Edit the script and change line 46:
```python
BASE_OUTPUT_DIR = Path.home() / "Downloads" / "domain_reports"
```

### Custom Retention Period

Edit the script and change line 47:
```python
RETENTION_DAYS = 30  # Change to desired number of days
```

### Different BigQuery Table

Edit the script and change lines 35-37:
```python
PROJECT_ID = "iab-publisher-data"
DATASET_ID = "dap_daily"
TABLE_ID = "dap_domain"
```

## Support

For issues or questions:
1. Check the log files first
2. Verify all prerequisites are met
3. Test manual execution before debugging cron
4. Review BigQuery quotas and limits

## Security Best Practices

1. **Credentials**: Never commit credentials to version control
2. **Permissions**: Use minimal required permissions for service account
3. **File Access**: Restrict credentials file to user-only access (`chmod 600`)
4. **Logs**: Regularly review logs for unauthorized access attempts
5. **Rotation**: Periodically rotate service account keys

## Next Steps

After successful setup:
1. Monitor first few automated runs
2. Review output reports for accuracy
3. Adjust cron schedule if needed
4. Set up monitoring/alerting for failures
5. Document any custom configurations
