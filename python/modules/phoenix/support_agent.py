import json
import re
import uuid
from typing import Any, Dict, List, Literal, Optional, TypedDict
from openai import OpenAI
from opentelemetry import trace
from phoenix.client import Client
from phoenix.otel import register
from dotenv import load_dotenv
load_dotenv()
from openinference.semconv.trace import SpanAttributes


tracer_provider = register(project_name="support-bot", auto_instrument=True)

client = OpenAI()
phoenix_client = Client()
# Get a tracer for creating custom spans
tracer = trace.get_tracer("support-agent")

user_query = "Where is my order?"

result = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Classify the query as 'order_status' or 'faq'"},
        {"role": "user", "content": user_query},
    ],
)
print("\n✅ This LLM call is automatically traced! Check Phoenix UI to see the span.")


class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str


# Order Database (for tool calls)
ORDER_DATABASE: Dict[str, Dict[str, str]] = {
    "ORD-12345": {
        "status": "shipped",
        "carrier": "FedEx",
        "trackingNumber": "1234567890",
        "eta": "December 11, 2025",
    },
    "ORD-67890": {
        "status": "processing",
        "carrier": "pending",
        "trackingNumber": "pending",
        "eta": "December 15, 2025",
    },
    "ORD-11111": {
        "status": "delivered",
        "carrier": "UPS",
        "trackingNumber": "9876543210",
        "eta": "Delivered December 5, 2025",
    },
}


# FAQ Database (for RAG)
class FAQEntry(TypedDict):
    id: int
    question: str
    answer: str
    category: str
    embedding: Optional[List[float]]


FAQ_DATABASE: List[FAQEntry] = [
    {
        "id": 1,
        "question": "How do I reset my password?",
        "answer": "Go to Settings > Security > Reset Password. You'll receive an email with a reset link that expires in 24 hours.",
        "category": "Account",
        "embedding": None,
    },
    {
        "id": 2,
        "question": "What's your refund policy?",
        "answer": "We offer full refunds within 30 days of purchase for unused items. Contact support with your order number to initiate a refund.",
        "category": "Billing",
        "embedding": None,
    },
    {
        "id": 3,
        "question": "How do I cancel my subscription?",
        "answer": "Go to Account Settings > Subscription > Cancel Subscription. Your access continues until the end of the current billing period.",
        "category": "Billing",
        "embedding": None,
    },
    {
        "id": 4,
        "question": "What payment methods do you accept?",
        "answer": "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay. All transactions are securely processed.",
        "category": "Billing",
        "embedding": None,
    },
    {
        "id": 5,
        "question": "How do I update my profile information?",
        "answer": "Go to Account Settings > Profile. You can update your name, email, phone number, and address there.",
        "category": "Account",
        "embedding": None,
    },
]

QueryCategory = Literal["order_status", "faq"]


class ClassificationResult(TypedDict):
    category: QueryCategory
    confidence: str
    reasoning: str


class AgentResponse(TypedDict):
    query: str
    response: str
    spanId: str
    category: QueryCategory
    sessionId: Optional[str]


class SessionContext(TypedDict):
    lastMentionedOrderId: Optional[str]
    turnCount: int



tools = [
    {
        "type": "function",
        "function": {
            "name": "lookupOrderStatus",
            "description": "Look up the current status of a customer order by order ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "orderId": {
                        "type": "string",
                        "description": "The order ID to look up (e.g., ORD-12345)",
                    }
                },
                "required": ["orderId"],
            },
        },
    }
]


# Helper function to execute tools automatically
def execute_tool_call(tool_call, database):
    """Execute a tool call and return the result."""
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    with tracer.start_as_current_span(
        function_name,
        attributes={
            SpanAttributes.OPENINFERENCE_SPAN_KIND: "TOOL",
            SpanAttributes.TOOL_NAME: function_name,
            SpanAttributes.TOOL_PARAMETERS: json.dumps(function_args),
            SpanAttributes.INPUT_VALUE: json.dumps(function_args),
        },
    ) as tool_span:
        if function_name == "lookupOrderStatus":
            order_id = function_args.get("orderId")
            result = database.get(order_id, {"error": f"Order {order_id} not found"})
        else:
            result = {"error": f"Unknown tool: {function_name}"}

        tool_span.set_attribute(SpanAttributes.OUTPUT_VALUE, json.dumps(result))
        tool_span.set_status(trace.Status(trace.StatusCode.OK))
        return result


user_query = "What is the status of ORD-12345?"

# Create a parent span to group all spans
with tracer.start_as_current_span(
    "tool-call-example",
    attributes={
        SpanAttributes.OPENINFERENCE_SPAN_KIND: "CHAIN",
        SpanAttributes.INPUT_VALUE: user_query,
    },
) as parent_span:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful customer support agent. When customers ask about order status, use the lookupOrderStatus tool to get the information.",
        },
        {"role": "user", "content": user_query},
    ]

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    message = result.choices[0].message
    messages.append(message)

    # Execute tool if called, then get final response
    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_result = execute_tool_call(tool_call, ORDER_DATABASE)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

        # Final LLM call with tool result
        final_result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        final_response = final_result.choices[0].message.content
    else:
        final_response = message.content

    parent_span.set_attribute(SpanAttributes.OUTPUT_VALUE, final_response)
    parent_span.set_status(trace.Status(trace.StatusCode.OK))
    print(f"Query: {user_query}")
print(f"Response: {final_response}")
print("✅ Check Phoenix UI to see the full trace")