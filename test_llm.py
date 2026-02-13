"""Test script to debug LLM service issue"""
import sys
sys.path.insert(0, '.')

from services.llm_service import LLMService
from services.csv_service import CSVService

# Test 1: Initialize LLM Service
print("=" * 60)
print("TEST 1: Initialize LLM Service")
print("=" * 60)
llm = LLMService()
print(f"LLM Client exists: {llm.client is not None}\n")

# Test 2: Parse sample CSV
print("=" * 60)
print("TEST 2: Parse Sample CSV")
print("=" * 60)
csv_service = CSVService()
success, summary, error = csv_service.parse_csv('sample.csv')
print(f"Parse success: {success}")
if not success:
    print(f"Error: {error}")
    sys.exit(1)
print(f"Summary: {summary}\n")

# Test 3: Generate insights
print("=" * 60)
print("TEST 3: Generate Insights")
print("=" * 60)
success, insights, error = llm.generate_insights(summary)
print(f"Success: {success}")
if success:
    print(f"Insights:\n{insights}")
else:
    print(f"ERROR: {error}")
