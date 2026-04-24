#!/usr/bin/env python3
"""Test UC4: Game Session Management"""

from decimal import Decimal
from modules.gambler.schemas import GamblerCreate
from modules.gambler.service import GamblerService
from modules.stake.service import StakeService
from modules.betting.service import BettingService
from modules.session.service import SessionService
from modules.session.repository import SessionRepository
from db.init_db import Database
from core.logger import logger

def test_uc4_game_session():
    """Test UC4 complete workflow"""
    
    print("\n" + "=" * 70)
    print("UC4: GAME SESSION MANAGEMENT - COMPLETE TEST")
    print("=" * 70)
    
    # Initialize database
    print("\n[1] Initializing database...")
    Database.init()
    print("✓ Database ready")
    
    # Step 1: Create gambler
    print("\n[2] Creating test gambler...")
    gambler_data = GamblerCreate(
        username="test_gambler_uc4",
        full_name="Test Gambler UC4",
        email="test.uc4@example.com",
        initial_stake=Decimal("1000.00"),
        win_threshold=Decimal("1500.00"),
        loss_threshold=Decimal("200.00"),
        min_required_stake=Decimal("50.00")
    )
    
    gambler = GamblerService.create_gambler(gambler_data)
    gambler_id = gambler['gambler_id']
    print(f"✓ Gambler created: ID={gambler_id}, Username={gambler['username']}")
    
    # Step 2: Initialize stake
    print("\n[3] Initializing stake...")
    StakeService.initialize_stake(gambler_id)
    current_stake = StakeService.get_current_balance(gambler_id)
    print(f"✓ Stake initialized: ${current_stake}")
    
    # Step 3: Start session
    print("\n[4] Starting game session...")
    session_result = SessionService.start_session(gambler_id)
    session_id = session_result['session_id']
    print(f"✓ Session started: ID={session_id}")
    
    # Step 4: Verify session is active
    print("\n[5] Verifying active session...")
    active_session = SessionService.get_active_session(gambler_id)
    if active_session and active_session['status'] == 'ACTIVE':
        print(f"✓ Session is active: {active_session}")
    else:
        print("✗ Session not found or not active!")
        return False
    
    # Step 5: Simulate betting
    print("\n[6] Simulating 5 bets in session...")
    for i in range(1, 6):
        print(f"\n   Bet {i}:")
        
        # Place bet
        bet_result = BettingService.place_and_resolve_bet(
            gambler_id,
            Decimal("50.00"),
            0.5
        )
        
        print(f"   - Result: {'WIN' if bet_result['is_win'] else 'LOSS'}")
        print(f"   - Stake: ${bet_result['stake_after']}")
        
        # Record in session
        SessionService.record_bet_in_session(session_id)
    
    # Step 6: End session
    print("\n[7] Ending session...")
    SessionService.end_session(session_id, "TEST_COMPLETE")
    print(f"✓ Session ended")
    
    # Step 7: Verify session is ended
    print("\n[8] Verifying session is ended...")
    session = SessionRepository.get_session(session_id)
    if session and session['status'] == 'ENDED':
        print(f"✓ Session is ended:")
        print(f"   - Reason: {session['end_reason']}")
        print(f"   - Games Played: {session['games_played']}")
        print(f"   - Starting Stake: ${session['starting_stake']}")
        print(f"   - Ending Stake: ${session['ending_stake']}")
        print(f"   - Duration: {session['started_at']} to {session['ended_at']}")
    else:
        print("✗ Session not ended properly!")
        return False
    
    # Step 8: get_current_balance for final stake
    print("\n[9] Final gambler status...")
    final_stake = StakeService.get_current_balance(gambler_id)
    print(f"✓ Final Stake: ${final_stake}")
    
    print("\n" + "=" * 70)
    print("✓ UC4 TEST COMPLETE - ALL CHECKS PASSED!")
    print("=" * 70 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = test_uc4_game_session()
        if not success:
            exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"\n✗ Test failed: {e}")
        exit(1)
