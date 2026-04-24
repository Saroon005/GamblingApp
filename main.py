from db.init_db import Database
from modules.gambler.schemas import GamblerCreate
from modules.gambler.service import GamblerService
from modules.stake.service import StakeService
from modules.betting.service import BettingService
from modules.session.service import SessionService
from modules.winloss.service import WinLossService
from modules.validation import InputValidator
from modules.interaction import UIDisplay
from core.logger import logger
from core.exceptions import ValidationException, DatabaseException
from decimal import Decimal


class GamblingCLI:
    """Simple and clean CLI for the gambling simulation system"""
    
    def __init__(self):
        self.current_gambler_id = None
        self.current_gambler = None
        Database.init()
    
    def show_menu(self):
        """Display main menu"""
        UIDisplay.show_main_menu()
    
    def create_gambler(self):
        """Create a new gambler with input validation and UI display"""
        UIDisplay.show_section_header("📝 CREATE GAMBLER")
        
        try:
            # Get all inputs
            inputs = UIDisplay.prompt_gambler_input()
            
            # Validate all inputs together
            validated = InputValidator.validate_gambler_creation(
                inputs['username'], inputs['full_name'], inputs['email'],
                inputs['initial_stake'], inputs['win_threshold'], 
                inputs['loss_threshold'], inputs['min_bet']
            )
            
            # Create gambler profile
            gambler_data = GamblerCreate(
                username=validated['username'],
                full_name=validated['full_name'],
                email=validated['email'],
                initial_stake=validated['initial_stake'],
                win_threshold=validated['win_threshold'],
                loss_threshold=validated['loss_threshold'],
                min_required_stake=validated['min_bet_amount']
            )
            
            gambler = GamblerService.create_gambler(gambler_data)
            StakeService.initialize_stake(gambler['gambler_id'])
            
            self.current_gambler_id = gambler['gambler_id']
            self.current_gambler = gambler
            
            UIDisplay.show_success(
                f"Gambler '{gambler['username']}' created (ID: {gambler['gambler_id']})"
            )
        
        except ValidationException as e:
            UIDisplay.show_validation_error(str(e))
            logger.warning(f"Validation error: {e}")
        except DatabaseException as e:
            UIDisplay.show_database_error(str(e))
            logger.error(f"Database error: {e}")
        except Exception as e:
            UIDisplay.show_error("Unexpected Error", str(e))
            logger.error(f"Unexpected error: {e}")
    
    def select_gambler(self):
        """Select a gambler by ID with clean UI"""
        UIDisplay.show_section_header("👤 SELECT GAMBLER")
        
        try:
            gambler_id_input = UIDisplay.prompt_gambler_id()
            gambler_id = InputValidator.validate_positive_integer(gambler_id_input, "Gambler ID")
            
            gambler = GamblerService.get_gambler_profile(gambler_id)
            stake = StakeService.get_current_balance(gambler_id)
            
            self.current_gambler_id = gambler_id
            self.current_gambler = gambler
            
            UIDisplay.show_gambler_selected(gambler['username'], gambler_id, stake)
        
        except ValidationException as e:
            UIDisplay.show_validation_error(str(e))
            logger.warning(f"Validation error: {e}")
        except Exception as e:
            UIDisplay.show_error("Error", str(e))
            logger.error(f"Error selecting gambler: {e}")
    
    def place_bet(self):
        """Place a single bet with clean outcome display"""
        UIDisplay.show_section_header("💰 PLACE BET")
        
        if not self.current_gambler_id:
            UIDisplay.show_no_gambler_selected()
            return
        
        try:
            stake = StakeService.get_current_balance(self.current_gambler_id)
            UIDisplay.show_current_status(self.current_gambler['username'], stake)
            
            # Validate inputs
            bet_amount_input = UIDisplay.prompt_bet_amount()
            amount = InputValidator.validate_bet_amount(bet_amount_input, stake)
            
            probability_input = UIDisplay.prompt_probability()
            probability = InputValidator.validate_probability(probability_input)
            
            # Place and resolve bet
            result = BettingService.place_and_resolve_bet(
                self.current_gambler_id, amount, probability
            )
            
            # Display outcome
            UIDisplay.show_bet_result(
                result['is_win'], amount, result['stake_after']
            )
        
        except ValidationException as e:
            UIDisplay.show_validation_error(str(e))
            logger.warning(f"Validation error: {e}")
        except DatabaseException as e:
            UIDisplay.show_database_error(str(e))
            logger.error(f"Database error: {e}")
        except Exception as e:
            UIDisplay.show_error("Error", str(e))
            logger.error(f"Error placing bet: {e}")
    
    def start_session(self):
        """Start a betting session with clean UI for bet outcomes and summary"""
        UIDisplay.show_section_header("🎮 START SESSION")
        
        if not self.current_gambler_id:
            UIDisplay.show_no_gambler_selected()
            return
        
        try:
            gambler = self.current_gambler
            stake = StakeService.get_current_balance(self.current_gambler_id)
            
            # Display session info
            UIDisplay.show_session_info(
                stake, 
                Decimal(gambler['win_threshold']),
                Decimal(gambler['loss_threshold'])
            )
            
            # Start session
            session = SessionService.start_session(self.current_gambler_id)
            session_id = session['session_id']
            tracker = WinLossService()
            bet_count = 0
            
            # Session loop
            while True:
                stake = BettingService.get_current_stake(self.current_gambler_id)
                UIDisplay.show_bet_input_prompt(bet_count + 1, stake)
                
                # Get bet inputs
                amount_input, prob_input = UIDisplay.prompt_session_bet()
                if amount_input is None:
                    break
                
                try:
                    # Validate inputs
                    amount = InputValidator.validate_bet_amount(amount_input, stake)
                    prob = InputValidator.validate_probability(prob_input)
                    
                    # Place and resolve bet
                    result = BettingService.place_and_resolve_bet(
                        self.current_gambler_id, amount, prob
                    )
                    
                    # Record in session and track win/loss
                    SessionService.record_bet_in_session(session_id)
                    outcome = tracker.record_game_outcome(
                        session_id, self.current_gambler_id, result['bet_id'],
                        result['is_win'], amount, result['stake_before'], 
                        result['stake_after']
                    )
                    
                    # Display outcome with streak info
                    if result['is_win']:
                        UIDisplay.show_win_outcome(
                            amount, result['stake_after'],
                            outcome['win_streak'], outcome['loss_streak']
                        )
                    else:
                        UIDisplay.show_loss_outcome(
                            amount, result['stake_after'],
                            outcome['win_streak'], outcome['loss_streak']
                        )
                    
                    bet_count += 1
                    
                    # Check thresholds
                    if result['stake_after'] >= Decimal(gambler['win_threshold']):
                        UIDisplay.show_win_threshold_reached()
                        SessionService.end_session(session_id, "WIN_THRESHOLD")
                        break
                    elif result['stake_after'] <= Decimal(gambler['loss_threshold']):
                        UIDisplay.show_loss_threshold_reached()
                        SessionService.end_session(session_id, "LOSS_THRESHOLD")
                        break
                
                except ValidationException as e:
                    UIDisplay.show_validation_error(str(e))
                    logger.warning(f"Validation error: {e}")
                except DatabaseException as e:
                    UIDisplay.show_database_error(str(e))
                    logger.error(f"Database error: {e}")
            
            # End session and show summary
            if bet_count > 0:
                try:
                    SessionService.end_session(session_id, "MANUAL")
                    stats = tracker.get_session_summary(session_id)
                    
                    UIDisplay.show_session_summary(
                        stats['total_games'],
                        stats['total_wins'],
                        stats['total_losses'],
                        stats['win_rate'],
                        result['stake_after'],
                        stats['current_win_streak'],
                        stats['current_loss_streak']
                    )
                except Exception as e:
                    UIDisplay.show_error("Error ending session", str(e))
                    logger.error(f"Error ending session: {e}")
            else:
                UIDisplay.show_warning("No bets placed. Session cancelled.")
        
        except DatabaseException as e:
            UIDisplay.show_database_error(str(e))
            logger.error(f"Database error: {e}")
        except Exception as e:
            UIDisplay.show_error("Unexpected Error", str(e))
            logger.error(f"Unexpected error: {e}")
    
    def show_stats(self):
        """Show gambler statistics with clean UI"""
        UIDisplay.show_section_header("📈 GAMBLER STATISTICS")
        
        if not self.current_gambler_id:
            UIDisplay.show_no_gambler_selected()
            return
        
        try:
            stake = StakeService.get_current_balance(self.current_gambler_id)
            stats = WinLossService.get_gambler_overall_stats(self.current_gambler_id)
            
            UIDisplay.show_gambler_stats(
                stake,
                stats['total_games'],
                stats['total_wins'],
                stats['total_losses'],
                stats['win_rate'],
                stats['total_net_change']
            )
        
        except DatabaseException as e:
            UIDisplay.show_database_error(str(e))
            logger.error(f"Database error: {e}")
        except Exception as e:
            UIDisplay.show_error("Error", str(e))
            logger.error(f"Error retrieving stats: {e}")
    
    def run(self):
        """Run the gambling simulation CLI"""
        UIDisplay.show_welcome()
        
        while True:
            self.show_menu()
            choice = UIDisplay.prompt_menu_choice()
            
            match choice:
                case "1":
                    self.create_gambler()
                case "2":
                    self.select_gambler()
                case "3":
                    self.place_bet()
                case "4":
                    self.start_session()
                case "5":
                    self.show_stats()
                case "6":
                    UIDisplay.show_goodbye()
                    break
                case _:
                    UIDisplay.show_invalid_choice()


if __name__ == "__main__":
    cli = GamblingCLI()
    cli.run()
