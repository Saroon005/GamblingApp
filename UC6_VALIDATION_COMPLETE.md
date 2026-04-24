# UC6: Input Validation and Error Handling
## Use Case 6 - Complete Implementation

---

## 📋 Overview

**UC6** implements **centralized input validation and comprehensive error handling** across the entire gambling simulation system. All validation logic is consolidated in a single module to ensure consistency, maintainability, and code reuse.

### Key Principles
✅ **KISS**: Keep It Simple, Stupid  
✅ **DRY**: Don't Repeat Yourself  
✅ **Centralized**: Single source of truth for all validation  
✅ **User-Friendly**: Clear, actionable error messages  
✅ **NO Pydantic**: Pure Python with custom validation  

---

## 🏗️ Architecture

### Module Structure
```
modules/
├── validation/
│   ├── __init__.py          # Export InputValidator
│   └── validator.py         # Centralized validation (UC6)
├── gambler/
│   └── validator.py         # NOW uses InputValidator
├── betting/
│   └── validator.py         # NOW uses InputValidator
```

### Validation Flow
```
User Input
    ↓
CLI Method (main.py)
    ↓
InputValidator.validate_X()  ← CENTRAL VALIDATION
    ↓
Exception ← ValidationException raised on error
    ↓
Catch & Display Error Message
```

---

## ✨ Features

### 1. Numeric Input Parsing
Safe parsing with clear error messages.

```python
# Parse float
probability = InputValidator.parse_float_safe(
    input("Probability: "), 
    field_name="Probability"
)
# Error: "Probability must be a valid number, got 'abc'"

# Parse Decimal
stake = InputValidator.parse_decimal_safe(
    input("Stake: "),
    field_name="Stake"
)
# Handles string, float, Decimal inputs safely

# Parse Integer
gambler_id = InputValidator.parse_int_safe(
    input("ID: "),
    field_name="Gambler ID"
)
```

### 2. Stake Validation
Ensures stakes are always positive.

```python
# Validate initial stake
initial_stake = InputValidator.validate_initial_stake(stake_input)
# Raises: ValidationException if ≤ 0 or invalid

# Validate any stake
stake = InputValidator.validate_stake(stake_input, "Player Stake")
# Ensures: > 0, numeric, not None
```

### 3. Bet Amount Validation
Prevents betting more than available.

```python
bet_amount = InputValidator.validate_bet_amount(
    bet_input,
    current_stake=Decimal(100),
    field_name="Bet Amount"
)
# Validates: bet > 0 AND bet ≤ current_stake
# Error: "Insufficient stake: bet_amount is $50 but current stake is only $30"
```

### 4. Limits Validation
Ensures thresholds make sense.

```python
initial, win, loss = InputValidator.validate_limits(
    initial_stake=1000,
    win_threshold=2000,
    loss_threshold=500
)
# Validates:
#   - win_threshold > initial_stake
#   - loss_threshold < initial_stake
#   - loss_threshold ≥ 0
```

### 5. Probability Validation
Ensures probabilities are in [0, 1].

```python
prob = InputValidator.validate_probability(
    input("Win Probability (0-1): "),
    field_name="Win Probability"
)
# Validates: 0.0 ≤ probability ≤ 1.0
# Error: "Win Probability must be between 0.0 and 1.0, got 1.5"
```

### 6. String Validation
Validates non-empty strings with optional max length.

```python
username = InputValidator.validate_non_empty_string(
    input("Username: "),
    field_name="username",
    max_length=50
)
# Ensures: not empty, not whitespace-only, ≤ 50 chars
```

### 7. Email Validation
Validates email format.

```python
email = InputValidator.validate_email(input("Email: "))
# Uses regex pattern: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
# Error: "Invalid email format: not-an-email"
```

### 8. ID Validation
Ensures IDs are positive integers.

```python
gambler_id = InputValidator.validate_positive_integer(
    input("Gambler ID: "),
    field_name="Gambler ID"
)
# Validates: positive (> 0), integer
```

### 9. Range Validation
Checks if value is within range.

```python
value = InputValidator.validate_in_range(
    input("Value: "),
    min_val=0,
    max_val=100,
    field_name="Percentage"
)
# Validates: 0 ≤ value ≤ 100
```

### 10. Generic Validators
Reusable validators for common checks.

```python
# Validate positive (> 0)
amount = InputValidator.validate_positive(input("Amount: "), "Amount")

# Validate non-negative (≥ 0)
bonus = InputValidator.validate_non_negative(input("Bonus: "), "Bonus")
```

### 11. Composite Validation
Validate entire gambler creation with one call.

```python
validated = InputValidator.validate_gambler_creation(
    username=username_input,
    full_name=full_name_input,
    email=email_input,
    initial_stake=initial_input,
    win_threshold=win_input,
    loss_threshold=loss_input,
    min_bet_amount=min_input
)
# Returns dict with all validated values
# Raises: ValidationException with ALL errors concatenated
```

---

## 🔄 Integration in CLI (main.py)

### Before (Old Way)
```python
def create_gambler(self):
    try:
        username = input("Username: ").strip()
        # ... raw inputs
        initial_stake = Decimal(input("Initial Stake ($): ").strip())
        # No validation! Crashes on bad input
```

### After (New Way with UC6)
```python
def create_gambler(self):
    try:
        username = input("Username: ").strip()
        initial_stake_input = input("Initial Stake ($): ").strip()
        
        # CENTRALIZED VALIDATION
        validated = InputValidator.validate_gambler_creation(
            username, full_name, email,
            initial_stake_input, win_threshold_input,
            loss_threshold_input, min_required_input
        )
        
        # Use validated data
        gambler_data = GamblerCreate(
            username=validated['username'],
            initial_stake=validated['initial_stake'],
            # ...
        )
    
    except ValidationException as e:
        print(f"✗ Validation Error: {e}")
    except DatabaseException as e:
        print(f"✗ Database Error: {e}")
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
```

---

## 🛡️ Exception Handling

### Exception Hierarchy
```
Exception
├── ValidationException (UC6 - INPUT VALIDATION)
├── DatabaseException
├── GamblerNotFoundException
├── StakeNotFoundException
├── InsufficientStakeException
├── BetNotFoundException
├── InvalidBetException
```

### Handling Pattern
```python
try:
    # Operation
    amount = InputValidator.validate_bet_amount(bet_input, stake)
except ValidationException as e:
    print(f"✗ Validation Error: {e}")           # User error
    logger.warning(f"Validation error: {e}")
except DatabaseException as e:
    print(f"✗ Database Error: {e}")            # System error
    logger.error(f"Database error: {e}")
except Exception as e:
    print(f"✗ Unexpected Error: {e}")          # Unknown error
    logger.error(f"Unexpected error: {e}")
```

---

## 📍 Where Validation Occurs

### 1. **CLI (main.py)** - PRIMARY ENTRY POINT
All user inputs pass through InputValidator:
- `create_gambler()` - Validates all 7 inputs (name, email, stakes, limits)
- `select_gambler()` - Validates gambler ID
- `place_bet()` - Validates bet amount and probability
- `start_session()` - Validates bets within session loop

### 2. **Gambler Module** - SECONDARY VALIDATION
`modules/gambler/validator.py` - Calls InputValidator functions:
```python
# Now delegates to InputValidator
InputValidator.validate_email(data.email)
InputValidator.validate_initial_stake(data.initial_stake)
InputValidator.validate_limits(init, win, loss)
```

### 3. **Betting Module** - SECONDARY VALIDATION
`modules/betting/validator.py` - Calls InputValidator functions:
```python
# Now delegates to InputValidator
InputValidator.validate_bet_amount(bet, stake)
InputValidator.validate_probability(prob)
```

---

## 🎯 Error Messages (User-Friendly)

### Validation Errors
```
✗ Validation Error: initial_stake must be greater than 0, got 0
✗ Validation Error: win_threshold ($2000) must be > initial_stake ($1000)
✗ Validation Error: Insufficient stake: bet_amount is $100 but current stake is only $50
✗ Validation Error: Win Probability must be between 0.0 and 1.0, got 1.5
```

### Database Errors
```
✗ Database Error: Error saving game record: ...
✗ Database Error: Error retrieving gambler stats: ...
```

### Unexpected Errors
```
✗ Unexpected Error: Unknown error occurred
```

---

## 📊 Validation Checklist

| Requirement | Implemented | Tests |
|---|---|---|
| ✅ Validate initial stake (> 0) | YES | Unit test coverage |
| ✅ Validate bet amount (> 0, ≤ stake) | YES | Unit test coverage |
| ✅ Validate limits (win > init > loss) | YES | Unit test coverage |
| ✅ Validate numeric inputs | YES | Safe parsing functions |
| ✅ Prevent negative values | YES | validate_non_negative() |
| ✅ Validate probability (0 ≤ p ≤ 1) | YES | Unit test coverage |
| ✅ Centralized validation module | YES | modules/validation/validator.py |
| ✅ User-friendly error messages | YES | All exceptions have clear msgs |
| ✅ Global exception handling | YES | Try/except in all CLI methods |
| ✅ Logging validation errors | YES | logger.warning() / logger.error() |
| ✅ NO crashes on bad input | YES | All exceptions caught |

---

## 🧪 Usage Examples

### Example 1: Safe Stake Input
```python
# User enters non-numeric value
>>> stake_input = "abc"
>>> stake = InputValidator.parse_decimal_safe(stake_input, "Stake")
ValidationException: Stake must be a valid number, got 'abc'

# User enters negative value
>>> stake_input = "-100"
>>> stake = InputValidator.validate_stake(stake_input)
ValidationException: stake must be greater than 0, got -100
```

### Example 2: Bet Amount Check
```python
# User bets more than stake
>>> bet = InputValidator.validate_bet_amount("200", Decimal(100))
ValidationException: Insufficient stake: bet_amount is $200 but current stake is only $100

# Valid bet
>>> bet = InputValidator.validate_bet_amount("50", Decimal(100))
Decimal('50')  # ✓ Returned
```

### Example 3: Threshold Validation
```python
# Invalid thresholds
>>> InputValidator.validate_limits(1000, 500, 800)
ValidationException: win_threshold ($500) must be greater than initial_stake ($1000); 
                      loss_threshold ($800) must be less than initial_stake ($1000)

# Valid thresholds
>>> InputValidator.validate_limits(1000, 2000, 500)
(Decimal('1000'), Decimal('2000'), Decimal('500'))  # ✓ Returned
```

### Example 4: Email Validation
```python
>>> InputValidator.validate_email("invalid.email")
ValidationException: Invalid email format: invalid.email

>>> InputValidator.validate_email("user@example.com")
'user@example.com'  # ✓ Returned
```

---

## 🔧 Implementation Details

### InputValidator Class Location
```
modules/
└── validation/
    ├── __init__.py
    └── validator.py  ← InputValidator class with 15+ methods
```

### Methods Summary
| Method | Purpose | Returns |
|--------|---------|---------|
| `parse_float_safe()` | Parse string to float safely | float |
| `parse_decimal_safe()` | Parse to Decimal safely | Decimal |
| `parse_int_safe()` | Parse string to int safely | int |
| `validate_stake()` | Validate positive stake | Decimal |
| `validate_initial_stake()` | Validate initial stake | Decimal |
| `validate_bet_amount()` | Validate bet amount | Decimal |
| `validate_limits()` | Validate all thresholds | tuple(3) |
| `validate_probability()` | Validate probability | float |
| `validate_positive()` | Validate > 0 | Decimal |
| `validate_non_negative()` | Validate ≥ 0 | Decimal |
| `validate_in_range()` | Validate range | float |
| `validate_non_empty_string()` | Validate string | str |
| `validate_email()` | Validate email format | str |
| `validate_positive_integer()` | Validate positive int | int |
| `validate_gambler_creation()` | Validate all gambler inputs | dict |

---

## ✅ Refactoring Summary

### Code Removed (Duplication)
```python
# From gambler/validator.py - removed duplication
# - _is_valid_email() → Now use InputValidator.validate_email()
# - Direct Decimal(0) checks → Now use InputValidator.validate_stake()

# From betting/validator.py - removed duplication
# - Direct min/max checks → Now use InputValidator.validate_probability()
# - Redundant bet_amount validation → Now use InputValidator.validate_bet_amount()
```

### Code Added (Centralized)
```python
# In modules/validation/validator.py
# - InputValidator class with 15+ reusable methods
# - Single source of truth for all validation logic
# - Consistent error messages across all modules
```

### Code Updated (Integration)
```python
# main.py - All input validation now goes through InputValidator
# gambler/validator.py - Delegates to InputValidator
# betting/validator.py - Delegates to InputValidator
```

---

## 🚀 How to Use

### 1. Import the Validator
```python
from modules.validation import InputValidator
```

### 2. Quick Validation
```python
# Validate bet amount
try:
    amount = InputValidator.validate_bet_amount(
        input("Bet: "),
        current_stake=Decimal(100)
    )
except ValidationException as e:
    print(f"Error: {e}")
```

### 3. Multi-Field Validation
```python
# Validate entire gambler creation
try:
    data = InputValidator.validate_gambler_creation(
        username, full_name, email,
        initial_stake, win_threshold, loss_threshold, min_bet
    )
except ValidationException as e:
    print(f"Validation errors: {e}")
```

---

## 📈 Benefits

| Benefit | Before UC6 | After UC6 |
|---------|-----------|----------|
| **Code Duplication** | Multiple validators | Single InputValidator |
| **Consistency** | Different validation in each module | Unified approach |
| **Maintainability** | Update each module | Update in one place |
| **Testing** | Test each module separately | Test InputValidator once |
| **Error Messages** | Inconsistent | Clear and actionable |
| **Robustness** | Crashes on invalid input | Graceful error handling |
| **Usability** | User confused by generic errors | Clear validation feedback |

---

## ✨ UC6 Complete! 

All 6 use cases now implemented:
- ✅ UC1: Gambler Profile Management
- ✅ UC2: Stake Management
- ✅ UC3: Betting Mechanism
- ✅ UC4: Game Session Management
- ✅ UC5: Win/Loss Calculation
- ✅ **UC6: Input Validation and Error Handling** ← NEW!

**System is now robust, maintainable, and user-friendly!**
