from decimal import Decimal


class StakeInitialize:
    def __init__(self, gambler_id, initial_balance):
        self.gambler_id = gambler_id
        self.initial_balance = initial_balance


class StakeBetOutcome:
    def __init__(self, gambler_id, bet_amount, is_win, bet_id=None, game_id=None):
        self.gambler_id = gambler_id
        self.bet_amount = bet_amount
        self.is_win = is_win
        self.bet_id = bet_id
        self.game_id = game_id


class StakeDeposit:
    def __init__(self, gambler_id, amount):
        self.gambler_id = gambler_id
        self.amount = amount


class StakeWithdrawal:
    def __init__(self, gambler_id, amount):
        self.gambler_id = gambler_id
        self.amount = amount


class StakeHistoryFilter:
    def __init__(self, gambler_id, transaction_type=None, limit=None):
        self.gambler_id = gambler_id
        self.transaction_type = transaction_type
        self.limit = limit
