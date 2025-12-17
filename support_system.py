"""
Customer Support Ticketing System Simulator (NO API VERSION)
Uses LangGraph for multi-agent orchestration without external API calls
All responses are generated using template-based rules
"""

from typing import TypedDict, Literal
import random
from datetime import datetime, timedelta
import os
import json

# Install required packages:
# pip install langgraph

from langgraph.graph import StateGraph, END


# ============= STATE DEFINITION =============
class TicketState(TypedDict):
    """State that gets passed through the graph"""
    ticket_id: str
    customer_id: str
    query: str
    intent: str
    priority: str
    agent_response: str
    sentiment_score: float
    escalated: bool
    resolution_notes: list[str]
    final_response: str


# ============= FAKE DATABASE =============
class FakeDatabase:
    """Simulates customer and order database"""
    
    def __init__(self):
        self.customers = {
            "CUST001": {"name": "Alice Johnson", "tier": "premium", "balance": -45.99},
            "CUST002": {"name": "Bob Smith", "tier": "standard", "balance": 0.0},
            "CUST003": {"name": "Carol White", "tier": "premium", "balance": 150.00},
            "CUST004": {"name": "David Brown", "tier": "standard", "balance": -120.50},
            "CUST005": {"name": "Emma Davis", "tier": "premium", "balance": 25.00},
            "CUST006": {"name": "Frank Miller", "tier": "standard", "balance": -75.00},
            "CUST007": {"name": "Grace Wilson", "tier": "premium", "balance": 0.0},
            "CUST008": {"name": "Henry Taylor", "tier": "standard", "balance": -200.00},
        }
        
        self.orders = {
            "ORD12345": {"customer": "CUST001", "status": "delivered", "item": "Laptop", "date": "2024-11-15"},
            "ORD12346": {"customer": "CUST002", "status": "in_transit", "item": "Headphones", "date": "2024-12-10"},
            "ORD12347": {"customer": "CUST003", "status": "delivered", "item": "Keyboard", "date": "2024-12-01"},
            "ORD12348": {"customer": "CUST005", "status": "processing", "item": "Monitor", "date": "2024-12-15"},
            "ORD12349": {"customer": "CUST006", "status": "delivered", "item": "Mouse", "date": "2024-11-20"},
            "ORD12350": {"customer": "CUST007", "status": "in_transit", "item": "Webcam", "date": "2024-12-12"},
            "ORD12351": {"customer": "CUST008", "status": "delivered", "item": "Speakers", "date": "2024-11-10"},
        }
        
        self.tech_issues = {
            "wifi": "Restart router, check if other devices connect, verify password",
            "app": "Clear cache, update app to latest version, reinstall if needed",
            "slow": "Close background apps, check storage space, restart device",
            "login": "Reset password via email, clear browser cookies, check caps lock",
        }
    
    def get_customer(self, customer_id: str) -> dict:
        return self.customers.get(customer_id, {"name": "Unknown", "tier": "standard", "balance": 0.0})
    
    def get_order(self, order_id: str) -> dict:
        return self.orders.get(order_id, {"error": "Order not found"})
    
    def get_tech_solution(self, issue_key: str) -> str:
        return self.tech_issues.get(issue_key, "Please contact advanced technical support")


# ============= POLICY RETRIEVAL =============
class PolicyRetriever:
    """Simulates policy document retrieval"""
    
    def __init__(self):
        self.policies = {
            "return_policy": {
                "window": "30 days",
                "conditions": "unused and in original packaging",
                "refund_time": "5-7 business days",
                "premium_shipping": "free",
                "standard_shipping": "$5.99"
            },
            "billing_policy": {
                "due_days": 15,
                "initial_late_fee": 10,
                "recurring_late_fee": 5,
                "payment_plan_threshold": 100
            },
            "tech_support_policy": {
                "premium_response": "2 hours",
                "standard_response": "24 hours"
            }
        }
    
    def get_policy(self, policy_type: str) -> dict:
        return self.policies.get(policy_type, {})


# ============= RESPONSE TEMPLATES =============
class ResponseTemplates:
    """Template-based response generator"""
    
    @staticmethod
    def generate_billing_response(customer: dict, policy: dict, query: str) -> str:
        name = customer.get('name', 'Valued Customer')
        tier = customer.get('tier', 'standard')
        balance = customer.get('balance', 0.0)
        
        if balance < 0:
            # Customer owes money
            return f"""Dear {name},

Thank you for contacting us regarding your billing concern.

**Current Account Status:**
- Account Balance: ${abs(balance):.2f} (amount owed)
- Account Tier: {tier.capitalize()}

I understand you have questions about the charges on your account. Let me provide some clarity:

**Our Billing Policy:**
- Payment is due within {policy.get('due_days', 15)} days of invoice
- Initial late fee: ${policy.get('initial_late_fee', 10)} after the due date
- Additional fees: ${policy.get('recurring_late_fee', 5)} per week thereafter

**Available Options:**
1. Make a one-time payment to clear your balance
2. Set up a payment plan (available for balances over ${policy.get('payment_plan_threshold', 100)})
3. Contact us to discuss your specific situation

If you believe there has been an error, please provide:
- Date of your payment
- Payment confirmation number
- Any relevant documentation

We're here to help resolve this fairly and quickly.

Best regards,
Billing Support Team"""
        else:
            return f"""Dear {name},

Thank you for reaching out about your billing.

**Current Account Status:**
- Account Balance: ${balance:.2f} (credit)
- Account Tier: {tier.capitalize()}

Your account is in good standing! Is there a specific billing question I can help you with?

Best regards,
Billing Support Team"""
    
    @staticmethod
    def generate_tech_response(customer: dict, tech_solution: str, query: str) -> str:
        name = customer.get('name', 'Valued Customer')
        tier = customer.get('tier', 'standard')
        policy = PolicyRetriever().get_policy("tech_support_policy")
        
        return f"""Hi {name},

I'd be happy to help you resolve your technical issue! As a {tier} member, you have access to our technical support with {policy.get(f'{tier}_response', '24 hours')} response time.

**Troubleshooting Steps:**

{tech_solution}

**Additional Recommendations:**
- Ensure your device/app is updated to the latest version
- Check your internet connection if the issue is online
- Restart your device after making changes

**Next Steps:**
Please try these troubleshooting steps and let us know if the issue persists. If you continue to experience problems:
- Reply to this email with details of what you've tried
- Include any error messages you're seeing
- Our team will prioritize your case

We're committed to getting you back up and running quickly!

Best regards,
Technical Support Team"""
    
    @staticmethod
    def generate_returns_response(customer: dict, policy: dict, query: str) -> str:
        name = customer.get('name', 'Valued Customer')
        tier = customer.get('tier', 'standard')
        shipping_cost = policy.get(f'{tier}_shipping', '$5.99')
        
        return f"""Dear {name},

I sincerely apologize for any issues with your order. I'm here to help you with the return process.

**Return Policy:**
- Return window: {policy.get('window', '30 days')} from delivery
- Condition required: {policy.get('conditions', 'unused in original packaging')}
- Refund processing: {policy.get('refund_time', '5-7 business days')}
- Return shipping: {shipping_cost} for {tier} members

**How to Return Your Item:**

1. **Initiate Return:** We'll email you a return authorization within 24 hours
2. **Pack the Item:** Use original packaging if possible
3. **Ship It Back:** Use the prepaid label we provide (or arrange your own shipping)
4. **Get Your Refund:** Once we receive and inspect the item, your refund will be processed

**What We Need From You:**
- Order number (if available)
- Reason for return
- Photos of the item (if damaged or incorrect)

I've flagged your case for priority processing. You should receive your return instructions within 24 hours.

We value your business and want to make this right.

Best regards,
Returns Department"""
    
    @staticmethod
    def generate_general_response(customer: dict, order_info: dict = None, query: str = "") -> str:
        name = customer.get('name', 'Valued Customer')
        
        if order_info and "error" not in order_info:
            status = order_info.get('status', 'unknown')
            item = order_info.get('item', 'your item')
            date = order_info.get('date', 'recently')
            
            status_messages = {
                "delivered": f"Great news! Your {item} was delivered. If you haven't received it, please check with your building management or neighbors.",
                "in_transit": f"Your {item} is currently on its way to you! Expected delivery is within 2-3 business days.",
                "processing": f"Your {item} order is being prepared for shipment. It should ship within 1-2 business days.",
            }
            
            return f"""Hi {name},

Thank you for reaching out about your order!

**Order Details:**
- Item: {item}
- Order Date: {date}
- Status: {status.replace('_', ' ').title()}

{status_messages.get(status, 'Your order is being processed.')}

**Tracking Information:**
You'll receive email updates at each stage:
- Order confirmation (sent)
- Shipment notification (with tracking number)
- Delivery confirmation

If you have any concerns or don't receive your order within the expected timeframe, please don't hesitate to contact us again.

Is there anything else I can help you with?

Best regards,
Customer Support Team"""
        else:
            return f"""Hi {name},

Thank you for contacting us!

I'm here to help with your inquiry. To provide you with the most accurate information, could you please provide:
- Your order number (if this is order-related)
- A brief description of what you need assistance with
- Any relevant dates or details

Our team is committed to resolving your concern as quickly as possible.

Best regards,
Customer Support Team"""


# ============= SENTIMENT ANALYZER =============
class SentimentAnalyzer:
    """Rule-based sentiment analysis"""
    
    @staticmethod
    def analyze_query(query: str) -> float:
        """Analyze customer query sentiment (0.0 = very negative, 1.0 = very positive)"""
        query_lower = query.lower()
        
        # Negative indicators
        negative_words = ["terrible", "awful", "horrible", "angry", "furious", "ridiculous", 
                         "unacceptable", "disgusted", "worst", "never", "hate"]
        # Positive indicators
        positive_words = ["thanks", "thank you", "please", "appreciate", "grateful", "good"]
        # Urgency indicators
        urgent_words = ["immediately", "urgent", "asap", "now", "emergency"]
        
        neg_count = sum(1 for word in negative_words if word in query_lower)
        pos_count = sum(1 for word in positive_words if word in query_lower)
        urgent_count = sum(1 for word in urgent_words if word in query_lower)
        
        # Base sentiment
        base_score = 0.7
        
        # Adjust for negative/positive words
        sentiment = base_score - (neg_count * 0.15) + (pos_count * 0.1) - (urgent_count * 0.1)
        
        # Clamp between 0 and 1
        return max(0.0, min(1.0, sentiment))
    
    @staticmethod
    def analyze_response(response: str, query_sentiment: float) -> float:
        """Analyze response quality based on response content and query sentiment"""
        response_lower = response.lower()
        
        # Quality indicators
        has_apology = any(word in response_lower for word in ["apology", "apologize", "sorry"])
        has_solution = any(word in response_lower for word in ["steps", "process", "how to", "options"])
        has_timeline = any(word in response_lower for word in ["within", "days", "hours", "shortly"])
        is_polite = any(word in response_lower for word in ["please", "thank you", "appreciate"])
        
        base_quality = 0.75
        
        if has_apology and query_sentiment < 0.6:
            base_quality += 0.1
        if has_solution:
            base_quality += 0.1
        if has_timeline:
            base_quality += 0.05
        if is_polite:
            base_quality += 0.05
        
        return min(1.0, base_quality)


# ============= INITIALIZE TOOLS =============
db = FakeDatabase()
policy_retriever = PolicyRetriever()
response_generator = ResponseTemplates()
sentiment_analyzer = SentimentAnalyzer()


# ============= SAMPLE QUERIES =============
SAMPLE_QUERIES = [
    {
        "customer_id": "CUST001",
        "query": "I received my laptop but it's not what I ordered. I want to return it and get a refund immediately!",
    },
    {
        "customer_id": "CUST002",
        "query": "My headphones haven't arrived yet. Where is my order ORD12346?",
    },
    {
        "customer_id": "CUST004",
        "query": "Why am I being charged late fees? This is ridiculous! I paid on time!",
    },
    {
        "customer_id": "CUST003",
        "query": "My WiFi keeps disconnecting. Can you help me troubleshoot?",
    },
    {
        "customer_id": "CUST005",
        "query": "When will my monitor ship? I ordered it 2 days ago and it's still processing.",
    },
    {
        "customer_id": "CUST006",
        "query": "The mouse I received is defective. The left click doesn't work properly.",
    },
    {
        "customer_id": "CUST007",
        "query": "My app keeps crashing every time I try to log in. Please help!",
    },
    {
        "customer_id": "CUST008",
        "query": "I can't afford to pay $200 right now. Can I set up a payment plan?",
    },
]


# ============= NODE FUNCTIONS =============

def classify_intent(state: TicketState) -> TicketState:
    """Classify the intent of the customer query"""
    query = state["query"].lower()
    
    # Simple keyword-based classification
    if any(word in query for word in ["return", "refund", "send back", "wrong item"]):
        intent = "returns"
    elif any(word in query for word in ["charge", "bill", "payment", "balance", "fee"]):
        intent = "billing"
    elif any(word in query for word in ["not working", "broken", "crash", "error", "fix", "help", "troubleshoot", "wifi", "disconnect"]):
        intent = "tech_support"
    elif any(word in query for word in ["where", "status", "tracking", "order", "arrived", "delivery"]):
        intent = "order_status"
    else:
        intent = "general"
    
    # Determine priority based on sentiment and keywords
    if any(word in query for word in ["immediately", "urgent", "angry", "ridiculous", "terrible"]):
        priority = "high"
    else:
        priority = "normal"
    
    state["intent"] = intent
    state["priority"] = priority
    state["resolution_notes"].append(f"Intent classified as: {intent} (Priority: {priority})")
    
    return state


def route_to_agent(state: TicketState) -> Literal["billing_agent", "tech_agent", "returns_agent", "general_agent"]:
    """Route to appropriate specialized agent"""
    intent = state["intent"]
    
    routing = {
        "billing": "billing_agent",
        "tech_support": "tech_agent",
        "returns": "returns_agent",
        "order_status": "general_agent",
        "general": "general_agent",
    }
    
    return routing.get(intent, "general_agent")


def billing_agent(state: TicketState) -> TicketState:
    """Handle billing-related queries"""
    customer = db.get_customer(state["customer_id"])
    policy = policy_retriever.get_policy("billing_policy")
    
    response = response_generator.generate_billing_response(customer, policy, state["query"])
    
    state["agent_response"] = response
    state["resolution_notes"].append(f"Billing agent handled query. Balance: ${customer.get('balance', 0.0)}")
    
    return state


def tech_agent(state: TicketState) -> TicketState:
    """Handle technical support queries"""
    customer = db.get_customer(state["customer_id"])
    
    # Try to find relevant tech solution
    query_lower = state["query"].lower()
    tech_solution = None
    for issue_key in db.tech_issues.keys():
        if issue_key in query_lower:
            tech_solution = db.get_tech_solution(issue_key)
            break
    
    if not tech_solution:
        tech_solution = """1. Check if the issue occurs on other devices
2. Restart the device/application
3. Check for software updates
4. Contact support if the issue persists"""
    
    response = response_generator.generate_tech_response(customer, tech_solution, state["query"])
    
    state["agent_response"] = response
    state["resolution_notes"].append("Tech support agent provided troubleshooting steps")
    
    return state


def returns_agent(state: TicketState) -> TicketState:
    """Handle returns and refunds"""
    customer = db.get_customer(state["customer_id"])
    policy = policy_retriever.get_policy("return_policy")
    
    response = response_generator.generate_returns_response(customer, policy, state["query"])
    
    state["agent_response"] = response
    state["resolution_notes"].append("Returns agent initiated return process")
    
    return state


def general_agent(state: TicketState) -> TicketState:
    """Handle general queries and order status"""
    customer = db.get_customer(state["customer_id"])
    
    # Check if query mentions an order ID
    query_words = state["query"].split()
    order_info = None
    for word in query_words:
        if word.startswith("ORD"):
            order_info = db.get_order(word)
            break
    
    response = response_generator.generate_general_response(customer, order_info, state["query"])
    
    state["agent_response"] = response
    state["resolution_notes"].append("General agent handled query")
    
    return state


def sentiment_checker(state: TicketState) -> TicketState:
    """Analyze sentiment of the query and response quality"""
    
    # Analyze query sentiment
    query_sentiment = sentiment_analyzer.analyze_query(state["query"])
    
    # Analyze response quality
    response_quality = sentiment_analyzer.analyze_response(state["agent_response"], query_sentiment)
    
    state["sentiment_score"] = response_quality
    
    # Escalate if sentiment is poor or priority is high and sentiment is moderate
    if response_quality < 0.6 or (state["priority"] == "high" and response_quality < 0.8):
        state["escalated"] = True
        state["resolution_notes"].append(f"⚠️  Escalated to human review (quality score: {response_quality:.2f}, query sentiment: {query_sentiment:.2f})")
    else:
        state["escalated"] = False
        state["resolution_notes"].append(f"✓ Auto-approved (quality score: {response_quality:.2f})")
    
    return state


def should_escalate(state: TicketState) -> Literal["human_review", "finalize"]:
    """Decide whether to escalate to human review"""
    return "human_review" if state["escalated"] else "finalize"


def human_review(state: TicketState) -> TicketState:
    """Simulate human review (adds note)"""
    state["resolution_notes"].append("👤 ESCALATED: Human agent reviewing before sending")
    state["final_response"] = "[PENDING HUMAN REVIEW]\n\n" + state["agent_response"]
    return state


def finalize_response(state: TicketState) -> TicketState:
    """Finalize and approve response"""
    state["final_response"] = state["agent_response"]
    state["resolution_notes"].append("✓ Response approved and sent to customer")
    return state


# ============= BUILD GRAPH =============

def create_support_graph():
    """Create the LangGraph workflow"""
    
    workflow = StateGraph(TicketState)
    
    # Add nodes
    workflow.add_node("classify", classify_intent)
    workflow.add_node("billing_agent", billing_agent)
    workflow.add_node("tech_agent", tech_agent)
    workflow.add_node("returns_agent", returns_agent)
    workflow.add_node("general_agent", general_agent)
    workflow.add_node("sentiment_check", sentiment_checker)
    workflow.add_node("human_review", human_review)
    workflow.add_node("finalize", finalize_response)
    
    # Set entry point
    workflow.set_entry_point("classify")
    
    # Add conditional routing from classify to agents
    workflow.add_conditional_edges(
        "classify",
        route_to_agent,
        {
            "billing_agent": "billing_agent",
            "tech_agent": "tech_agent",
            "returns_agent": "returns_agent",
            "general_agent": "general_agent",
        }
    )
    
    # All agents go to sentiment check
    workflow.add_edge("billing_agent", "sentiment_check")
    workflow.add_edge("tech_agent", "sentiment_check")
    workflow.add_edge("returns_agent", "sentiment_check")
    workflow.add_edge("general_agent", "sentiment_check")
    
    # Conditional routing based on sentiment
    workflow.add_conditional_edges(
        "sentiment_check",
        should_escalate,
        {
            "human_review": "human_review",
            "finalize": "finalize",
        }
    )
    
    # Both paths end after their final node
    workflow.add_edge("human_review", END)
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# ============= MAIN EXECUTION =============

def process_ticket(query_data: dict, graph):
    """Process a single support ticket"""
    
    ticket_id = f"TKT{random.randint(10000, 99999)}"
    
    initial_state = TicketState(
        ticket_id=ticket_id,
        customer_id=query_data["customer_id"],
        query=query_data["query"],
        intent="",
        priority="",
        agent_response="",
        sentiment_score=0.0,
        escalated=False,
        resolution_notes=[],
        final_response=""
    )
    
    print(f"\n{'='*80}")
    print(f"TICKET ID: {ticket_id}")
    print(f"CUSTOMER: {query_data['customer_id']}")
    print(f"{'='*80}")
    print(f"\nCUSTOMER QUERY:")
    print(f"{query_data['query']}")
    print(f"\n{'-'*80}")
    
    # Run through the graph
    result = graph.invoke(initial_state)
    
    print(f"\nRESOLUTION FLOW:")
    for note in result["resolution_notes"]:
        print(f"  • {note}")
    
    print(f"\n{'-'*80}")
    print(f"FINAL RESPONSE:")
    print(f"{result['final_response']}")
    print(f"{'='*80}\n")
    
    return result


def save_results_to_file(results: list, output_folder: str = "ticket_results"):
    """Save ticket results to organized files in a folder"""
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save individual ticket files
    for result in results:
        ticket_id = result["ticket_id"]
        customer_id = result["customer_id"]
        
        # Create detailed ticket report
        ticket_report = f"""CUSTOMER SUPPORT TICKET REPORT
{'='*80}
Ticket ID: {ticket_id}
Customer ID: {customer_id}
Customer Name: {db.get_customer(customer_id).get('name', 'Unknown')}
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*80}

CUSTOMER QUERY:
{result['query']}

{'='*80}
TICKET CLASSIFICATION:
Intent: {result['intent']}
Priority: {result['priority']}
Sentiment Score: {result['sentiment_score']:.2f}
Escalated: {'Yes' if result['escalated'] else 'No'}

{'='*80}
RESOLUTION FLOW:
"""
        for note in result['resolution_notes']:
            ticket_report += f"  • {note}\n"
        
        ticket_report += f"""
{'='*80}
FINAL RESPONSE:
{result['final_response']}

{'='*80}
"""
        
        # Save individual ticket
        ticket_filename = os.path.join(output_folder, f"{ticket_id}_{timestamp}.txt")
        with open(ticket_filename, 'w', encoding='utf-8') as f:
            f.write(ticket_report)
    
    # Save summary report
    summary_report = f"""CUSTOMER SUPPORT SUMMARY REPORT
{'='*80}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*80}

STATISTICS:
Total tickets processed: {len(results)}
Escalated to human review: {sum(1 for r in results if r['escalated'])}
Auto-resolved: {sum(1 for r in results if not r['escalated'])}

INTENT DISTRIBUTION:
"""
    
    intent_counts = {}
    for r in results:
        intent_counts[r['intent']] = intent_counts.get(r['intent'], 0) + 1
    
    for intent, count in intent_counts.items():
        summary_report += f"  • {intent}: {count}\n"
    
    summary_report += f"\nAVERAGE QUALITY SCORE: {sum(r['sentiment_score'] for r in results) / len(results):.2f}\n\n"
    summary_report += f"{'='*80}\nTICKET DETAILS:\n{'='*80}\n\n"
    
    for result in results:
        summary_report += f"""
Ticket: {result['ticket_id']}
Customer: {db.get_customer(result['customer_id']).get('name', 'Unknown')} ({result['customer_id']})
Intent: {result['intent']} | Priority: {result['priority']} | Escalated: {'Yes' if result['escalated'] else 'No'}
Query: {result['query'][:100]}{'...' if len(result['query']) > 100 else ''}
---
"""
    
    summary_filename = os.path.join(output_folder, f"SUMMARY_{timestamp}.txt")
    with open(summary_filename, 'w', encoding='utf-8') as f:
        f.write(summary_report)
    
    # Save JSON version for data analysis
    json_data = []
    for result in results:
        json_data.append({
            "ticket_id": result["ticket_id"],
            "customer_id": result["customer_id"],
            "customer_name": db.get_customer(result["customer_id"]).get('name', 'Unknown'),
            "query": result["query"],
            "intent": result["intent"],
            "priority": result["priority"],
            "sentiment_score": result["sentiment_score"],
            "escalated": result["escalated"],
            "resolution_notes": result["resolution_notes"],
            "final_response": result["final_response"],
            "timestamp": datetime.now().isoformat()
        })
    
    json_filename = os.path.join(output_folder, f"tickets_data_{timestamp}.json")
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    return output_folder, timestamp


def main():
    """Main execution function"""
    print("🎫 Customer Support Ticketing System Simulator")
    print("=" * 80)
    
    # Create the graph
    support_graph = create_support_graph()
    
    # Process sample queries
    print("\nProcessing sample support tickets...\n")
    
    results = []
    for query_data in SAMPLE_QUERIES:
        result = process_ticket(query_data, support_graph)
        results.append(result)
    
    # Summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"Total tickets processed: {len(results)}")
    print(f"Escalated to human review: {sum(1 for r in results if r['escalated'])}")
    print(f"Auto-resolved: {sum(1 for r in results if not r['escalated'])}")
    
    intent_counts = {}
    for r in results:
        intent_counts[r['intent']] = intent_counts.get(r['intent'], 0) + 1
    
    print(f"\nIntent Distribution:")
    for intent, count in intent_counts.items():
        print(f"  • {intent}: {count}")
    
    print(f"\nAverage Quality Score: {sum(r['sentiment_score'] for r in results) / len(results):.2f}")
    
    # Save results to files
    print("\n" + "="*80)
    print("SAVING RESULTS TO FILES")
    print("="*80)
    
    output_folder, timestamp = save_results_to_file(results)
    
    print(f"✓ Results saved to folder: {output_folder}/")
    print(f"✓ Individual ticket reports: {len(results)} files")
    print(f"✓ Summary report: SUMMARY_{timestamp}.txt")
    print(f"✓ JSON data file: tickets_data_{timestamp}.json")
    print(f"\n📁 Check the '{output_folder}' folder for all saved files!")
    print("="*80)


if __name__ == "__main__":
    main()