"""
Demo script to test ladder loading with retry logic and error handling.
Simulates API failures and recovery scenarios.
"""
import sys
import time
from unittest.mock import Mock, patch


# Mock the logger before importing modules
class MockLogger:
    def __init__(self, name):
        self.name = name

    def log(self, msg):
        print(f"[{self.name}] INFO: {msg}")

    def error(self, msg):
        print(f"[{self.name}] ERROR: {msg}")

    def debug(self, msg):
        print(f"[{self.name}] DEBUG: {msg}")


# Mock utils before importing bot_state
sys.modules['src.util.logger'] = Mock(MyLogger=MockLogger)
sys.modules['src.util.utils'] = Mock(
    is_error=lambda obj: isinstance(obj, Exception),
    get_exception_msg=lambda e: str(e)
)

from src.bot.bot_state import BotState
from src.svc.cncnet_api_svc import CnCNetApiSvc


def demo_scenario_1_api_failure_then_success():
    """Scenario 1: API fails initially, then succeeds on retry"""
    print("\n" + "="*80)
    print("SCENARIO 1: API fails twice, then succeeds on third attempt")
    print("="*80 + "\n")

    state = BotState()
    state.cnc_api_client = Mock(spec=CnCNetApiSvc)

    # Simulate: first 2 calls return exceptions, third call succeeds
    # Note: CnCNetApiSvc returns exceptions as values, not raises them
    call_count = [0]

    def mock_fetch():
        call_count[0] += 1
        if call_count[0] <= 2:
            return Exception("502 Server Error: Bad Gateway")
        return [
            {"abbreviation": "yr", "private": 0},
            {"abbreviation": "ra2", "private": 0},
            {"abbreviation": "d2k", "private": 0}
        ]

    state.cnc_api_client.fetch_ladders.side_effect = mock_fetch

    # Load ladders with max 5 retries, 1 second delay
    success = state.load_ladders(max_retries=5, retry_delay=1)

    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    print(f"Ladders loaded: {state.ladders}")
    print(f"Expected: ['yr', 'ra2', 'd2k']")
    assert success == True
    assert state.ladders == ['yr', 'ra2', 'd2k']


def demo_scenario_2_all_retries_fail():
    """Scenario 2: All retry attempts fail"""
    print("\n" + "="*80)
    print("SCENARIO 2: All retry attempts fail (API consistently down)")
    print("="*80 + "\n")

    state = BotState()
    state.cnc_api_client = Mock(spec=CnCNetApiSvc)

    # All calls fail
    state.cnc_api_client.fetch_ladders.return_value = Exception(
        "Connection timeout"
    )

    # Try with only 3 retries to keep test fast
    success = state.load_ladders(max_retries=3, retry_delay=1)

    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    print(f"Ladders loaded: {state.ladders}")
    print(f"Expected: []")
    assert success == False
    assert state.ladders == []


def demo_scenario_3_immediate_success():
    """Scenario 3: API works immediately"""
    print("\n" + "="*80)
    print("SCENARIO 3: API works on first attempt (normal operation)")
    print("="*80 + "\n")

    state = BotState()
    state.cnc_api_client = Mock(spec=CnCNetApiSvc)

    # Immediate success
    state.cnc_api_client.fetch_ladders.return_value = [
        {"abbreviation": "yr", "private": 0},
        {"abbreviation": "ra2", "private": 0},
        {"abbreviation": "blitz", "private": 0},
        {"abbreviation": "ra", "private": 0}
    ]

    success = state.load_ladders(max_retries=5, retry_delay=1)

    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    print(f"Ladders loaded: {state.ladders}")
    print(f"Expected: ['yr', 'ra2', 'blitz', 'ra']")
    assert success == True
    assert state.ladders == ['yr', 'ra2', 'blitz', 'ra']


def demo_scenario_4_empty_ladder_list():
    """Scenario 4: API returns empty list"""
    print("\n" + "="*80)
    print("SCENARIO 4: API returns empty ladder list")
    print("="*80 + "\n")

    state = BotState()
    state.cnc_api_client = Mock(spec=CnCNetApiSvc)

    # Empty list
    state.cnc_api_client.fetch_ladders.return_value = []

    success = state.load_ladders(max_retries=5, retry_delay=1)

    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    print(f"Ladders loaded: {state.ladders}")
    print(f"Expected: []")
    assert success == False
    assert state.ladders == []


def demo_scenario_5_malformed_data():
    """Scenario 5: API returns malformed data"""
    print("\n" + "="*80)
    print("SCENARIO 5: API returns malformed data (missing keys)")
    print("="*80 + "\n")

    state = BotState()
    state.cnc_api_client = Mock(spec=CnCNetApiSvc)

    # Malformed data - missing 'abbreviation' key
    state.cnc_api_client.fetch_ladders.return_value = [
        {"name": "yr", "private": 0},  # Missing 'abbreviation'
        {"abbreviation": "ra2", "private": 0}
    ]

    success = state.load_ladders(max_retries=5, retry_delay=1)

    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    print(f"Ladders loaded: {state.ladders}")
    print(f"Note: Should handle malformed data gracefully")


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# LADDER LOADING RECOVERY MECHANISM - TEST SCENARIOS")
    print("#"*80)

    try:
        demo_scenario_1_api_failure_then_success()
        demo_scenario_2_all_retries_fail()
        demo_scenario_3_immediate_success()
        demo_scenario_4_empty_ladder_list()
        demo_scenario_5_malformed_data()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80 + "\n")

        print("\nSUMMARY OF RECOVERY MECHANISMS:")
        print("-" * 80)
        print("1. Initial load retries: 5 attempts with exponential backoff (10s, 20s, 40s, 80s)")
        print("2. Periodic refresh: Every 4 hours via background task")
        print("3. On-demand refresh: When update task detects empty ladder list")
        print("4. Error logging: All failures logged with detailed error messages")
        print("5. Admin notifications: Sent when ladder loading fails")
        print("-" * 80)

    except AssertionError as e:
        print(f"\n[TEXT] TEST FAILED: {e}")
        sys.exit(1)
