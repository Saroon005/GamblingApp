# UC6 Quick Start: Input Validation and Error Handling

## 🎯 What's New in UC6?

**Centralized Input Validation** - All validation logic is now in one place, making the system:
- ✅ More robust (no crashes on bad input)
- ✅ More consistent (same validation rules everywhere)
- ✅ More maintainable (change validation once, update everywhere)
- ✅ More user-friendly (clear error messages)

---

## 🚀 Using the Validator in Code

### Example 1: Validate Bet Amount
```python
from modules.validation import InputValidator
from core.exceptions import ValidationException

try:
    # Only 2 lines of code!
    bet_amount = InputValidator.validate_bet_amount(
        input("Bet ($): "),
        current_stake=current_balance
    )
    # Use bet_amount...
except ValidationException as e:
    print(f"❌ {e}")  # User-friendly error message
```

### Example 2: Validate Probability
```python
try:
    probability = InputValidator.validate_probability(
        input("Win Probability (0-1): ")
    )
    # Use probability...
except ValidationException as e:
    print(f"❌ {e}")
```

### Example 3: Safe Numeric Parsing
```python
try:
    stake = InputValidator.parse_decimal_safe(
        input("Stake ($): "),
        field_name="Stake"
    )
    # stake is now a Decimal, guaranteed to be valid
except ValidationException as e:
    print(f"❌ {e}")
```

### Example 4: Multi-Input Validation
```python
try:
    # Validate entire gambler creation in ONE call
    validated = InputValidator.validate_gambler_creation(
        username, full_name, email,
        initial_stake, win_threshold, loss_threshold, min_bet
    )
    # All inputs are validated and converted
    print(f"✓ Created {validated['username']}")
except ValidationException as e:
    print(f"❌ Validation errors: {e}")
```

---

## 📋 Available Validators

### Numeric Parsing (Safe)
- `parse_float_safe(value, field_name)` → float
- `parse_decimal_safe(value, field_name)` → Decimal
- `parse_int_safe(value, field_name)` → int

### Numeric Validation
- `validate_stake(value, field_name)` → Decimal (> 0)
- `validate_initial_stake(value)` → Decimal (> 0)
- `validate_bet_amount(value, current_stake)` → Decimal (0 < bet ≤ stake)
- `validate_probability(value, field_name)` → float (0.0 ≤ prob ≤ 1.0)
- `validate_positive(value, field_name)` → Decimal (> 0)
- `validate_non_negative(value, field_name)` → Decimal (≥ 0)
- `validate_in_range(value, min, max, field_name)` → float

### Threshold Validation
- `validate_limits(initial, win, loss)` → tuple (validates: win > init > loss ≥ 0)

### String Validation
- `validate_non_empty_string(value, field_name, max_length)` → str
- `validate_email(value)` → str

### ID Validation
- `validate_positive_integer(value, field_name)` → int

### Composite Validation
- `validate_gambler_creation(...)` → dict (validates all 7 inputs)

---

## 🔴 Error Messages (What Users See)

```
# Invalid input type
❌ Validation Error: initial_stake must be a valid number, got 'abc'

# Negative value
❌ Validation Error: initial_stake must be greater than 0, got -100

# Bet exceeds stake
❌ Validation Error: Insufficient stake: bet_amount is $1000 but current stake is only $500

# Invalid probability
❌ Validation Error: Win Probability must be between 0.0 and 1.0, got 2.0

# Invalid email
❌ Validation Error: Invalid email format: not-an-email

# Invalid threshold
❌ Validation Error: win_threshold ($500) must be greater than initial_stake ($1000)

# Empty string
❌ Validation Error: username cannot be empty
```

---

## 🧪 Testing Validation

### Test 1: Bet Amount Validation
```python
from modules.validation import InputValidator
from decimal import Decimal

# Should succeed
amount = InputValidator.validate_bet_amount("50", Decimal(100))
print(f"✓ Valid: {amount}")

# Should fail (more than stake)
try:
    amount = InputValidator.validate_bet_amount("150", Decimal(100))
except ValidationException as e:
    print(f"✓ Caught error: {e}")
```

### Test 2: Probability Validation
```python
# Should succeed
prob = InputValidator.validate_probability("0.5")
print(f"✓ Valid: {prob}")

# Should fail (> 1.0)
try:
    prob = InputValidator.validate_probability("1.5")
except ValidationException as e:
    print(f"✓ Caught error: {e}")
```

### Test 3: Threshold Validation
```python
# Should succeed
init, win, loss = InputValidator.validate_limits(1000, 2000, 500)
print(f"✓ Valid: init={init}, win={win}, loss={loss}")

# Should fail (win < init)
try:
    init, win, loss = InputValidator.validate_limits(2000, 1000, 500)
except ValidationException as e:
    print(f"✓ Caught error: {e}")
```

---

## 🏭 Integration Points

### 1. **main.py** (CLI) - PRIMARY USAGE
All user inputs go through InputValidator:
```python
# Create Gambler ✓
# Select Gambler ✓
# Place Bet ✓
# Start Session ✓
```

### 2. **modules/gambler/validator.py** - SECONDARY USAGE
Now delegates to InputValidator:
```python
# Calls:
InputValidator.validate_email()
InputValidator.validate_initial_stake()
InputValidator.validate_limits()
```

### 3. **modules/betting/validator.py** - SECONDARY USAGE
Now delegates to InputValidator:
```python
# Calls:
InputValidator.validate_bet_amount()
InputValidator.validate_probability()
```

---

## 📊 Validation Checklist

| Input | Validator | Rules |
|-------|-----------|-------|
| Username | `validate_non_empty_string()` | 1-50 chars, not empty |
| Full Name | `validate_non_empty_string()` | 1-100 chars, not empty |
| Email | `validate_email()` | Valid email format |
| Initial Stake | `validate_initial_stake()` | > 0, numeric |
| Win Threshold | `validate_limits()` | > initial, numeric |
| Loss Threshold | `validate_limits()` | < initial, ≥ 0 |
| Min Bet | `validate_non_negative()` | ≥ 0, numeric |
| Bet Amount | `validate_bet_amount()` | 0 < bet ≤ stake |
| Probability | `validate_probability()` | 0.0 ≤ prob ≤ 1.0 |

---

## 🛡️ Exception Handling Pattern

**Always use this pattern:**
```python
from core.exceptions import ValidationException, DatabaseException

try:
    # Validate input
    amount = InputValidator.validate_bet_amount(user_input, stake)
    # Use amount...
except ValidationException as e:
    print(f"✗ Validation Error: {e}")      # User error - expected
except DatabaseException as e:
    print(f"✗ Database Error: {e}")        # System error - unexpected
except Exception as e:
    print(f"✗ Unexpected Error: {e}")      # Unknown error - log it
```

---

## 🎯 Key Features

✅ **Centralized** - One module, all validation  
✅ **Reusable** - Use anywhere in the codebase  
✅ **Safe** - Handles all edge cases gracefully  
✅ **Clear** - Error messages clients understand  
✅ **Logged** - All errors logged for debugging  
✅ **Typed** - Returns correct types (Decimal, float, int, str)  
✅ **Composable** - Mix and match validators  
✅ **Simple** - No magic, just plain functions  

---

## 📁 File Structure

```
modules/
└── validation/
    ├── __init__.py              # Export InputValidator
    └── validator.py             # InputValidator class (UC6)
                                   - 15+ methods
                                   - Single source of truth
                                   - <400 lines of clear code
```

---

## ✨ System Status

All 6 use cases implemented and working:
- UC1: Gambler Profile Management ✓
- UC2: Stake Management ✓
- UC3: Betting Mechanism ✓
- UC4: Game Session Management ✓
- UC5: Win/Loss Calculation ✓
- **UC6: Input Validation and Error Handling ✓ NEW!**

**No crashes on invalid input!** 🎉

---

## 🚀 Try It Now!

```bash
python main.py
```

Then try:
1. Enter invalid inputs (strings instead of numbers)
2. Enter negative values
3. Enter thresholds in wrong order
4. Try to bet more than your stake
5. Enter invalid email

**You'll get clear, helpful error messages** - no crashes!
