#!/usr/bin/env python3
"""
API Endpoint Test Script for PartSelect Agent
Tests all important queries via the API and displays results clearly.

Usage:
    # Make sure your server is running:
    uvicorn app.main:app --reload
    
    # Then run this script:
    python test_api_queries.py
"""

import requests
import json
import sys
from typing import Dict, Any

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

BASE_URL = "http://localhost:8000"


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text:^80}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")


def print_section(text):
    """Print a section header."""
    print(f"\n{BOLD}{CYAN}{'─'*80}{RESET}")
    print(f"{BOLD}{CYAN}{text}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*80}{RESET}\n")


def format_metadata(metadata: Dict[str, Any]) -> str:
    """Format metadata for display."""
    if not metadata:
        return "None"
    
    metadata_type = metadata.get("type", "unknown")
    
    if metadata_type == "product_info":
        product = metadata.get("product", {})
        return f"Product Card: {product.get('name', 'N/A')} (ID: {product.get('id', 'N/A')})"
    
    elif metadata_type == "order_info":
        order = metadata.get("order", {})
        return f"Order Card: Order #{order.get('id', 'N/A')} - {order.get('status', 'N/A')}"
    
    elif metadata_type == "links":
        links = metadata.get("links", [])
        link_labels = [link.get("label", "N/A") for link in links]
        return f"Links: {', '.join(link_labels)}"
    
    else:
        return f"Type: {metadata_type}"


def test_query(query: str, category: str = "General") -> Dict[str, Any]:
    """Test a single query and return results."""
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": query},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "query": query,
                "reply": data.get("reply", ""),
                "metadata": data.get("metadata"),
                "status_code": 200,
                "error": None
            }
        else:
            return {
                "success": False,
                "query": query,
                "reply": None,
                "metadata": None,
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "query": query,
            "reply": None,
            "metadata": None,
            "status_code": None,
            "error": "Connection refused. Is the server running?"
        }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "reply": None,
            "metadata": None,
            "status_code": None,
            "error": str(e)
        }


def display_result(result: Dict[str, Any], index: int, total: int):
    """Display a test result in a formatted way."""
    print(f"{YELLOW}[{index}/{total}]{RESET} {BOLD}Query:{RESET} {result['query']}")
    
    if result["success"]:
        print(f"  {GREEN}✓ Status:{RESET} Success (HTTP {result['status_code']})")
        print(f"  {BOLD}Reply:{RESET} {result['reply'][:200]}{'...' if len(result['reply']) > 200 else ''}")
        print(f"  {BOLD}Metadata:{RESET} {format_metadata(result['metadata'])}")
    else:
        print(f"  {RED}✗ Status:{RESET} Failed")
        if result["error"]:
            print(f"  {RED}Error:{RESET} {result['error']}")
    
    print()


def main():
    """Run all test queries."""
    print_header("PartSelect Agent API Test Suite")
    
    # Check if server is running
    print(f"{YELLOW}Checking if server is running at {BASE_URL}...{RESET}")
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print(f"{GREEN}✓ Server is running!{RESET}\n")
        else:
            print(f"{RED}✗ Server returned status {health_response.status_code}{RESET}\n")
    except requests.exceptions.ConnectionError:
        print(f"{RED}✗ Cannot connect to server at {BASE_URL}{RESET}")
        print(f"{YELLOW}Make sure your server is running:{RESET}")
        print(f"  {CYAN}uvicorn app.main:app --reload{RESET}\n")
        return 1
    except Exception as e:
        print(f"{RED}✗ Error checking server: {e}{RESET}\n")
        return 1
    
    # Define test queries organized by category
    test_queries = [
        # Product Information
        ("Product Info by Part ID", "Tell me about PS123456"),
        ("Product Info by MPN", "What is WPW10321304?"),
        ("Replacement Query", "I need a replacement for PS123456- not working"),
        ("Product Details", "What does part PS123456 do?"),
        
        # Compatibility Checks
        ("Compatibility Check", "Is PS123456 compatible with WDT780SAEM1?"),
        ("Compatibility with Model", "Does WPW10321304 fit my WDT780SAEM1 model?"),
        
        # Order Support
        ("Order Status - Format 1", "My order number is #4"),
        ("Order Status - Format 2", "Where is my order with orderid #3"),
        ("Order Status - Format 3", "Track order 1"),
        ("Order Return", "My order number is #4, I need to return my order"),
        
        # Repair Help
        ("Repair - Dishwasher Leak", "My dishwasher is leaking"),
        ("Repair - Refrigerator Not Cooling", "My refrigerator is not cooling"),
        ("Repair - Draining Issue", "My dishwasher isn't draining — what should I check?"),
        ("Repair - Ice Maker", "The ice maker on my Whirlpool fridge is not working. How can I fix it?"),
        ("Repair - General", "My dishwasher is not working"),
        
        # Blog/How-To
        ("How-To - Eco Mode", "What is eco mode on a dishwasher?"),
        ("How-To - Reset", "How do I reset my Bosch dishwasher?"),
        ("Usage Question", "What does sanitize cycle do?"),
        
        # Policy
        ("Return Policy", "What is your return policy?"),
        ("Warranty", "What is your warranty?"),
        ("Shipping Policy", "What is your shipping policy?"),
        ("Price Match", "Do you offer price matching?"),
        
        # Edge Cases
        ("Clarification Needed", "Is this compatible?"),
        ("Out of Scope", "Tell me about microwaves"),
        ("Empty/Invalid", "Hello"),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    # Run tests by category
    categories = {}
    for category, query in test_queries:
        if category not in categories:
            categories[category] = []
        categories[category].append((category, query))
    
    # Test each query
    total = len(test_queries)
    current = 0
    
    for category, queries in categories.items():
        print_section(f"Testing: {category}")
        
        for cat, query in queries:
            current += 1
            result = test_query(query, category)
            results.append(result)
            display_result(result, current, total)
            
            if result["success"]:
                passed += 1
            else:
                failed += 1
    
    # Summary
    print_header("Test Summary")
    print(f"Total Queries Tested: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    pass_rate = (passed / total * 100) if total > 0 else 0
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    # Detailed results
    if failed > 0:
        print_section("Failed Queries")
        for result in results:
            if not result["success"]:
                print(f"{RED}✗{RESET} {result['query']}")
                print(f"   Error: {result['error']}\n")
    
    # Success examples
    if passed > 0:
        print_section("Sample Successful Responses")
        successful = [r for r in results if r["success"]][:3]
        for result in successful:
            print(f"{BOLD}Query:{RESET} {result['query']}")
            print(f"{BOLD}Reply:{RESET} {result['reply'][:150]}...")
            print(f"{BOLD}Metadata:{RESET} {format_metadata(result['metadata'])}\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user.{RESET}")
        sys.exit(1)

