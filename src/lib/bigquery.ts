import { BigQuery } from '@google-cloud/bigquery';
import path from 'path';

const projectId = 'iab-publisher-data';
const keyFile = path.join(process.cwd(), 'service-account.json');

// Check if we have credentials in an environment variable (for Vercel/Production)
let options: any = { projectId };

if (process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON) {
  try {
    options.credentials = JSON.parse(process.env.GOOGLE_APPLICATION_CREDENTIALS_JSON);
  } catch (e) {
    console.error('Failed to parse GOOGLE_APPLICATION_CREDENTIALS_JSON', e);
  }
} else {
  // Fallback to local file
  options.keyFilename = keyFile;
}

export const bigquery = new BigQuery(options);

