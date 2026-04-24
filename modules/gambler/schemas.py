from decimal import Decimal


class GamblerCreate:
    def __init__(self, username, full_name, email, initial_stake, win_threshold, loss_threshold, min_required_stake):
        self.username = username
        self.full_name = full_name
        self.email = email
        self.initial_stake = initial_stake
        self.win_threshold = win_threshold
        self.loss_threshold = loss_threshold
        self.min_required_stake = min_required_stake


class GamblerUpdate:
    def __init__(self, full_name=None, email=None, win_threshold=None, loss_threshold=None, min_required_stake=None, is_active=None):
        self.full_name = full_name
        self.email = email
        self.win_threshold = win_threshold
        self.loss_threshold = loss_threshold
        self.min_required_stake = min_required_stake
        self.is_active = is_active
