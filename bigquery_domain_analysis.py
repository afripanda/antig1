#!/usr/bin/env python3
"""
BigQuery Domain Analysis Script
Automated cron job to extract and analyze domain performance data from BigQuery.

This script:
1. Connects to BigQuery using service account credentials
2. Extracts data for the two most recent dates
3. Performs day-over-day analysis by domain
4. Generates formatted TXT and CSV reports
5. Maintains 30-day file retention policy
6. Logs all operations for cron monitoring

Author: Data Engineering Team
Last Modified: 2025-11-20
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Optional
import os

try:
    from google.cloud import bigquery
    import pandas as pd
except ImportError as e:
    print(f"ERROR: Missing required package: {e}")
    print("Please install requirements: pip install google-cloud-bigquery pandas db-dtypes")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

# BigQuery Configuration
PROJECT_ID = "iab-publisher-data"
DATASET_ID = "dap_daily"
TABLE_ID = "dap_domain"

# Credentials - Service account JSON file
CREDENTIALS_PATH = os.path.expanduser("~/iab-5d3c53b40c41.json")

# Output Configuration
BASE_OUTPUT_DIR = Path.home() / "Downloads" / "domain_reports"
LOGS_DIR = BASE_OUTPUT_DIR / "logs"
RETENTION_DAYS = 30

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging() -> logging.Logger:
    """
    Set up file-based logging with monthly rotation.
    
    Returns:
        Configured logger instance
    """
    # Ensure logs directory exists
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create monthly log file
    log_filename = f"cron_log_{datetime.now().strftime('%Y-%m')}.log"
    log_path = LOGS_DIR / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout)  # Also print to console
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("BigQuery Domain Analysis Script Started")
    logger.info("=" * 80)
    
    return logger


# ============================================================================
# FILE MANAGEMENT
# ============================================================================

def ensure_directories() -> None:
    """Create necessary directories if they don't exist."""
    BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {BASE_OUTPUT_DIR}")
    logger.info(f"Logs directory: {LOGS_DIR}")


def cleanup_old_files() -> None:
    """Remove files older than RETENTION_DAYS."""
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted_count = 0
    
    for file_path in BASE_OUTPUT_DIR.glob("domain_analysis_*"):
        if file_path.is_file():
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime < cutoff_date:
                file_path.unlink()
                deleted_count += 1
                logger.info(f"Deleted old file: {file_path.name}")
    
    if deleted_count > 0:
        logger.info(f"Cleanup complete: {deleted_count} old files removed")
    else:
        logger.info("Cleanup complete: No old files to remove")


def get_output_filenames() -> Tuple[Path, Path]:
    """
    Generate timestamped output filenames.
    
    Returns:
        Tuple of (txt_path, csv_path)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    txt_file = BASE_OUTPUT_DIR / f"domain_analysis_{timestamp}.txt"
    csv_file = BASE_OUTPUT_DIR / f"domain_analysis_{timestamp}.csv"
    return txt_file, csv_file


# ============================================================================
# BIGQUERY OPERATIONS
# ============================================================================

def get_bigquery_client() -> bigquery.Client:
    """
    Initialize BigQuery client with service account credentials.
    
    Returns:
        Authenticated BigQuery client
        
    Raises:
        FileNotFoundError: If credentials file doesn't exist
        Exception: If authentication fails
    """
    creds_path = Path(CREDENTIALS_PATH)
    
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Credentials file not found: {CREDENTIALS_PATH}\n"
            f"Please update CREDENTIALS_PATH in the script to point to your "
            f"service account JSON file."
        )
    
    logger.info(f"Using credentials: {CREDENTIALS_PATH}")
    
    try:
        client = bigquery.Client.from_service_account_json(
            str(creds_path),
            project=PROJECT_ID
        )
        logger.info(f"Connected to BigQuery project: {PROJECT_ID}")
        return client
    except Exception as e:
        logger.error(f"Failed to authenticate with BigQuery: {e}")
        raise


def get_recent_dates(client: bigquery.Client) -> Tuple[str, str]:
    """
    Find the two most recent dates in the dataset.
    
    Args:
        client: Authenticated BigQuery client
        
    Returns:
        Tuple of (previous_date, latest_date) as strings
        
    Raises:
        ValueError: If insufficient data is available
    """
    query = f"""
    SELECT DISTINCT DATE(date) as date
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY date DESC
    LIMIT 2
    """
    
    logger.info("Querying for most recent dates...")
    
    try:
        df = client.query(query).to_dataframe()
        
        if len(df) < 2:
            raise ValueError(
                f"Insufficient data: Found {len(df)} dates, need at least 2 for comparison"
            )
        
        latest_date = df.iloc[0]['date'].strftime('%Y-%m-%d')
        previous_date = df.iloc[1]['date'].strftime('%Y-%m-%d')
        
        logger.info(f"Latest date: {latest_date}")
        logger.info(f"Previous date: {previous_date}")
        
        return previous_date, latest_date
        
    except Exception as e:
        logger.error(f"Failed to retrieve dates: {e}")
        raise


def extract_domain_data(client: bigquery.Client, previous_date: str, latest_date: str) -> pd.DataFrame:
    """
    Extract and aggregate domain data for the two most recent dates.
    
    Args:
        client: Authenticated BigQuery client
        previous_date: Previous date string (YYYY-MM-DD)
        latest_date: Latest date string (YYYY-MM-DD)
        
    Returns:
        DataFrame with aggregated domain metrics
    """
    query = f"""
    SELECT 
        DATE(date) as date,
        domain_name,
        SUM(total_activeUsers) as total_activeUsers,
        SUM(total_screenPageViews) as total_screenPageViews
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    WHERE DATE(date) IN ('{previous_date}', '{latest_date}')
    GROUP BY date, domain_name
    ORDER BY domain_name, date
    """
    
    logger.info("Extracting domain data from BigQuery...")
    
    try:
        df = client.query(query).to_dataframe()
        logger.info(f"Retrieved {len(df)} records")
        return df
        
    except Exception as e:
        logger.error(f"Failed to extract data: {e}")
        raise


# ============================================================================
# DATA PROCESSING
# ============================================================================

def calculate_changes(df: pd.DataFrame, previous_date: str, latest_date: str) -> pd.DataFrame:
    """
    Calculate day-over-day changes for each domain.
    
    Args:
        df: DataFrame with domain data
        previous_date: Previous date string
        latest_date: Latest date string
        
    Returns:
        DataFrame with change metrics
    """
    logger.info("Calculating day-over-day changes...")
    
    # Convert date column to string for comparison
    df['date'] = df['date'].astype(str)
    
    # Split into previous and latest dataframes
    prev_df = df[df['date'] == previous_date].copy()
    latest_df = df[df['date'] == latest_date].copy()
    
    # Rename columns for clarity
    prev_df = prev_df.rename(columns={
        'total_activeUsers': 'prev_users',
        'total_screenPageViews': 'prev_views'
    })
    latest_df = latest_df.rename(columns={
        'total_activeUsers': 'latest_users',
        'total_screenPageViews': 'latest_views'
    })
    
    # Merge on domain_name
    merged = pd.merge(
        prev_df[['domain_name', 'prev_users', 'prev_views']],
        latest_df[['domain_name', 'latest_users', 'latest_views']],
        on='domain_name',
        how='outer'
    )
    
    # Fill NaN values with 0 (for domains that only appear in one date)
    merged = merged.fillna(0)
    
    # Calculate changes
    merged['users_change'] = merged['latest_users'] - merged['prev_users']
    merged['users_pct_change'] = (
        (merged['users_change'] / merged['prev_users'] * 100)
        .replace([float('inf'), -float('inf')], 0)
        .fillna(0)
    )
    
    merged['views_change'] = merged['latest_views'] - merged['prev_views']
    merged['views_pct_change'] = (
        (merged['views_change'] / merged['prev_views'] * 100)
        .replace([float('inf'), -float('inf')], 0)
        .fillna(0)
    )
    
    # Convert to integers where appropriate
    for col in ['prev_users', 'latest_users', 'users_change', 'prev_views', 'latest_views', 'views_change']:
        merged[col] = merged[col].astype(int)
    
    logger.info(f"Calculated changes for {len(merged)} domains")
    
    return merged


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def format_number(num: int) -> str:
    """Format number with commas."""
    return f"{num:,}"


def format_percentage(pct: float) -> str:
    """Format percentage with sign and one decimal place."""
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.1f}%"


def get_arrow(change: int) -> str:
    """Get direction arrow based on change."""
    return "↑" if change > 0 else "↓" if change < 0 else "→"


def create_users_table(df: pd.DataFrame, previous_date: str, latest_date: str) -> str:
    """
    Create formatted table for top 10 domains by active users change.
    
    Args:
        df: DataFrame with change metrics
        previous_date: Previous date string (YYYY-MM-DD)
        latest_date: Latest date string (YYYY-MM-DD)
        
    Returns:
        Formatted table string
    """
    # Sort by ABSOLUTE change and take top 10
    df['users_change_abs'] = df['users_change'].abs()
    top_10 = df.nlargest(10, 'users_change_abs', keep='all')
    
    lines = []
    lines.append("\n" + "=" * 120)
    lines.append("TABLE 1: TOP 10 DOMAINS BY ACTIVE USERS CHANGE (BY ABSOLUTE VOLUME)")
    lines.append("=" * 120)
    lines.append("")
    
    # Header with actual dates - reordered columns
    header = f"{'Rank':<6} {'Domain':<40} {latest_date:<15} {previous_date:<15} {'Change':<15} {'Change %':<12} {'Dir':<4}"
    lines.append(header)
    lines.append("-" * 120)
    
    # Rows - reordered to match new column order
    for idx, row in enumerate(top_10.itertuples(), 1):
        lines.append(
            f"{idx:<6} "
            f"{row.domain_name:<40} "
            f"{format_number(row.latest_users):<15} "
            f"{format_number(row.prev_users):<15} "
            f"{format_number(row.users_change):<15} "
            f"{format_percentage(row.users_pct_change):<12} "
            f"{get_arrow(row.users_change):<4}"
        )
    
    # Summary
    lines.append("-" * 120)
    gainers = len(df[df['users_change'] > 0])
    decliners = len(df[df['users_change'] < 0])
    total_change = df['users_change'].sum()
    
    lines.append(f"Summary: {gainers} gainers, {decliners} decliners | Total change: {format_number(total_change)}")
    lines.append("=" * 120)
    
    return "\n".join(lines)


def create_views_table(df: pd.DataFrame, previous_date: str, latest_date: str) -> str:
    """
    Create formatted table for top 10 domains by pageviews change.
    
    Args:
        df: DataFrame with change metrics
        previous_date: Previous date string (YYYY-MM-DD)
        latest_date: Latest date string (YYYY-MM-DD)
        
    Returns:
        Formatted table string
    """
    # Sort by ABSOLUTE change and take top 10
    df['views_change_abs'] = df['views_change'].abs()
    top_10 = df.nlargest(10, 'views_change_abs', keep='all')
    
    lines = []
    lines.append("\n" + "=" * 120)
    lines.append("TABLE 2: TOP 10 DOMAINS BY PAGEVIEWS CHANGE (BY ABSOLUTE VOLUME)")
    lines.append("=" * 120)
    lines.append("")
    
    # Header with actual dates - reordered columns
    header = f"{'Rank':<6} {'Domain':<40} {latest_date:<15} {previous_date:<15} {'Change':<15} {'Change %':<12} {'Dir':<4}"
    lines.append(header)
    lines.append("-" * 120)
    
    # Rows - reordered to match new column order
    for idx, row in enumerate(top_10.itertuples(), 1):
        lines.append(
            f"{idx:<6} "
            f"{row.domain_name:<40} "
            f"{format_number(row.latest_views):<15} "
            f"{format_number(row.prev_views):<15} "
            f"{format_number(row.views_change):<15} "
            f"{format_percentage(row.views_pct_change):<12} "
            f"{get_arrow(row.views_change):<4}"
        )
    
    # Summary
    lines.append("-" * 120)
    gainers = len(df[df['views_change'] > 0])
    decliners = len(df[df['views_change'] < 0])
    total_change = df['views_change'].sum()
    
    lines.append(f"Summary: {gainers} gainers, {decliners} decliners | Total change: {format_number(total_change)}")
    lines.append("=" * 120)
    
    return "\n".join(lines)


def save_txt_report(df: pd.DataFrame, txt_path: Path, previous_date: str, latest_date: str) -> None:
    """
    Save formatted text report.
    
    Args:
        df: DataFrame with change metrics
        txt_path: Output file path
        previous_date: Previous date string
        latest_date: Latest date string
    """
    with open(txt_path, 'w') as f:
        # Header
        f.write("=" * 120 + "\n")
        f.write("BIGQUERY DOMAIN ANALYSIS REPORT\n")
        f.write("=" * 120 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Data Range: {previous_date} to {latest_date}\n")
        f.write(f"Total Domains Analyzed: {len(df)}\n")
        
        # Tables
        f.write(create_users_table(df, previous_date, latest_date))
        f.write("\n\n")
        f.write(create_views_table(df, previous_date, latest_date))
        f.write("\n\n")
        
        # Footer
        f.write("=" * 120 + "\n")
        f.write("End of Report\n")
        f.write("=" * 120 + "\n")
    
    logger.info(f"Saved TXT report: {txt_path}")


def save_csv_report(df: pd.DataFrame, csv_path: Path, previous_date: str, latest_date: str) -> None:
    """
    Save CSV report with all data.
    
    Args:
        df: DataFrame with change metrics
        csv_path: Output file path
        previous_date: Previous date string
        latest_date: Latest date string
    """
    # Add metadata columns
    output_df = df.copy()
    output_df['report_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output_df['previous_date'] = previous_date
    output_df['latest_date'] = latest_date
    
    # Reorder columns for better readability
    columns = [
        'domain_name',
        'prev_users', 'latest_users', 'users_change', 'users_pct_change',
        'prev_views', 'latest_views', 'views_change', 'views_pct_change',
        'report_date', 'previous_date', 'latest_date'
    ]
    
    output_df = output_df[columns]
    
    # Sort by users_change descending
    output_df = output_df.sort_values('users_change', ascending=False)
    
    # Save to CSV
    output_df.to_csv(csv_path, index=False)
    
    logger.info(f"Saved CSV report: {csv_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main() -> int:
    """
    Main execution function.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Setup
        ensure_directories()
        
        # Connect to BigQuery
        client = get_bigquery_client()
        
        # Get recent dates
        previous_date, latest_date = get_recent_dates(client)
        
        # Extract data
        df = extract_domain_data(client, previous_date, latest_date)
        
        # Calculate changes
        changes_df = calculate_changes(df, previous_date, latest_date)
        
        # Generate output filenames
        txt_path, csv_path = get_output_filenames()
        
        # Save reports
        save_txt_report(changes_df, txt_path, previous_date, latest_date)
        save_csv_report(changes_df, csv_path, previous_date, latest_date)
        
        # Cleanup old files
        cleanup_old_files()
        
        # Success
        logger.info("=" * 80)
        logger.info("Script completed successfully")
        logger.info(f"TXT Report: {txt_path}")
        logger.info(f"CSV Report: {csv_path}")
        logger.info("=" * 80)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        return 1
        
    except ValueError as e:
        logger.error(f"Data error: {e}")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    logger = setup_logging()
    exit_code = main()
    sys.exit(exit_code)
