# Setup Guide: Travel Agency AI Operating System (AI OS)

This guide walks you through setting up and running the Travel Agency AI OS using Google Sheets, n8n, OpenAI, and Meta (WhatsApp Cloud API).

---

## Step 1: Google Sheets Setup

To set up the database:
1. Create a new Google Spreadsheet at [sheets.google.com](https://sheets.google.com).
2. Go to **Extensions -> Apps Script**.
3. Clear any existing code in the editor, and copy-paste the entire code from **[setup-sheets.gs](file:///c:/Users/Khalil%20Ahmad/OneDrive/Desktop/ai%20agent/setup-sheets.gs)**.
4. Click the **Save** icon, then click the **Run** button.
5. Grant permissions if prompted by Google.
6. The script will automatically generate the following tabs with headers, dropdown validations, and sample packages:
   - `Leads` (CRM Logs)
   - `Packages` (Umrah/Hajj/Tour packages)
   - `SupportTickets` (Complaints log)
   - `Payments` (Receipt verification logs)
7. Copy your Google Spreadsheet ID from the URL:
   `https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID_HERE/edit`

---

## Step 2: Configuration & Credentials Setup

Make sure you have the following API details and environment variables configured in your n8n environment:

| Environment Variable | Description | Value / Source |
|---|---|---|
| `GROQ_API_KEY` | Groq API Key (used in n8n HTTP Request nodes as `{{ $env.GROQ_API_KEY }}`). | `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` (Get from [console.groq.com](https://console.groq.com)) |
| `UNIPILE_DSN` | Unipile Domain/Data Source Name endpoint. | `api50.unipile.com:18030` |
| `UNIPILE_ACCESS_TOKEN`| Unipile access token. | `6i+2zg84.W2iHyl4Pe3T/fREjswsxToHsmCwNJICvweJmod1HJUs=` |
| `UNIPILE_ACCOUNT_ID` | Authenticated WhatsApp account ID. | `ZSQDa63MRHaGw4f33KrMSg` (Linked to Phone: `923205711503`) |
| `SALES_GROUP_CHAT_ID`| Unipile Chat/Group ID to send sales notifications.| Found in Unipile panel or via listing chats |

> [!IMPORTANT]
> **Unipile Webhook Status:**
> Currently configured webhook in Unipile: `https://seerootravels.app.n8n.cloud/webhook-test/whatsapp/webhook`
> *(Remember to remove `-test` from this URL in Unipile once you set the n8n workflow to Active).*

---

## Step 3: Importing n8n Workflows

### 1. Main AI OS Webhook & Qualification Workflow
1. Open your n8n dashboard.
2. Create a new workflow, click the top-right settings (three dots) -> **Import from file**.
3. Select **[n8n-ai-os-workflow.json](file:///c:/Users/Khalil%20Ahmad/OneDrive/Desktop/ai%20agent/n8n-ai-os-workflow.json)**.
4. Open the Google Sheets nodes (e.g. `Lookup Status in CRM`, `Save Lead to Sheets`) and:
   - Connect your **Google Sheets OAuth2 API** credentials.
   - Paste your spreadsheet ID into the `Document ID` field.
5. In the HTTP Request nodes (`LLM Intent Classifier`, `Umrah Qualification`, etc.), ensure the Groq bearer token points to your `GROQ_API_KEY` variable.
6. Click **Save** and set the workflow to **Active**.
7. In the Unipile Webhooks settings page, configure your callback URL pointing to the n8n **WhatsApp Webhook** node URL.

### 2. Staggered Follow-up Workflow
1. Create another new workflow in n8n.
2. Settings -> **Import from file**.
3. Select **[follow-up-workflow.json](file:///c:/Users/Khalil%20Ahmad/OneDrive/Desktop/ai%20agent/follow-up-workflow.json)**.
4. Update the Google Sheets nodes with your Google credentials and Spreadsheet ID.
5. Click **Save** and set the workflow to **Active**.

---

## Step 4: System Prompts (Prompts Customization)

The system prompts for all subagents are pre-embedded directly inside the HTTP Request nodes of the **[n8n-ai-os-workflow.json](file:///c:/Users/Khalil%20Ahmad/OneDrive/Desktop/ai%20agent/n8n-ai-os-workflow.json)** workflow.
- You can customize the instructions, languages (Roman Urdu/English), or JSON schemas directly in the n8n node settings inside each agent's body parameter.

---

## Step 5: Testing & Verification

(Note: If you have deleted the simulation test scripts to clear space, you can skip this step and test directly live via WhatsApp. Otherwise, to run offline tests):

### 1. Route Intent Verification Test
```bash
node test-router.js
```

### 2. Multi-Turn Stateful Memory Simulator
```bash
node test-state.js
```

---

## Appendix: Google Sheets Apps Script Code

Copy and paste this script into your Google Sheet editor (**Extensions -> Apps Script**) to automatically format headers, colors, and dropdown validations:

```javascript
/**
 * setup-sheets.gs
 * Google Apps Script to automatically initialize and configure the Google Sheets CRM Database
 * for the Seeroo Travels AI Operating System.
 */

function setupTravelAgencyCRM() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // Define sheets and their headers
  const schemas = {
    "Leads": [
      "LeadID", "SenderPhone", "SenderName", "Status", "ServiceType", 
      "Month", "Persons", "DepartureCity", "Budget", "VisaPurpose", 
      "TravelDates", "Duration", "SchemeType", "FollowUpCount", 
      "LastFollowUpTime", "ActiveAgent", "BotActive", "CreatedTime"
    ],
    "Packages": [
      "PackageID", "Category", "PackageName", "Duration", "Price", 
      "Currency", "Details", "Status"
    ],
    "SupportTickets": [
      "TicketID", "Phone", "Category", "Description", "Status", 
      "AssignedAgent", "CreatedTime"
    ],
    "Payments": [
      "PaymentID", "LeadID", "Amount", "Method", "ProofUrl", 
      "Verification"
    ]
  };

  // Status and Enum Dropdowns Configurations
  const dropdownRules = {
    "Leads": {
      "Status": ["New", "Qualifying", "Qualified", "Handoff", "Lost"],
      "ServiceType": ["Umrah", "Hajj", "Visa", "Tours", "Flights", "Hotels"],
      "ActiveAgent": ["None", "Umrah", "Hajj", "Visa", "Tours", "Flights", "Hotels", "Complaint", "Payment"],
      "BotActive": ["TRUE", "FALSE"]
    },
    "Packages": {
      "Category": ["Umrah", "Hajj", "International"],
      "Status": ["Active", "Inactive"]
    },
    "SupportTickets": {
      "Category": ["Hotel", "Transport", "Guide", "Visa", "Other"],
      "Status": ["Open", "In-Progress", "Resolved"]
    },
    "Payments": {
      "Method": ["Bank Transfer", "EasyPaisa", "JazzCash"],
      "Verification": ["Pending", "Verified", "Rejected"]
    }
  };

  console.log("Starting CRM Database Setup...");

  // Remove the default "Sheet1" if it exists and is empty
  const defaultSheet = ss.getSheetByName("Sheet1");

  for (const [sheetName, headers] of Object.entries(schemas)) {
    let sheet = ss.getSheetByName(sheetName);
    
    // Create sheet if it does not exist
    if (!sheet) {
      sheet = ss.insertSheet(sheetName);
      console.log(`Created new sheet: ${sheetName}`);
    } else {
      console.log(`Sheet "${sheetName}" already exists. Setting up headers.`);
    }

    // Write headers
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setValues([headers]);

    // Format headers professionally (Dark Gray background, bold white text)
    headerRange.setBackground("#343a40")
               .setFontColor("#ffffff")
               .setFontWeight("bold")
               .setHorizontalAlignment("center")
               .setFontFamily("Inter");

    // Freeze header row
    sheet.setFrozenRows(1);

    // Setup Dropdown Data Validations
    if (dropdownRules[sheetName]) {
      for (const [columnName, options] of Object.entries(dropdownRules[sheetName])) {
        const colIndex = headers.indexOf(columnName) + 1;
        if (colIndex > 0) {
          // Apply validation to rows 2 to 1000 for that column
          const cellRange = sheet.getRange(2, colIndex, 999, 1);
          const rule = SpreadsheetApp.newDataValidation()
                                      .requireValueInList(options)
                                      .setAllowInvalid(false)
                                      .build();
          cellRange.setDataValidation(rule);
          console.log(`Applied dropdown validation for column: ${columnName} in ${sheetName}`);
        }
      }
    }

    // Auto-fit column widths
    for (let c = 1; c <= headers.length; c++) {
      sheet.autoResizeColumn(c);
    }
  }

  // Insert mock/sample data into "Packages" to test n8n matching
  const packagesSheet = ss.getSheetByName("Packages");
  if (packagesSheet.getLastRow() === 1) {
    const mockPackages = [
      ["PKG-UMR-001", "Umrah", "Premium Gold 15 Days", "15 Days", 350000, "PKR", "5-Star Hotels, private luxury transport", "Active"],
      ["PKG-UMR-002", "Umrah", "Economy Silver 15 Days", "15 Days", 260000, "PKR", "3-Star Hotels, shared shuttle transport", "Active"],
      ["PKG-TUR-001", "International", "Thailand Escape Tour", "7 Days", 180000, "PKR", "Bangkok & Phuket hotels + sightseeing", "Active"]
    ];
    packagesSheet.getRange(2, 1, mockPackages.length, 8).setValues(mockPackages);
    console.log("Inserted sample packages data.");
  }

  // If Sheet1 was empty, let's delete it
  if (defaultSheet && defaultSheet.getLastRow() === 0) {
    try {
      ss.deleteSheet(defaultSheet);
      console.log("Deleted default empty Sheet1.");
    } catch (e) {
      console.warn("Could not delete default Sheet1 (it might be the only sheet).");
    }
  }

  console.log("CRM Database Setup Completed Successfully!");
}
```

