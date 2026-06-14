/**
 * test-webhook.js
 * Sends a simulated WhatsApp webhook payload to your n8n workflow.
 * Run as: node test-webhook.js <webhook_url> "<message>"
 */

const http = require('http');
const https = require('https');
const { URL } = require('url');

// Default Webhook URLs
const DEFAULT_CLOUD_URL = 'https://seerootravels.app.n8n.cloud/webhook-test/whatsapp/webhook';
const DEFAULT_LOCAL_URL = 'http://localhost:5678/webhook-test/whatsapp/webhook';

// Read arguments
const args = process.argv.slice(2);
let webhookUrl = args[0] || DEFAULT_CLOUD_URL;
let testMessage = args[1] || 'I want to book a Premium Gold 15 Days Umrah package next December for 3 people';
const senderPhone = args[2] || '923001234567';
const senderName = args[3] || 'Test User';

if (webhookUrl === 'local') {
  webhookUrl = DEFAULT_LOCAL_URL;
} else if (webhookUrl === 'cloud') {
  webhookUrl = DEFAULT_CLOUD_URL;
}

console.log("=== WhatsApp Webhook Simulator ===");
console.log(`Target Webhook URL: \x1b[36m${webhookUrl}\x1b[0m`);
console.log(`Test Message:       "${testMessage}"`);
console.log(`Sender Name:        "${senderName}"`);
console.log(`Sender Phone:       "${senderPhone}"\n`);

const payload = JSON.stringify({
  body: {
    message: testMessage,
    chat_id: `whatsapp-${senderPhone}`,
    sender: {
      attendee_id: senderPhone,
      attendee_provider_id: senderPhone,
      attendee_name: senderName
    }
  }
});

function sendWebhook() {
  let urlObj;
  try {
    urlObj = new URL(webhookUrl);
  } catch (e) {
    console.error(`\x1b[31mError:\x1b[0m Invalid URL format: ${webhookUrl}`);
    process.exit(1);
  }

  const options = {
    hostname: urlObj.hostname,
    port: urlObj.port || (urlObj.protocol === 'https:' ? 443 : 80),
    path: urlObj.pathname + urlObj.search,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': payload.length
    }
  };

  const client = urlObj.protocol === 'https:' ? https : http;

  const req = client.request(options, (res) => {
    let responseBody = '';
    res.on('data', (chunk) => responseBody += chunk);
    res.on('end', () => {
      console.log(`Status Code: \x1b[32m${res.statusCode}\x1b[0m`);
      console.log('Response Body:');
      console.log(responseBody || '(empty response)');
      console.log('\n\x1b[32m✔ Webhook sent successfully!\x1b[0m Check your n8n execution log to see the path.');
    });
  });

  req.on('error', (err) => {
    console.error(`\x1b[31mFailed to connect to n8n Webhook:\x1b[0m ${err.message}`);
    console.log('\nMake sure your n8n workflow is active, or in "Listen for test event" mode if using test webhook URL.');
  });

  req.write(payload);
  req.end();
}

sendWebhook();
