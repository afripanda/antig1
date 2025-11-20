import { NextResponse } from 'next/server';
import { bigquery } from '@/lib/bigquery';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const type = searchParams.get('type');

  try {
    let query = '';
    let params: any[] = [];

    switch (type) {
      case 'trend':
        query = `
          SELECT 
            date, 
            SUM(total_screenPageViews) as total_views 
          FROM \`iab-publisher-data.dap_daily.dap_domain\` 
          GROUP BY date 
          ORDER BY date ASC
        `;
        break;
      case 'top-domains':
        query = `
          SELECT 
            domain_name, 
            monthly_pageviews 
          FROM \`iab-publisher-data.da_monthly.mv_domain_monthly_metrics\` 
          ORDER BY monthly_pageviews DESC 
          LIMIT 5
        `;
        break;
      case 'platform':
        query = `
          SELECT 
            platform, 
            SUM(total_screenPageViews) as total_views 
          FROM \`iab-publisher-data.dap_daily.dap_domain\` 
          GROUP BY platform
        `;
        break;
      default:
        return NextResponse.json({ error: 'Invalid type' }, { status: 400 });
    }

    const [rows] = await bigquery.query({ query, params });

    // Serialize BigQuery dates/timestamps and BigInts
    const serializedRows = rows.map(row => {
      const newRow: any = { ...row };
      if (newRow.date && newRow.date.value) newRow.date = newRow.date.value;
      // Handle BigInt (e.g. total_views)
      for (const key in newRow) {
        if (typeof newRow[key] === 'bigint') {
          newRow[key] = Number(newRow[key]);
        }
      }
      return newRow;
    });

    return NextResponse.json(serializedRows);
  } catch (error) {
    console.error('BigQuery Error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
