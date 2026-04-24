from decimal import Decimal


class PlaceBet:
    def __init__(self, gambler_id, bet_amount, win_probability, game_index=1, 
                 odds_type=None, odds_value=None, strategy_id=None):
        self.gambler_id = gambler_id
        self.bet_amount = bet_amount
        self.win_probability = win_probability
        self.game_index = game_index
        self.odds_type = odds_type
        self.odds_value = odds_value
        self.strategy_id = strategy_id


class BetStrategy:
    def __init__(self, strategy_type, strategy_value):
        """
        strategy_type: 'FIXED' or 'PERCENTAGE'
        strategy_value: amount or percentage
        """
        self.strategy_type = strategy_type.upper()
        self.strategy_value = strategy_value


class BettingResult:
    def __init__(self, bet_id, is_win, amount_won_lost, new_balance):
        self.bet_id = bet_id
        self.is_win = is_win
        self.amount_won_lost = amount_won_lost
        self.new_balance = new_balance
