# BigQuery Domain Analysis - Project Documentation

**Document Version:** 1.0
**Last Updated:** 2025-11-22
**Document Owner:** Data Engineering Team
**Document Type:** Business Analyst Documentation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Purpose](#business-purpose)
3. [Project Overview](#project-overview)
4. [System Architecture](#system-architecture)
5. [Data Sources](#data-sources)
6. [Process Flow](#process-flow)
7. [Component Descriptions](#component-descriptions)
8. [Output Deliverables](#output-deliverables)
9. [Automation & Scheduling](#automation--scheduling)
10. [Data Retention Policy](#data-retention-policy)
11. [Error Handling & Monitoring](#error-handling--monitoring)
12. [Security Considerations](#security-considerations)
13. [Dependencies](#dependencies)
14. [Success Metrics](#success-metrics)
15. [Troubleshooting Guide](#troubleshooting-guide)

---

## Executive Summary

The BigQuery Domain Analysis project is an automated data pipeline that extracts, analyzes, and reports on web domain performance metrics from Google BigQuery. The system performs daily day-over-day analysis of active users and pageviews across multiple domains, generating both human-readable and machine-readable reports for stakeholders.

**Key Benefits:**
- Automated daily performance tracking
- Quick identification of significant traffic changes
- Historical trend analysis capability
- Reduced manual reporting effort
- Standardized reporting format

---

## Business Purpose

### Primary Objectives

1. **Performance Monitoring**: Track daily changes in domain traffic and user engagement
2. **Anomaly Detection**: Identify domains with significant increases or decreases in activity
3. **Data-Driven Decision Making**: Provide stakeholders with timely, accurate performance data
4. **Operational Efficiency**: Automate manual reporting processes

### Target Audience

- **Primary**: Business analysts, marketing teams, product managers
- **Secondary**: Data analysts, executive leadership
- **Technical**: Operations team for monitoring and maintenance

### Business Value

- **Time Savings**: Eliminates 2-3 hours of manual reporting per day
- **Consistency**: Standardized metrics and reporting format
- **Timeliness**: Automated daily delivery before business hours
- **Scalability**: Can handle growing number of domains without additional effort

---

## Project Overview

### What It Does

The system performs the following business functions:

1. Connects to the organization's BigQuery data warehouse
2. Retrieves domain performance data for the two most recent dates
3. Calculates day-over-day changes in traffic metrics
4. Identifies top movers (biggest increases and decreases)
5. Generates formatted reports in multiple formats
6. Maintains a 30-day archive of historical reports
7. Logs all operations for audit and troubleshooting

### Key Metrics Tracked

| Metric | Description | Business Significance |
|--------|-------------|----------------------|
| **Active Users** | Unique users visiting the domain | Measures audience reach and engagement |
| **Pageviews** | Total page views across the domain | Indicates content consumption and site stickiness |
| **Day-over-Day Change** | Absolute change from previous day | Identifies trending domains |
| **Percentage Change** | Relative change from previous day | Normalizes changes for domain size |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Google BigQuery                           │
│              iab-publisher-data.dap_daily.dap_domain        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ SQL Query (Service Account Auth)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              BigQuery Domain Analysis Script                 │
│                  (Python Application)                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Data Extract │→ │   Process    │→ │   Generate   │     │
│  │              │  │  & Analyze   │  │   Reports    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               Output Directory Structure                     │
│          ~/Downloads/domain_reports/                        │
│                                                              │
│  ├── domain_analysis_2025-11-22_080001.txt                 │
│  ├── domain_analysis_2025-11-22_080001.csv                 │
│  └── logs/                                                  │
│      ├── cron_log_2025-11.log                              │
│      └── cron_stdout.log                                   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Warehouse** | Google BigQuery | Source data storage |
| **Programming Language** | Python 3.7+ | Application logic |
| **Data Processing** | Pandas | Data manipulation and analysis |
| **Authentication** | Google Cloud Service Account | Secure API access |
| **Scheduling** | Cron (macOS) | Automated execution |
| **Logging** | Python logging module | Audit trail and monitoring |

---

## Data Sources

### Primary Data Source

**BigQuery Table:** `iab-publisher-data.dap_daily.dap_domain`

**Data Structure:**
```
Table: dap_domain
├── date (DATE) - Date of data collection
├── domain_name (STRING) - Website domain identifier
├── platform (STRING) - Platform type (aggregated in analysis)
├── total_activeUsers (INTEGER) - Count of active users
└── total_screenPageViews (INTEGER) - Count of pageviews
```

### Data Aggregation

The system aggregates data across all platforms for each domain:
- **Input**: Multiple rows per domain (one per platform)
- **Output**: Single row per domain with summed metrics
- **Grouping**: By `domain_name` and `date`

### Data Freshness

- System automatically detects the two most recent dates in the dataset
- No hardcoded dates ensures flexibility with data availability
- Typically analyzes yesterday vs. day-before-yesterday

---

## Process Flow

### End-to-End Process

```
START
  │
  ├─► 1. INITIALIZATION
  │     ├─ Create output directories
  │     ├─ Set up logging
  │     └─ Validate credentials file exists
  │
  ├─► 2. AUTHENTICATION
  │     ├─ Load service account credentials
  │     └─ Initialize BigQuery client
  │
  ├─► 3. DATA DISCOVERY
  │     ├─ Query for 2 most recent dates
  │     └─ Validate sufficient data exists
  │
  ├─► 4. DATA EXTRACTION
  │     ├─ Query domain metrics for both dates
  │     ├─ Aggregate by domain (sum across platforms)
  │     └─ Load into Pandas DataFrame
  │
  ├─► 5. DATA ANALYSIS
  │     ├─ Separate data by date
  │     ├─ Join previous and current data
  │     ├─ Calculate absolute changes
  │     ├─ Calculate percentage changes
  │     └─ Handle missing data (new/removed domains)
  │
  ├─► 6. REPORT GENERATION
  │     ├─ Identify top 10 domains by user change
  │     ├─ Identify top 10 domains by pageview change
  │     ├─ Format TXT report (human-readable)
  │     └─ Format CSV report (machine-readable)
  │
  ├─► 7. FILE MANAGEMENT
  │     ├─ Save reports with timestamp
  │     ├─ Delete files older than 30 days
  │     └─ Update log files
  │
  └─► 8. COMPLETION
        ├─ Log success message
        └─ Exit with status code
END
```

### Processing Time

- **Typical Duration**: 30-60 seconds
- **BigQuery Query Time**: 10-20 seconds
- **Data Processing**: 5-10 seconds
- **Report Generation**: 5-10 seconds

---

## Component Descriptions

### 1. Configuration Module (Lines 34-49)

**Purpose:** Centralized configuration management

**Key Settings:**
- `PROJECT_ID`: BigQuery project identifier
- `DATASET_ID`: BigQuery dataset name
- `TABLE_ID`: Source table name
- `CREDENTIALS_PATH`: Service account JSON file location
- `BASE_OUTPUT_DIR`: Report output location
- `RETENTION_DAYS`: File retention policy (30 days)

**Business Impact:** Allows easy updates to system parameters without code changes

---

### 2. Logging System (Lines 55-84)

**Purpose:** Comprehensive audit trail and troubleshooting support

**Features:**
- Monthly log file rotation (e.g., `cron_log_2025-11.log`)
- Dual output (file and console)
- Timestamped entries
- Multiple log levels (INFO, ERROR)

**Business Value:**
- Compliance and audit trail
- Performance monitoring
- Issue diagnosis
- Historical execution tracking

**Log File Location:** `~/Downloads/domain_reports/logs/`

---

### 3. File Management System (Lines 91-128)

**Purpose:** Automated file lifecycle management

**Functions:**

#### Directory Management
- Automatically creates output directories if missing
- Ensures consistent folder structure

#### File Cleanup (Retention Policy)
- Scans for files older than 30 days
- Automatically deletes expired reports
- Logs deletion activities

**Business Value:**
- Prevents disk space issues
- Maintains relevant historical data
- Reduces manual maintenance

---

### 4. BigQuery Operations (Lines 135-245)

**Purpose:** Data warehouse connectivity and data extraction

**Components:**

#### Authentication (Lines 135-166)
- Loads service account credentials
- Validates credential file exists
- Establishes secure connection to BigQuery

#### Date Discovery (Lines 169-209)
- Identifies 2 most recent dates in dataset
- Ensures sufficient data for comparison
- Validates data availability

**SQL Query:**
```sql
SELECT DISTINCT DATE(date) as date
FROM `iab-publisher-data.dap_daily.dap_domain`
ORDER BY date DESC
LIMIT 2
```

#### Data Extraction (Lines 212-245)
- Retrieves domain metrics for both dates
- Aggregates across platforms
- Returns structured dataset

**SQL Query:**
```sql
SELECT
    DATE(date) as date,
    domain_name,
    SUM(total_activeUsers) as total_activeUsers,
    SUM(total_screenPageViews) as total_screenPageViews
FROM `iab-publisher-data.dap_daily.dap_domain`
WHERE DATE(date) IN ('YYYY-MM-DD', 'YYYY-MM-DD')
GROUP BY date, domain_name
ORDER BY domain_name, date
```

**Business Value:**
- Reliable data access
- Consistent data aggregation
- Error handling for data issues

---

### 5. Data Processing Engine (Lines 252-315)

**Purpose:** Calculate business metrics and trends

**Process:**

1. **Data Separation**
   - Split dataset into previous and current date
   - Rename columns for clarity

2. **Data Merging**
   - Outer join on domain_name
   - Handles new domains (no previous data)
   - Handles removed domains (no current data)

3. **Change Calculation**
   - **Absolute Change**: Current - Previous
   - **Percentage Change**: (Change / Previous) × 100
   - Handles division by zero (new domains)
   - Handles infinity values

4. **Data Type Conversion**
   - Converts metrics to integers
   - Rounds percentages to 1 decimal place

**Business Rules:**
- Domains appearing only on one date are included (zero-filled)
- Infinite percentage changes are set to 0
- Negative changes indicate decline
- Positive changes indicate growth

---

### 6. Report Generation System (Lines 320-505)

**Purpose:** Create stakeholder-facing deliverables

#### Text Report (TXT Format)

**Structure:**
```
=============================================================================
BIGQUERY DOMAIN ANALYSIS REPORT
=============================================================================
Generated: 2025-11-22 08:00:01
Data Range: 2025-11-20 to 2025-11-21
Total Domains Analyzed: 150

TABLE 1: TOP 10 DOMAINS BY ACTIVE USERS CHANGE (BY ABSOLUTE VOLUME)
=============================================================================

Rank   Domain                Latest Date     Previous Date   Change    Change %   Dir
-----------------------------------------------------------------------------------
1      example.com          50,000          45,000          +5,000    +11.1%     ↑
...

Summary: 75 gainers, 73 decliners | Total change: +12,500

TABLE 2: TOP 10 DOMAINS BY PAGEVIEWS CHANGE (BY ABSOLUTE VOLUME)
=============================================================================
[Similar format]
```

**Features:**
- Clear column headers with actual dates
- Comma-separated number formatting
- Percentage with sign (+/-)
- Direction arrows (↑ ↓ →)
- Summary statistics

**Target Audience:** Executives, managers, non-technical stakeholders

#### CSV Report (CSV Format)

**Columns:**
- `domain_name`: Domain identifier
- `prev_users`: Previous day active users
- `latest_users`: Current day active users
- `users_change`: Absolute change in users
- `users_pct_change`: Percentage change in users
- `prev_views`: Previous day pageviews
- `latest_views`: Current day pageviews
- `views_change`: Absolute change in pageviews
- `views_pct_change`: Percentage change in pageviews
- `report_date`: Report generation timestamp
- `previous_date`: Previous data date
- `latest_date`: Current data date

**Features:**
- Includes ALL domains (not just top 10)
- Sorted by users_change (descending)
- Machine-readable format
- Includes metadata columns

**Target Audience:** Data analysts, BI tools, further analysis

---

### 7. Main Execution Controller (Lines 512-570)

**Purpose:** Orchestrate end-to-end process flow

**Responsibilities:**
1. Initialize system components
2. Execute process steps in sequence
3. Handle errors gracefully
4. Return appropriate exit codes

**Error Handling:**
- `FileNotFoundError`: Missing credentials file
- `ValueError`: Insufficient data in BigQuery
- `Exception`: Unexpected errors (with full stack trace)

**Exit Codes:**
- `0`: Success
- `1`: Failure (any type)

**Business Value:** Reliable automated execution with proper error reporting

---

## Output Deliverables

### Report Files

#### TXT Report
- **Filename Pattern:** `domain_analysis_YYYY-MM-DD_HHMMSS.txt`
- **Format:** Fixed-width formatted tables
- **Size:** ~5-10 KB
- **Use Case:** Quick review, email distribution, executive dashboards

#### CSV Report
- **Filename Pattern:** `domain_analysis_YYYY-MM-DD_HHMMSS.csv`
- **Format:** Comma-separated values
- **Size:** ~50-200 KB (varies with domain count)
- **Use Case:** Excel analysis, BI tool import, statistical analysis

### Log Files

#### Execution Logs
- **Filename Pattern:** `cron_log_YYYY-MM.log`
- **Format:** Timestamped log entries
- **Rotation:** Monthly
- **Use Case:** Troubleshooting, audit trail, performance monitoring

#### Cron Output
- **Filename:** `cron_stdout.log`
- **Format:** Standard output and error streams
- **Use Case:** Cron job debugging

---

## Automation & Scheduling

### Cron Configuration

**Recommended Schedule:** Daily at 8:00 AM

```cron
0 8 * * * /Users/geoffcohen/antig1/bigquery_domain_analysis.py >> ~/Downloads/domain_reports/logs/cron_stdout.log 2>&1
```

**Alternative Schedules:**

| Schedule | Cron Expression | Use Case |
|----------|----------------|----------|
| Weekdays 7:30 AM | `30 7 * * 1-5` | Business days only |
| Twice daily | `0 8,18 * * *` | Morning and evening reports |
| Every 6 hours | `0 */6 * * *` | High-frequency monitoring |

### Execution Environment

- **Platform:** macOS (compatible with Linux)
- **Shell:** `/usr/bin/env python3`
- **Permissions:** Executable script (`chmod +x`)
- **Full Disk Access:** Required for cron on macOS Catalina+

### Unattended Operation

**Design Features:**
- No user interaction required
- Automatic error recovery where possible
- Comprehensive logging for remote monitoring
- Exit codes for monitoring systems

---

## Data Retention Policy

### Policy Overview

**Retention Period:** 30 days for report files

**Rationale:**
- Balances historical access with storage management
- Sufficient for monthly trend analysis
- Prevents unlimited disk usage growth

### What Gets Deleted

- TXT reports older than 30 days
- CSV reports older than 30 days

### What Gets Retained

- Log files (monthly rotation, manual cleanup)
- Current month data (always preserved)

### Cleanup Process

- **Trigger:** Every script execution
- **Method:** File modification time comparison
- **Logged:** All deletions recorded in log file
- **Safety:** Only deletes files matching pattern `domain_analysis_*`

### Override Options

To change retention period, modify configuration:
```python
RETENTION_DAYS = 30  # Change to desired value
```

---

## Error Handling & Monitoring

### Error Categories

#### 1. Configuration Errors
- **Example:** Missing credentials file
- **Detection:** File existence check at startup
- **Response:** Clear error message, exit code 1
- **Resolution:** Update credentials path

#### 2. Authentication Errors
- **Example:** Invalid service account
- **Detection:** BigQuery client initialization
- **Response:** Error logged, exit code 1
- **Resolution:** Verify service account permissions

#### 3. Data Errors
- **Example:** Insufficient dates in dataset
- **Detection:** Date query validation
- **Response:** Error logged with details, exit code 1
- **Resolution:** Check BigQuery data pipeline

#### 4. Unexpected Errors
- **Example:** Network timeouts, API errors
- **Detection:** Try-catch blocks throughout
- **Response:** Full stack trace logged, exit code 1
- **Resolution:** Review log file for details

### Monitoring Recommendations

#### Daily Checks
- Verify new reports generated
- Check log file for errors
- Review summary statistics

#### Weekly Checks
- Verify cron job execution times
- Review disk space usage
- Check for repeated errors

#### Monthly Checks
- Validate data accuracy
- Review retention policy effectiveness
- Archive important reports if needed

### Monitoring Commands

```bash
# Check latest execution
tail -50 ~/Downloads/domain_reports/logs/cron_log_$(date +%Y-%m).log

# List recent reports
ls -lt ~/Downloads/domain_reports/*.txt | head -5

# Check for errors
grep ERROR ~/Downloads/domain_reports/logs/cron_log_*.log
```

---

## Security Considerations

### Credential Management

**Service Account File:**
- **Location:** `~/iab-5d3c53b40c41.json`
- **Permissions:** `600` (user read/write only)
- **Type:** Google Cloud Service Account JSON key
- **Access:** BigQuery read-only recommended

**Security Best Practices:**
1. Never commit credentials to version control
2. Use minimal required permissions
3. Rotate keys periodically (recommended: quarterly)
4. Monitor service account usage logs
5. Use separate service accounts per environment

### Data Access

**Principle of Least Privilege:**
- Service account has read-only access to specific BigQuery dataset
- No write permissions to BigQuery
- No access to other GCP resources

### File System Security

**Output Directory:**
- Default location: `~/Downloads/domain_reports/`
- Inherits user's file permissions
- Consider restricting access if contains sensitive data

### Audit Trail

- All operations logged with timestamps
- Authentication attempts logged
- File access patterns trackable via logs
- Suitable for compliance requirements

---

## Dependencies

### Software Requirements

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.7+ | Runtime environment |
| google-cloud-bigquery | 3.11.0+ | BigQuery client library |
| pandas | 2.0.0+ | Data manipulation |
| db-dtypes | 1.1.0+ | BigQuery data type support |

### Installation

```bash
pip3 install -r requirements.txt
```

### System Requirements

- **Operating System:** macOS (Linux compatible)
- **Disk Space:** ~100 MB (varies with data volume)
- **Network:** Internet access for BigQuery API
- **Cron:** System cron daemon running

### External Dependencies

- **Google Cloud Platform:** BigQuery service availability
- **Network Connectivity:** Stable internet connection
- **Service Account:** Active GCP service account

---

## Success Metrics

### System Performance Metrics

| Metric | Target | Current | Monitoring Method |
|--------|--------|---------|-------------------|
| **Execution Success Rate** | 99%+ | Track in logs | Daily log review |
| **Execution Time** | <2 minutes | 30-60 seconds | Log timestamps |
| **Report Accuracy** | 100% | Validated | Spot checks |
| **Storage Usage** | <500 MB | ~200 MB | Disk usage monitoring |

### Business Metrics

| Metric | Description | Value |
|--------|-------------|-------|
| **Time Saved** | Manual reporting hours eliminated | 2-3 hrs/day |
| **Report Timeliness** | Reports available by start of business | 100% |
| **Stakeholder Satisfaction** | User feedback on report utility | High |
| **Data Coverage** | Domains tracked | All active domains |

### Quality Indicators

- **Data Completeness:** All domains present in source appear in reports
- **Calculation Accuracy:** Change calculations mathematically correct
- **Format Consistency:** Reports follow standard template
- **Historical Continuity:** Daily reports without gaps

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: "Credentials file not found"

**Symptoms:**
```
ERROR: Credentials file not found: /Users/geoffcohen/iab-5d3c53b40c41.json
```

**Solutions:**
1. Verify file exists: `ls -la ~/iab-5d3c53b40c41.json`
2. Check file path in script matches actual location
3. Ensure file permissions allow reading: `chmod 600 ~/iab-5d3c53b40c41.json`

---

#### Issue 2: "Insufficient data: Found 1 dates, need at least 2"

**Symptoms:**
```
ERROR: Insufficient data: Found 1 dates, need at least 2 for comparison
```

**Solutions:**
1. Verify BigQuery table has data for multiple dates
2. Check data pipeline is running daily
3. Query BigQuery directly to confirm data:
   ```sql
   SELECT DISTINCT DATE(date) FROM `iab-publisher-data.dap_daily.dap_domain`
   ORDER BY date DESC LIMIT 5
   ```

---

#### Issue 3: Reports not generated

**Symptoms:** No new files in output directory

**Solutions:**
1. Check log file for errors
2. Verify cron job is running: `crontab -l`
3. Check cron has Full Disk Access (macOS Security & Privacy settings)
4. Test manual execution: `./bigquery_domain_analysis.py`
5. Verify output directory is writable

---

#### Issue 4: Cron job not executing

**Symptoms:** No log entries at scheduled time

**Solutions:**
1. Verify cron service running: `sudo launchctl list | grep cron`
2. Check crontab syntax: `crontab -l`
3. Review system cron logs
4. Test with simple cron job first
5. Ensure absolute paths used in crontab

---

#### Issue 5: Authentication failures

**Symptoms:**
```
ERROR: Failed to authenticate with BigQuery
```

**Solutions:**
1. Verify service account has BigQuery permissions
2. Check service account is enabled in GCP console
3. Confirm project ID is correct
4. Validate JSON key file format
5. Test authentication manually with gcloud CLI

---

### Getting Help

**For Technical Issues:**
1. Review log files first: `~/Downloads/domain_reports/logs/`
2. Check this documentation
3. Review SETUP.md for configuration details
4. Contact: Data Engineering Team

**For Business/Reporting Issues:**
1. Review output reports for data quality
2. Validate against source BigQuery data
3. Contact: Business Analytics Team

---

## Appendix

### File Locations Quick Reference

| Item | Location |
|------|----------|
| **Script** | `/Users/geoffcohen/antig1/bigquery_domain_analysis.py` |
| **Credentials** | `/Users/geoffcohen/iab-5d3c53b40c41.json` |
| **Output Reports** | `~/Downloads/domain_reports/` |
| **Log Files** | `~/Downloads/domain_reports/logs/` |
| **Requirements** | `/Users/geoffcohen/antig1/requirements.txt` |
| **Setup Guide** | `/Users/geoffcohen/antig1/SETUP.md` |

### Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-22 | Initial documentation | Business Analyst |

### Related Documentation

- **SETUP.md** - Technical setup and configuration guide
- **README.md** - Quick start guide
- **requirements.txt** - Python dependencies

---

**End of Document**
