"""
UC7: User Interaction - Clean CLI Interface Layer
==================================================

Responsible for:
- Displaying menus and prompts
- Showing game status and outcomes
- Presenting session summaries
- Formatting output for readability
- NO business logic (just display logic)
"""

from decimal import Decimal
from core.logger import logger


class UIDisplay:
    """User interface display functions for the gambling system"""
    
    # ===== MENU DISPLAYS =====
    
    @staticmethod
    def show_main_menu():
        """Display main menu"""
        print("\n" + "=" * 70)
        print("🎰 GAMBLING SIMULATION SYSTEM")
        print("=" * 70)
        print("1. Create Gambler")
        print("2. Select Gambler")
        print("3. Place Bet")
        print("4. Start Session")
        print("5. Show Statistics")
        print("6. Exit")
        print("=" * 70)
    
    @staticmethod
    def show_section_header(title: str):
        """Display a section header"""
        print(f"\n{title}")
        print("-" * 70)
    
    # ===== STATUS DISPLAYS =====
    
    @staticmethod
    def show_gambler_selected(gambler_name: str, gambler_id: int, current_stake: Decimal):
        """Show gambler selection confirmation"""
        print(f"\n✓ Selected Gambler: {gambler_name} (ID: {gambler_id})")
        print(f"  Current Stake: ${current_stake}")
    
    @staticmethod
    def show_current_status(gambler_name: str, current_stake: Decimal, 
                           total_games: int = 0, wins: int = 0, losses: int = 0):
        """Display current game status"""
        print(f"\nGambler: {gambler_name}")
        print(f"Current Stake: ${current_stake}")
        if total_games > 0:
            win_rate = (wins / total_games * 100) if total_games > 0 else 0
            print(f"Games Played: {total_games} | Wins: {wins} | Losses: {losses} | Win Rate: {win_rate:.1f}%")
    
    @staticmethod
    def show_session_info(current_stake: Decimal, win_threshold: Decimal, 
                         loss_threshold: Decimal, bet_count: int = 0):
        """Display session information"""
        print(f"\n┌─ SESSION INFO")
        print(f"├─ Current Stake: ${current_stake}")
        print(f"├─ Win Threshold: ${win_threshold}")
        print(f"├─ Loss Threshold: ${loss_threshold}")
        print(f"└─ Bets Placed: {bet_count}")
    
    # ===== BET OUTCOME DISPLAYS =====
    
    @staticmethod
    def show_bet_input_prompt(bet_number: int, current_stake: Decimal):
        """Prompt for bet input during session"""
        print(f"\n[Bet #{bet_number}] Current Stake: ${current_stake}")
        print("Enter 'stop' to end session")
    
    @staticmethod
    def show_win_outcome(amount: Decimal, new_stake: Decimal, 
                        win_streak: int, loss_streak: int):
        """Display winning bet outcome"""
        print(f"\n🎉 WIN! +${amount}")
        print(f"   New Stake: ${new_stake}")
        print(f"   Win Streak: {win_streak}  Loss Streak: {loss_streak}")
    
    @staticmethod
    def show_loss_outcome(amount: Decimal, new_stake: Decimal, 
                         win_streak: int, loss_streak: int):
        """Display losing bet outcome"""
        print(f"\n❌ LOSS! -${amount}")
        print(f"   New Stake: ${new_stake}")
        print(f"   Win Streak: {win_streak}  Loss Streak: {loss_streak}")
    
    @staticmethod
    def show_bet_result(is_win: bool, amount: Decimal, new_stake: Decimal):
        """Display simple bet result (for non-session bets)"""
        status = "🎉 WIN" if is_win else "❌ LOSS"
        change = f"+${amount}" if is_win else f"-${amount}"
        print(f"\n{status} | {change} | New Stake: ${new_stake}")
    
    # ===== THRESHOLD ALERTS =====
    
    @staticmethod
    def show_win_threshold_reached():
        """Alert: Win threshold reached"""
        print(f"\n🏆 WIN THRESHOLD REACHED! Congratulations!")
    
    @staticmethod
    def show_loss_threshold_reached():
        """Alert: Loss threshold reached"""
        print(f"\n💔 LOSS THRESHOLD REACHED! Session ended.")
    
    # ===== SESSION SUMMARY DISPLAYS =====
    
    @staticmethod
    def show_session_summary(total_games: int, total_wins: int, total_losses: int, 
                            win_rate: float, final_stake: Decimal, 
                            win_streak: int = 0, loss_streak: int = 0):
        """Display comprehensive session summary"""
        print("\n" + "=" * 70)
        print("📊 SESSION SUMMARY")
        print("=" * 70)
        print(f"Total Bets Placed: {total_games}")
        print(f"Wins: {total_wins} | Losses: {total_losses}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Current Streak: {win_streak if win_streak > 0 else loss_streak} "
              f"({'W' if win_streak > 0 else 'L'})")
        print(f"Final Stake: ${final_stake}")
        print("=" * 70)
    
    @staticmethod
    def show_quick_summary(total_games: int, wins: int, losses: int, 
                          win_rate: float, final_stake: Decimal):
        """Display quick session summary"""
        print(f"\n📊 Games: {total_games} | Wins: {wins} | Losses: {losses} | Rate: {win_rate:.1f}% | Stake: ${final_stake}")
    
    # ===== STATISTICS DISPLAYS =====
    
    @staticmethod
    def show_gambler_stats(current_stake: Decimal, total_games: int, wins: int, 
                          losses: int, win_rate: float, total_net_change: Decimal):
        """Display gambler lifetime statistics"""
        print("\n" + "=" * 70)
        print("📈 GAMBLER STATISTICS")
        print("=" * 70)
        print(f"Current Stake: ${current_stake}")
        print(f"Total Games: {total_games}")
        print(f"Wins: {wins} | Losses: {losses}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total Net Change: ${total_net_change}")
        print("=" * 70)
    
    # ===== ERROR & SUCCESS MESSAGES =====
    
    @staticmethod
    def show_success(message: str):
        """Display success message"""
        print(f"\n✓ {message}")
    
    @staticmethod
    def show_error(error_type: str, message: str):
        """Display error message"""
        print(f"\n✗ {error_type}: {message}")
    
    @staticmethod
    def show_validation_error(message: str):
        """Display validation error"""
        UIDisplay.show_error("Validation Error", message)
    
    @staticmethod
    def show_database_error(message: str):
        """Display database error"""
        UIDisplay.show_error("Database Error", message)
    
    @staticmethod
    def show_warning(message: str):
        """Display warning message"""
        print(f"\n⚠ {message}")
    
    # ===== INPUT PROMPTS =====
    
    @staticmethod
    def prompt_gambler_input() -> dict:
        """Prompt for all gambler creation inputs"""
        print("\nEnter gambler information:")
        return {
            'username': input("  Username: ").strip(),
            'full_name': input("  Full Name: ").strip(),
            'email': input("  Email: ").strip(),
            'initial_stake': input("  Initial Stake ($): ").strip(),
            'win_threshold': input("  Win Threshold ($): ").strip(),
            'loss_threshold': input("  Loss Threshold ($): ").strip(),
            'min_bet': input("  Min Bet Amount ($): ").strip(),
        }
    
    @staticmethod
    def prompt_gambler_id() -> str:
        """Prompt for gambler ID"""
        return input("\nGambler ID: ").strip()
    
    @staticmethod
    def prompt_bet_amount() -> str:
        """Prompt for bet amount"""
        return input("Bet Amount ($): ").strip()
    
    @staticmethod
    def prompt_probability() -> str:
        """Prompt for win probability"""
        return input("Win Probability (0-1): ").strip()
    
    @staticmethod
    def prompt_session_bet() -> tuple:
        """Prompt for session bet (amount and probability)"""
        amount = input("Bet ($) or 'stop': ").strip()
        if amount.lower() == "stop":
            return None, None
        
        prob = input("Probability (0-1): ").strip()
        return amount, prob
    
    @staticmethod
    def prompt_menu_choice() -> str:
        """Prompt for main menu choice"""
        return input("\nChoice (1-6): ").strip()
    
    # ===== UTILITY DISPLAYS =====
    
    @staticmethod
    def show_welcome():
        """Display welcome message"""
        print("\n" + "=" * 70)
        print("Welcome to the Gambling Simulation System!")
        print("=" * 70)
    
    @staticmethod
    def show_goodbye():
        """Display goodbye message"""
        print("\n👋 Thank you for playing! Goodbye!\n")
    
    @staticmethod
    def show_no_gambler_selected():
        """Show error when no gambler is selected"""
        UIDisplay.show_warning("No gambler selected. Please select a gambler first.")
    
    @staticmethod
    def show_invalid_choice():
        """Show error for invalid menu choice"""
        UIDisplay.show_warning("Invalid choice. Please try again.")
    
    @staticmethod
    def show_session_ended(reason: str):
        """Show session ended message"""
        UIDisplay.show_success(f"Session ended ({reason})")
    
    # ===== FORMATTING HELPERS =====
    
    @staticmethod
    def format_currency(amount: Decimal) -> str:
        """Format amount as currency"""
        return f"${amount:.2f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format value as percentage"""
        return f"{value:.1f}%"
    
    @staticmethod
    def separator(char: str = "-", length: int = 70) -> str:
        """Return a separator line"""
        return char * length
