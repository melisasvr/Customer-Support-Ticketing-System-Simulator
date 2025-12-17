# 🎫 Customer Support Ticketing System Simulator
- A multi-agent customer support system built with **LangGraph** and **Python** that automatically classifies, routes, and resolves customer support tickets using specialized agents.

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Visual Dashboard](#visual-dashboard)
- [Output Files](#output-files)
- [Customization](#customization)
- [Technologies Used](#technologies-used)

## ✨ Features

### Core Functionality
- **Intent Classification**: Automatically categorizes tickets into billing, tech support, returns, order status, or general inquiries
- **Multi-Agent System**: Specialized agents handle different types of queries
- **Smart Routing**: Conditional routing based on ticket intent
- **Sentiment Analysis**: Rule-based quality scoring for responses
- **Escalation Logic**: Automatically escalates low-quality or high-priority tickets to human review
- **State Management**: Complete ticket lifecycle tracking using LangGraph

### Additional Features
- **8 Sample Customers**: Pre-configured customer database with different tiers
- **Template-Based Responses**: Professional, context-aware responses without API costs
- **Automatic File Saving**: Saves individual tickets, summaries, and JSON data
- **Interactive Dashboard**: Beautiful HTML visualization of all tickets
- **No API Required**: Runs 100% offline without any external API calls

## 🏗️ Architecture

```
Customer Query
     ↓
Intent Classifier
     ↓
┌────────────────────────────────┐
│  Conditional Router            │
├────────────────────────────────┤
│  → Billing Agent               │
│  → Tech Support Agent          │
│  → Returns Agent               │
│  → General Agent               │
└────────────────────────────────┘
     ↓
Sentiment Checker
     ↓
┌────────────────────────────────┐
│  Escalation Decision           │
├────────────────────────────────┤
│  → Human Review (if needed)    │
│  → Auto-Approve & Send         │
└────────────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone or Download
```bash
# Create project directory
mkdir customer-support-system
cd customer-support-system
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install langgraph
```

- That's it! No API keys required.

## 🚀 Usage

### Running the System

1. **Run the ticket processor:**
```bash
python support_system.py
```

2. **Open the dashboard:**
   - Open `index.html` in your web browser
   - View real-time statistics and ticket details
   - Use filters to explore different ticket types

### Expected Output

When you run the script, you'll see:
- Live processing of 8 customer tickets
- Intent classification and routing decisions
- Resolution flow for each ticket
- Final responses generated
- Summary statistics
- Confirmation that files have been saved

## 📁 Project Structure

```
customer-support-system/
│
├── support_system.py      # Main Python application
├── index.html             # Interactive dashboard
├── README.md              # This file
│
└── ticket_results/        # Auto-generated folder
    ├── TKT12345_timestamp.txt       # Individual ticket reports
    ├── TKT12346_timestamp.txt
    ├── ...
    ├── SUMMARY_timestamp.txt        # Summary report
    └── tickets_data_timestamp.json  # JSON data for dashboard
```

## 🔧 How It Works

### 1. Intent Classification
- The system analyzes customer queries using keyword matching to classify into:
- **Returns**: Refund, return, wrong item
- **Billing**: Charges, fees, payment issues
- **Tech Support**: Bugs, errors, not working
- **Order Status**: Tracking, delivery questions
- **General**: Everything else

### 2. Specialized Agents
- Each agent has access to:
- **Customer Database**: Name, tier (premium/standard), account balance
- **Order Database**: Order status, items, dates
- **Policy Retrieval**: Return policy, billing policy, tech support policy
- **Tech Solutions Database**: Common troubleshooting steps

### 3. Response Generation
- Agents generate responses based on:
- Customer tier (premium customers get better terms)
- Account status (balance, order history)
- Relevant policies
- Context-appropriate tone

### 4. Quality Control
- The sentiment checker analyzes:
- **Query Sentiment**: How negative/urgent is the customer?
- **Response Quality**: Does it include apologies, solutions, timelines?

**Escalation Rules:**
- Quality score < 0.6 → Escalate
- High priority + quality score < 0.8 → Escalate
- Otherwise → Auto-approve

## 📊 Visual Dashboard
- The HTML dashboard provides:

### Statistics
- Total tickets processed
- Escalated vs. auto-resolved counts
- Average quality score

### Charts
- Intent distribution (doughnut chart)
- Priority breakdown (bar chart)

### Features
- **Real-time filtering**: Filter by intent, priority, or status
- **Detailed ticket cards**: See full query, resolution flow, and response
- **Color-coded badges**: Easy visual identification
- **Quality indicators**: Traffic light system for scores
- **Responsive design**: Works on desktop and mobile

## 📄 Output Files

### Individual Ticket Reports (.txt)
- Each ticket gets its own detailed report with:
- Customer information
- Query and classification
- Complete resolution flow
- Final response
- Quality metrics

### Summary Report (.txt)
- Aggregate statistics including:
- Total counts
- Intent distribution
- List of all tickets with key details

### JSON Data File (.json)
- Machine-readable format with all ticket data, perfect for:
- Loading into the dashboard
- Data analysis
- Integration with other systems

## 🎨 Customization

### Adding New Customers
Edit the `FakeDatabase.__init__()` method:
```python
self.customers = {
    "CUST009": {"name": "Your Name", "tier": "premium", "balance": 0.0},
    # Add more customers...
}
```

### Adding New Queries
Edit the `SAMPLE_QUERIES` list:
```python
SAMPLE_QUERIES = [
    {
        "customer_id": "CUST009",
        "query": "Your custom query here",
    },
    # Add more queries...
]
```

### Modifying Response Templates
Edit the `ResponseTemplates` class methods:
- `generate_billing_response()`
- `generate_tech_response()`
- `generate_returns_response()`
- `generate_general_response()`

### Adjusting Escalation Rules
Modify the `sentiment_checker()` function:
```python
# Current logic:
if response_quality < 0.6 or (state["priority"] == "high" and response_quality < 0.8):
    state["escalated"] = True
```

### Adding New Intent Types
1. Add keywords to `classify_intent()`
2. Create new agent function
3. Add routing in `route_to_agent()`
4. Update the graph in `create_support_graph()`

## 🛠️ Technologies Used

- **Python 3.8+**: Core programming language
- **LangGraph**: State machine and workflow orchestration
- **Chart.js**: Interactive charts in dashboard
- **HTML/CSS/JavaScript**: Visual dashboard interface

## 📈 Future Enhancements

- Potential improvements:
- Integration with real LLM APIs (Claude, GPT-4)
- Database persistence (SQLite, PostgreSQL)
- Email notification system
- Real-time WebSocket updates
- Machine learning for intent classification
- Multi-language support
- Customer satisfaction surveys
- Performance metrics tracking

## 🤝 Contributing

- Feel free to fork this project and submit pull requests with improvements!

## 📝 License

- This project is open source and available for educational purposes.

## 💡 Tips
- Run the system multiple times to see different ticket IDs
- Check the `ticket_results/` folder after each run
- Use the dashboard filters to analyze specific ticket types
- Modify templates to match your company's tone
- Add more customers and queries to test edge cases

## 🐛 Troubleshooting
**Issue**: Script won't run
- **Solution**: Make sure LangGraph is installed: `pip install langgraph`

**Issue**: Dashboard shows sample data only
- **Solution**: The dashboard currently uses built-in sample data. To load JSON files, you'd need to add file reading functionality

**Issue**: No ticket_results folder created
- **Solution**: The folder is created automatically when you run the script

**Issue**: Tickets not escalating
- **Solution**: This is normal! The template responses are high quality. To see escalations, modify responses to have lower quality or create more negative queries

## 📞 Support
- For questions or issues, please review the code comments or create an issue in the project repository.

---

**Built with ❤️ using LangGraph and Python**

