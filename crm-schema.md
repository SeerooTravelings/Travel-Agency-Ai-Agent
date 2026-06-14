# Google Sheets CRM Database Design

This document details the Google Sheets configuration for the Travel Agency AI Operating System (AI OS). To implement this system, create a Google Spreadsheet and add the following 4 tabs (sheets): **Leads**, **Packages**, **SupportTickets**, and **Payments**.

> [!TIP]
> **Auto Setup script:**
> You can automatically generate all tabs, headers, professional colors, and column dropdown validations by running the [setup-sheets.gs](file:///c:/Users/Khalil%20Ahmad/OneDrive/Desktop/ai%20agent/setup-sheets.gs) Apps Script directly in your spreadsheet editor (Extensions -> Apps Script).

---

## 1. Leads Table (Core Table)
Tracks the customer interaction, status, and details gathered during the qualification flows.

| Field Name | Data Type | Description | Example Values |
|---|---|---|---|
| `LeadID` | String (UUID / Autonumber) | Unique identifier for each lead. | `LID-10042` |
| `SenderPhone` | String | Customer's WhatsApp phone number. | `923001234567` |
| `SenderName` | String | WhatsApp Profile name or parsed full name. | `Ali Khan` |
| `Status` | Enum / String | Current state of the lead in sales pipeline. | `New`, `Qualifying`, `Qualified`, `Handoff`, `Lost` |
| `ServiceType` | Enum / String | The travel service they are interested in. | `Umrah`, `Hajj`, `Visa`, `Tours`, `Flights`, `Hotels` |
| `Month` | String | Travel Month requested. | `September`, `December` |
| `Persons` | Integer | Total number of passengers/pilgrims. | `4` |
| `DepartureCity` | String | City from which travel starts. | `Karachi`, `Lahore` |
| `Budget` | String / Numeric | Total budget or budget per person. | `300000` |
| `VisaPurpose` | String | Purpose of travel (Visa flow only). | `Tourism`, `Business` |
| `TravelDates` | String | Range of travel dates. | `2026-09-10 to 2026-09-25` |
| `Duration` | Integer | Days of stay (Tours/Hotels). | `15` |
| `SchemeType` | String | Hajj scheme choice (Hajj flow only). | `Government`, `Private` |
| `FollowUpCount` | Integer | Number of follow-ups sent. | `1` |
| `LastFollowUpTime`| DateTime | Timestamp of last sent follow-up. | `2026-06-15T09:00:00Z` |
| `ActiveAgent` | String / Enum | Currently active sub-agent for multi-turn chat. | `Umrah`, `Hajj`, `None` |
| `BotActive` | Boolean / Enum | If FALSE, the bot is paused for human handoff. | `TRUE`, `FALSE` |
| `CreatedTime` | DateTime | Timestamp when lead was first captured. | `2026-06-14T13:30:00Z` |

---

## 2. Packages Table
Used for package matching against qualification responses.

| Field Name | Data Type | Description | Example Values |
|---|---|---|---|
| `PackageID` | String | Unique package identifier. | `PKG-UMR-001` |
| `Category` | Enum | The category of package. | `Umrah`, `Hajj`, `International` |
| `PackageName` | String | The official name of the package. | `Premium Umrah Gold Package` |
| `Duration` | String | Total duration. | `15 Days` |
| `Price` | Numeric | Cost per person. | `280000` |
| `Currency` | String | Pricing currency. | `PKR`, `AED`, `USD` |
| `Details` | Text / Markdown | Package details, hotels, and highlights. | `5-Star Hotel in Makkah, Transport included` |
| `Status` | Enum | Status of package. | `Active`, `Inactive` |

---

## 3. Support Tickets Table
Created when the intent is classified as `complaint`.

| Field Name | Data Type | Description | Example Values |
|---|---|---|---|
| `TicketID` | String | Unique ticket ID. | `TCK-8821` |
| `Phone` | String | Customer's WhatsApp phone number. | `923001234567` |
| `Category` | Enum | The issue classification. | `Hotel`, `Transport`, `Guide`, `Visa`, `Other` |
| `Description` | Text | The feedback or complaint text. | `Hotel room ac was not working in Makkah` |
| `Status` | Enum | Ticket state. | `Open`, `In-Progress`, `Resolved` |
| `AssignedAgent`| String | Human support representative name. | `Zainab` |
| `CreatedTime` | DateTime | Timestamp when ticket was raised. | `2026-06-14T13:34:00Z` |

---

## 4. Payments Table
Handles payment transactions and receipt verifications.

| Field Name | Data Type | Description | Example Values |
|---|---|---|---|
| `PaymentID` | String | Transaction identifier. | `TXN-998273` |
| `LeadID` | String | Associated Lead ID. | `LID-10042` |
| `Amount` | Numeric | Total amount paid. | `150000` |
| `Method` | Enum | Payment channel. | `Bank Transfer`, `EasyPaisa`, `JazzCash` |
| `ProofUrl` | String | Link to uploaded transaction receipt image.| `http://s3.aws/receipts/img.jpg` |
| `Verification` | Enum | Finance validation status. | `Pending`, `Verified`, `Rejected` |
