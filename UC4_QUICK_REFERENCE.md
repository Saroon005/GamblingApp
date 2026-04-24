# UC4 Quick Reference

## 1-Minute Overview
UC4 tracks game sessions. Start a session → loop bets → ends when thresholds reached or user stops.

## Quick Code Snippets

### Start a Session
```python
from modules.session.service import SessionService

result = SessionService.start_session(gambler_id=1)
session_id = result['session_id']
print(f"Session {session_id} started")
```

### Record a Bet in Session
```python
SessionService.record_bet_in_session(session_id)
```

### End a Session
```python
SessionService.end_session(session_id, "MANUAL")
# or "WIN_THRESHOLD", "LOSS_THRESHOLD", "ERROR"
```

### Get Active Session
```python
session = SessionService.get_active_session(gambler_id)
if session:
    print(f"Session {session['session_id']} active with {session['games_played']} bets")
```

## CLI Usage

1. Select gambler (option 2)
2. Initialize stake (option 4)
3. Start Game Session (option 10)
4. Enter bet amount and probability
5. Session auto-ends on threshold or type "stop"

## Database Table

```
sessions
├── session_id (PK)
├── gambler_id (FK)
├── status ('ACTIVE'/'ENDED')
├── starting_stake ($)
├── ending_stake ($)
├── games_played (count)
├── started_at (timestamp)
├── ended_at (timestamp)
└── end_reason (string)
```

## Integration

| UC | Method Called |
|----|---|
| UC1 | `GamblerRepository.get_by_id()` - validate gambler |
| UC2 | `StakeService.get_current_balance()` - get starting & ending stake |
| UC3 | `BettingService.place_and_resolve_bet()` - bet in loop |

## Methods

### SessionRepository
- `create_session(gambler_id, starting_stake)` → session_id
- `end_session(session_id, end_reason, ending_stake)` → None
- `get_session(session_id)` → session dict
- `get_active_session(gambler_id)` → session dict (or None)
- `increment_games_played(session_id)` → None

### SessionService
- `start_session(gambler_id)` → {'session_id': int}
- `end_session(session_id, end_reason)` → None
- `get_active_session(gambler_id)` → session dict
- `record_bet_in_session(session_id)` → None

## Threshold Checking

In CLI loop:
```python
if stake >= win_threshold:
    SessionService.end_session(session_id, "WIN_THRESHOLD")
elif stake <= loss_threshold:
    SessionService.end_session(session_id, "LOSS_THRESHOLD")
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Session not starting | Verify gambler exists (UC1) |
| Bets not recording | Call `record_bet_in_session()` after each bet |
| Ending stake wrong | Ensure `get_current_balance()` called before end |
| No DB records | Run `Database.init()` to create tables |

## Testing

```bash
python test_uc4.py
```

Expected output:
```
[1] Initializing database...
[2] Creating test gambler...
[3] Initializing stake...
[4] Starting game session...
[5] Verifying active session...
[6] Simulating 5 bets in session...
[7] Ending session...
[8] Verifying session is ended...
[9] Final gambler status...
✓ UC4 TEST COMPLETE - ALL CHECKS PASSED!
```

## SessionRepository Connection Pattern

```python
connection = DatabaseConnection.get_db_connection()
cursor = connection.cursor(dictionary=True)  # For SELECT
try:
    cursor.execute(query, values)
    connection.commit()  # For INSERT/UPDATE/DELETE
except Error as e:
    connection.rollback()
    raise DatabaseException(...)
finally:
    cursor.close()
    connection.close()
```

---
**Keep it simple. Focus on the core: track sessions, record bets, detect thresholds.**
