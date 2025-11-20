const { BigQuery } = require('@google-cloud/bigquery');
const path = require('path');

const keyFile = path.join(process.cwd(), 'service-account.json');
const bigquery = new BigQuery({
    projectId: 'iab-publisher-data',
    keyFilename: keyFile,
});

async function checkData() {
    const query = `
    SELECT 
      date, 
      SUM(total_screenPageViews) as total_views 
    FROM \`iab-publisher-data.dap_daily.dap_domain\` 
    GROUP BY date 
    ORDER BY date DESC
    LIMIT 5
  `;

    try {
        const [rows] = await bigquery.query({ query });
        console.log('Data found:', rows.length);
        console.log(rows);
    } catch (e) {
        console.error('Query failed:', e);
    }
}

checkData();
