/**
 * test-router.js
 * Test script to verify the Groq API and LLM Intent Classifier prompt.
 * Runs using native Node.js 'https' module (no npm install required).
 */

const https = require('https');

const API_KEY = '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';
const MODEL = 'llama-3.3-70b-versatile';

const systemPrompt = `You are the Master Router Agent for Seeroo Travels. Classify the user's travel intent. Respond ONLY in JSON. Intents: 'umrah', 'hajj', 'visa', 'tours', 'flights', 'hotels', 'status_check', 'complaint', 'payment', 'general_faq'. Schema: {"intent": "string", "confidence": float}`;

const testMessages = [
  "I want to book an Umrah package next December for 4 people from Lahore",
  "Mera visa status check kar dein, application number 992817",
  "I want to report a complaint about my hotel room in Makkah, the AC was not working",
  "How much does a flight ticket to Jeddah cost for next week?"
];

function testClassification(message) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: MODEL,
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: message }
      ]
    });

    const options = {
      hostname: 'api.groq.com',
      port: 4443, // Default for secure https or fallback to 443
      path: '/openai/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Length': data.length
      },
      timeout: 10000
    };

    // Fallback port if 4443 fails (some proxies block custom ports)
    options.port = 443;

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode !== 200) {
          return reject(new Error(`API Error (Status ${res.statusCode}): ${body}`));
        }
        try {
          const parsed = JSON.parse(body);
          const content = JSON.parse(parsed.choices[0].message.content);
          resolve(content);
        } catch (e) {
          reject(new Error(`JSON Parsing Error: ${e.message}. Raw response: ${body}`));
        }
      });
    });

    req.on('error', (err) => reject(err));
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timed out after 10s'));
    });
    req.write(data);
    req.end();
  });
}

async function runTests() {
  console.log("=== Starting Groq LLM Intent Classifier Tests ===");
  console.log(`Using Model: ${MODEL}\n`);

  for (const msg of testMessages) {
    console.log(`Testing Message: "${msg}"`);
    try {
      const result = await testClassification(msg);
      console.log(`↳ Result: Intent = \x1b[36m"${result.intent}"\x1b[0m, Confidence = \x1b[32m${result.confidence}\x1b[0m`);
    } catch (err) {
      console.error(`↳ \x1b[31mError:\x1b[0m ${err.message}`);
    }
    console.log("-".repeat(50));
  }
}

runTests();
