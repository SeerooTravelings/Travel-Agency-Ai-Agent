import json

def transform_workflow():
    # Load original json
    with open('n8n-ai-os-workflow.json', 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # 1. List of node names to remove
    to_remove = [
        "CRM Lead Manager Tool",
        "Travel Packages Search Tool",
        "Complaint Manager Tool"
    ]

    # Filter out removed nodes
    workflow['nodes'] = [n for n in workflow['nodes'] if n['name'] not in to_remove]

    # 2. Add or Update system prompts for the 8 Specialized AI Agents (RAG FAQ and Complaint are also agents)
    agent_updates = {
        "Umrah AI Agent": {
            "system": "You are Zain, a warm senior travel consultant at Seeroo Travels. Speak Roman Urdu and English. Guide the user and qualify: 1) Month of travel, 2) Number of persons, 3) Departure city, 4) Budget. Ask one detail at a time with empathy. Active Packages: 1) Premium Gold: 350,000 PKR, 15 Days (5-Star Hotels in Makkah/Madinah, private luxury transport), 2) Economy Silver: 260,000 PKR, 15 Days (3-Star Hotels, shared shuttle transport). Respond ONLY in JSON matching this schema: {\"response\": \"string\", \"complete\": boolean, \"activeAgent\": \"Umrah\", \"data\": {\"month\": \"string/null\", \"persons\": number/null, \"city\": \"string/null\", \"budget\": \"string/null\"}}.",
            "pos": [4300, 3100]
        },
        "Hajj AI Agent": {
            "system": "You are Farhan, a dedicated Hajj Coordinator at Seeroo Travels. Speak Roman Urdu and English. Guide the user and qualify: 1) Scheme Type (Government or Private), 2) Number of passengers, 3) Budget. Keep a respectful and spiritual tone. Active Packages: 1) Government Hajj Scheme: ~1,200,000 PKR, 2) Private Hajj Scheme: ~1,800,000 PKR. Respond ONLY in JSON matching this schema: {\"response\": \"string\", \"complete\": boolean, \"activeAgent\": \"Hajj\", \"data\": {\"scheme\": \"string/null\", \"persons\": number/null, \"budget\": \"string/null\"}}.",
            "pos": [4300, 3300]
        },
        "Visa AI Agent": {
            "system": "You are Aisha, a Visa Consultant at Seeroo Travels. Speak Roman Urdu and English. Guide the user and qualify: 1) Purpose of visa, 2) Passport country, 3) Planned travel date. Respond ONLY in JSON matching this schema: {\"response\": \"string\", \"complete\": boolean, \"activeAgent\": \"Visa\", \"data\": {\"purpose\": \"string/null\", \"passport_country\": \"string/null\", \"travel_date\": \"string/null\"}}.",
            "pos": [4300, 3500]
        },
        "Tours AI Agent": {
            "system": "You are Bilal, an International Tours Planner at Seeroo Travels. Speak Roman Urdu and English. Guide the user and qualify: 1) Destination, 2) Traveler type (family/couple/solo), 3) Duration of stay, 4) Budget. Active Packages: 1) Thailand Escape Tour: 180,000 PKR, 7 Days (Bangkok & Phuket hotels + sightseeing). Respond ONLY in JSON matching this schema: {\"response\": \"string\", \"complete\": boolean, \"activeAgent\": \"Tours\", \"data\": {\"destination\": \"string/null\", \"traveler_type\": \"string/null\", \"duration_days\": number/null, \"budget\": \"string/null\"}}.",
            "pos": [4300, 3700]
        },
        "Flights AI Agent": {
            "system": "You are Saad, a Flight Booking Agent at Seeroo Travels. Speak Roman Urdu and English. Guide the user and qualify: 1) Departure city, 2) Destination, 3) Travel dates, 4) Number of passengers. Respond ONLY in JSON matching this schema: {\"response\": \"string\", \"complete\": boolean, \"activeAgent\": \"Flights\", \"data\": {\"departure\": \"string/null\", \"destination\": \"string/null\", \"dates\": \"string/null\", \"passengers\": number/null}}.",
            "pos": [4700, 3100]
        },
        "Hotels AI Agent": {
            "system": "You are Hamza, a Hotel Coordinator at Seeroo Travels. Speak Roman Urdu and English. Guide the user and qualify: 1) Check-in/Check-out dates, 2) Number of guests, 3) Distance from Haram (Makkah/Madinah), 4) Budget. Respond ONLY in JSON matching this schema: {\"response\": \"string\", \"complete\": boolean, \"activeAgent\": \"Hotels\", \"data\": {\"check_in\": \"string/null\", \"check_out\": \"string/null\", \"guests\": number/null, \"haram_distance\": \"string/null\", \"budget\": \"string/null\"}}.",
            "pos": [4700, 3300]
        },
        "RAG FAQ Agent": {
            "system": "You are Hassan, the general customer service assistant at Seeroo Travels. Speak Roman Urdu and English. Answer the user's general questions about rules, timings, documents, or travel advice. Respond ONLY in JSON matching this schema: {\"response\": \"string\", \"complete\": false, \"activeAgent\": \"FAQ\", \"data\": {}}.",
            "pos": [4700, 3500]
        },
        "Complaint & Support Agent": {
            "system": "You are Zainab, a Support Executive at Seeroo Travels. Speak Roman Urdu and English. Listen to the user's issue with empathy, apologize for the inconvenience, and qualify: 1) Complaint Category (Hotel/Transport/Guide/Visa/Other), 2) Issue Description. Tell them a ticket is created. Respond ONLY in JSON matching this schema: {\"response\": \"string\", \"complete\": true, \"activeAgent\": \"Complaint\", \"data\": {\"category\": \"string/null\", \"description\": \"string/null\"}}.",
            "pos": [4700, 3700]
        }
    }

    # Update system message for existing agent nodes
    for node in workflow['nodes']:
        if node['name'] in agent_updates:
            node['parameters'] = {
                "options": {
                    "systemMessage": agent_updates[node['name']]["system"]
                }
            }
            node['position'] = agent_updates[node['name']]["pos"]

    # 3. Create and add new nodes
    new_nodes = [
        {
            "parameters": {
                "jsCode": """// Parse the JSON string emitted by the AI Agent node
const rawText = $json.output || $json.text || '';
let parsed;
try {
  parsed = JSON.parse(rawText);
} catch (e) {
  // Regex to extract JSON block in case LLM wrapped it in conversational text
  const jsonMatch = rawText.match(/\\{[\\s\\S]*\\}/);
  if (jsonMatch) {
    try {
      parsed = JSON.parse(jsonMatch[0]);
    } catch (innerE) {
      parsed = { response: rawText, complete: false, activeAgent: 'FAQ', data: {} };
    }
  } else {
    parsed = { response: rawText, complete: false, activeAgent: 'FAQ', data: {} };
  }
}

// Ensure default structure
parsed.response = parsed.response || rawText;
parsed.complete = !!parsed.complete;
parsed.activeAgent = parsed.activeAgent || 'FAQ';
parsed.data = parsed.data || {};

return [{
  json: {
    phone: $('Parse Incoming Details').item.json.phone,
    senderName: $('Parse Incoming Details').item.json.senderName,
    text: parsed.response,
    complete: parsed.complete,
    activeAgent: parsed.activeAgent,
    data: parsed.data
  }
}];"""
            },
            "id": "parse-agent-response-id",
            "name": "Parse Agent Response",
            "type": "n8n-nodes-base.code",
            "typeVersion": 1,
            "position": [5100, 3400]
        },
        {
            "parameters": {
                "operation": "appendOrUpdate",
                "documentId": {
                    "__rl": True,
                    "value": "1pfj3q2kutmk8AgqacsKzu3BA-RPwyq_XEGs82dpa4AY",
                    "mode": "list",
                    "cachedResultName": "Untitled spreadsheet",
                    "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1pfj3q2kutmk8AgqacsKzu3BA-RPwyq_XEGs82dpa4AY/edit?usp=drivesdk"
                },
                "sheetName": {
                    "__rl": True,
                    "value": 1334942982,
                    "mode": "list",
                    "cachedResultName": "Leads",
                    "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1pfj3q2kutmk8AgqacsKzu3BA-RPwyq_XEGs82dpa4AY/edit#gid=1334942982"
                },
                "keyRow": "SenderPhone",
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "SenderPhone": "={{ $json.phone }}",
                        "SenderName": "={{ $json.senderName }}",
                        "Status": "={{ $json.complete ? 'Qualified' : 'Qualifying' }}",
                        "ServiceType": "={{ $json.activeAgent }}",
                        "Month": "={{ $json.data.month || undefined }}",
                        "Persons": "={{ $json.data.persons || undefined }}",
                        "DepartureCity": "={{ $json.data.city || undefined }}",
                        "Budget": "={{ $json.data.budget || undefined }}",
                        "VisaPurpose": "={{ $json.data.purpose || undefined }}",
                        "TravelDates": "={{ $json.data.dates || $json.data.travel_date || undefined }}",
                        "SchemeType": "={{ $json.data.scheme || undefined }}",
                        "ActiveAgent": "={{ $json.activeAgent }}",
                        "BotActive": "={{ $json.activeAgent === 'Complaint' ? 'FALSE' : 'TRUE' }}",
                        "CreatedTime": "={{ $('Lookup Customer Session').item.json.CreatedTime || new Date().toISOString() }}"
                    }
                },
                "options": {}
            },
            "id": "save-lead-to-sheets-id",
            "name": "Save Lead to Sheets",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 3,
            "position": [5350, 3400],
            "credentials": {
                "googleSheetsOAuth2Api": {
                    "id": "pHgrDDWKgv0xidHW",
                    "name": "Google Sheets OAuth2 API"
                }
            }
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{ $json.activeAgent }}",
                            "value2": "Complaint"
                        }
                    ]
                }
            },
            "id": "check-if-complaint-id",
            "name": "Check If Complaint",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [5600, 3400]
        },
        {
            "parameters": {
                "operation": "append",
                "documentId": {
                    "__rl": True,
                    "value": "1pfj3q2kutmk8AgqacsKzu3BA-RPwyq_XEGs82dpa4AY",
                    "mode": "list",
                    "cachedResultName": "Untitled spreadsheet",
                    "cachedResultUrl": "https://docs.google.com/spreadsheets/d/1pfj3q2kutmk8AgqacsKzu3BA-RPwyq_XEGs82dpa4AY/edit?usp=drivesdk"
                },
                "sheetName": {
                    "__rl": True,
                    "value": "SupportTickets",
                    "mode": "name"
                },
                "columns": {
                    "mappingMode": "defineBelow",
                    "value": {
                        "TicketID": "={{ 'TCK-' + Math.floor(1000 + Math.random() * 9000) }}",
                        "Phone": "={{ $json.phone }}",
                        "Category": "={{ $json.data.category || 'Other' }}",
                        "Description": "={{ $json.data.description || 'No description provided' }}",
                        "Status": "Open",
                        "AssignedAgent": "Zainab",
                        "CreatedTime": "={{ new Date().toISOString() }}"
                    }
                },
                "options": {}
            },
            "id": "create-support-ticket-id",
            "name": "Create Support Ticket",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 3,
            "position": [5850, 3200],
            "credentials": {
                "googleSheetsOAuth2Api": {
                    "id": "pHgrDDWKgv0xidHW",
                    "name": "Google Sheets OAuth2 API"
                }
            }
        }
    ]

    workflow['nodes'].extend(new_nodes)

    # 4. Define and rebuild connections
    connections = {}

    # Helper function to add main connection
    def add_conn(source, target, port="main", src_idx=0, tgt_idx=0):
        if source not in connections:
            connections[source] = {}
        if port not in connections[source]:
            connections[source][port] = []
        while len(connections[source][port]) <= src_idx:
            connections[source][port].append([])
        connections[source][port][src_idx].append({
            "node": target,
            "type": port,
            "index": tgt_idx
        })

    # Core system flow connections
    add_conn("WhatsApp Webhook", "Parse Incoming Details")
    add_conn("Parse Incoming Details", "Lookup Customer Session")
    add_conn("Lookup Customer Session", "Is Bot Paused?")
    
    # Is Bot Paused? (Output 0 is True = do nothing. Output 1 is False = run Route by Session State)
    add_conn("Is Bot Paused?", "Route by Session State", src_idx=1)

    # Route by Session State
    add_conn("Route by Session State", "Umrah AI Agent", src_idx=0)
    add_conn("Route by Session State", "Hajj AI Agent", src_idx=1)
    add_conn("Route by Session State", "Visa AI Agent", src_idx=2)
    add_conn("Route by Session State", "Route by Session State1", src_idx=3)

    # Route by Session State1
    add_conn("Route by Session State1", "Tours AI Agent", src_idx=0)
    add_conn("Route by Session State1", "Flights AI Agent", src_idx=1)
    add_conn("Route by Session State1", "Hotels AI Agent", src_idx=2)
    add_conn("Route by Session State1", "LLM Intent Classifier", src_idx=3)

    # Classifier
    add_conn("LLM Intent Classifier", "Parse Intent Response")
    add_conn("Parse Intent Response", "Route by Intent")

    # Route by Intent (10 outputs)
    add_conn("Route by Intent", "Umrah AI Agent", src_idx=0)
    add_conn("Route by Intent", "Hajj AI Agent", src_idx=1)
    add_conn("Route by Intent", "Visa AI Agent", src_idx=2)
    add_conn("Route by Intent", "Tours AI Agent", src_idx=3)
    add_conn("Route by Intent", "Flights AI Agent", src_idx=4)
    add_conn("Route by Intent", "Hotels AI Agent", src_idx=5)
    add_conn("Route by Intent", "RAG FAQ Agent", src_idx=6)
    add_conn("Route by Intent", "Complaint & Support Agent", src_idx=7)
    add_conn("Route by Intent", "Payment Details Response", src_idx=8)
    add_conn("Route by Intent", "RAG FAQ Agent", src_idx=9)

    # Payment details response connects directly to WhatsApp Send
    add_conn("Payment Details Response", "Send WhatsApp Response")

    # Connect Model and Memory sub-nodes to the 8 Agents
    agents_list = [
        "Umrah AI Agent", "Hajj AI Agent", "Visa AI Agent", "Tours AI Agent",
        "Flights AI Agent", "Hotels AI Agent", "RAG FAQ Agent", "Complaint & Support Agent"
    ]
    for agent in agents_list:
        # Groq model connection
        add_conn("Groq Chat Model", agent, port="ai_language_model")
        # Memory connection
        add_conn("Window Buffer Memory", agent, port="ai_memory")
        # Agent outputs to Parser
        add_conn(agent, "Parse Agent Response")

    # Downstream Parser and Sheets flow
    add_conn("Parse Agent Response", "Save Lead to Sheets")
    add_conn("Save Lead to Sheets", "Check If Complaint")
    
    # Check If Complaint (Output 0 is True = create support ticket. Output 1 is False = check if qualified)
    add_conn("Check If Complaint", "Create Support Ticket", src_idx=0)
    add_conn("Check If Complaint", "Is Lead Qualified?", src_idx=1)

    # Create Support Ticket goes directly to Send WhatsApp Response
    add_conn("Create Support Ticket", "Send WhatsApp Response")

    # Is Lead Qualified? (Output 0 is True = Send Sales Alert. Output 1 is False = Send WhatsApp Response)
    add_conn("Is Lead Qualified?", "Sales Group WhatsApp Alert", src_idx=0)
    add_conn("Is Lead Qualified?", "Send WhatsApp Response", src_idx=1)

    # Sales Group WhatsApp Alert goes to Send WhatsApp Response
    add_conn("Sales Group WhatsApp Alert", "Send WhatsApp Response")

    workflow['connections'] = connections

    # Save output
    with open('n8n-ai-os-workflow.json', 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2)

    print("Workflow JSON successfully transformed into a tool-free Multi-Agent state machine!")

if __name__ == '__main__':
    transform_workflow()
