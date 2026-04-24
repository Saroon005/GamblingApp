from db.init_db import Database
from modules.gambler.schemas import GamblerCreate
from modules.gambler.service import GamblerService
from modules.stake.service import StakeService
from modules.betting.service import BettingService
from core.logger import logger
from core.exceptions import ValidationException, DatabaseException
from decimal import Decimal


class GamblingCLI:
    """Command-line interface for the gambling simulation system"""
    
    def __init__(self):
        self.current_gambler_id = None
        self.current_gambler = None
        Database.init()
    
    def clear_screen(self):
        """Clear the screen"""
        print("\n" * 2)
    
    def show_main_menu(self):
        """Display main menu"""
        print("=" * 60)
        print("🎰 GAMBLING SIMULATION SYSTEM")
        print("=" * 60)
        print("\n1. Create Gambler")
        print("2. Select Gambler")
        print("3. View Current Gambler Info")
        print("4. Initialize Stake")
        print("5. Place a Single Bet")
        print("6. Place Multiple Consecutive Bets")
        print("7. View Betting History")
        print("8. View Stake Statistics")
        print("9. View Betting Statistics")
        print("10. Exit")
        print("\n" + "=" * 60)
    
    def create_gambler(self):
        """Create a new gambler"""
        self.clear_screen()
        print("CREATE NEW GAMBLER")
        print("-" * 60)
        
        try:
            username = input("Username: ").strip()
            full_name = input("Full Name: ").strip()
            email = input("Email: ").strip()
            
            initial_stake_input = input("Initial Stake (e.g., 1000.00): ").strip()
            win_threshold_input = input("Win Threshold (e.g., 5000.00): ").strip()
            loss_threshold_input = input("Loss Threshold (e.g., 100.00): ").strip()
            min_required_input = input("Min Required Stake (e.g., 50.00): ").strip()
            
            gambler_create = GamblerCreate(
                username=username,
                full_name=full_name,
                email=email,
                initial_stake=Decimal(initial_stake_input),
                win_threshold=Decimal(win_threshold_input),
                loss_threshold=Decimal(loss_threshold_input),
                min_required_stake=Decimal(min_required_input)
            )
            
            gambler = GamblerService.create_gambler(gambler_create)
            
            self.current_gambler_id = gambler['gambler_id']
            self.current_gambler = gambler
            
            print(f"\n✓ Gambler created successfully!")
            print(f"  Gambler ID: {gambler['gambler_id']}")
            print(f"  Username: {gambler['username']}")
            print(f"  Initial Stake: ${gambler['initial_stake']}")
            
            # Auto-initialize stake
            StakeService.initialize_stake(self.current_gambler_id)
            print(f"✓ Stake initialized: ${gambler['initial_stake']}")
            
        except ValidationException as e:
            print(f"✗ Validation Error: {e}")
            logger.error(f"Validation error: {e}")
        except DatabaseException as e:
            print(f"✗ Database Error: {e}")
            logger.error(f"Database error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def select_gambler(self):
        """Select a gambler by ID"""
        self.clear_screen()
        print("SELECT GAMBLER")
        print("-" * 60)
        
        try:
            gambler_id_input = input("Enter Gambler ID: ").strip()
            gambler_id = int(gambler_id_input)
            
            gambler = GamblerService.get_gambler_profile(gambler_id)
            
            self.current_gambler_id = gambler_id
            self.current_gambler = gambler
            
            print(f"\n✓ Gambler selected!")
            print(f"  ID: {gambler['gambler_id']}")
            print(f"  Username: {gambler['username']}")
            print(f"  Full Name: {gambler['full_name']}")
            print(f"  Current Stake: ${gambler['current_stake']}")
            
        except ValueError:
            print("✗ Invalid gambler ID")
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_gambler_info(self):
        """View current gambler information"""
        self.clear_screen()
        
        if not self.current_gambler_id:
            print("✗ No gambler selected. Please select a gambler first.")
            input("\nPress Enter to continue...")
            return
        
        try:
            gambler = GamblerService.get_gambler_profile(self.current_gambler_id)
            current_stake = StakeService.get_current_balance(self.current_gambler_id)
            
            print("GAMBLER INFORMATION")
            print("-" * 60)
            print(f"ID: {gambler['gambler_id']}")
            print(f"Username: {gambler['username']}")
            print(f"Full Name: {gambler['full_name']}")
            print(f"Email: {gambler['email']}")
            print(f"Initial Stake: ${gambler['initial_stake']}")
            print(f"Current Stake: ${current_stake}")
            print(f"Win Threshold: ${gambler['win_threshold']}")
            print(f"Loss Threshold: ${gambler['loss_threshold']}")
            print(f"Min Required Stake: ${gambler['min_required_stake']}")
            print(f"Active: {gambler['is_active']}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def place_single_bet(self):
        """Place a single bet"""
        self.clear_screen()
        
        if not self.current_gambler_id:
            print("✗ No gambler selected. Please select a gambler first.")
            input("\nPress Enter to continue...")
            return
        
        try:
            print("PLACE A SINGLE BET")
            print("-" * 60)
            
            current_stake = BettingService.get_current_stake(self.current_gambler_id)
            print(f"Current Stake: ${current_stake}\n")
            
            bet_amount_input = input("Bet Amount: $").strip()
            probability_input = input("Win Probability (0.0 to 1.0, e.g., 0.5): ").strip()
            
            bet_amount = Decimal(bet_amount_input)
            win_probability = float(probability_input)
            
            # Place and resolve bet
            result = BettingService.place_and_resolve_bet(
                self.current_gambler_id,
                bet_amount,
                win_probability
            )
            
            print(f"\n{'=' * 60}")
            print(f"BET RESULT: {'🎉 WIN!' if result['is_win'] else '❌ LOSS'}")
            print(f"{'=' * 60}")
            print(f"Bet Amount: ${result['bet_amount']}")
            print(f"Stake Before: ${result['stake_before']}")
            print(f"Stake After: ${result['stake_after']}")
            print(f"Outcome: {'+' if result['is_win'] else '-'}${abs(result['amount_won_lost'])}")
            
        except ValueError:
            print("✗ Invalid input. Please enter valid numbers.")
        except ValidationException as e:
            print(f"✗ Validation Error: {e}")
        except DatabaseException as e:
            print(f"✗ Database Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def place_consecutive_bets(self):
        """Place multiple consecutive bets"""
        self.clear_screen()
        
        if not self.current_gambler_id:
            print("✗ No gambler selected. Please select a gambler first.")
            input("\nPress Enter to continue...")
            return
        
        try:
            print("PLACE CONSECUTIVE BETS")
            print("-" * 60)
            
            current_stake = BettingService.get_current_stake(self.current_gambler_id)
            print(f"Current Stake: ${current_stake}\n")
            
            num_bets_input = input("Number of Bets: ").strip()
            bet_amount_input = input("Bet Amount per Bet: $").strip()
            probability_input = input("Win Probability (0.0 to 1.0, e.g., 0.5): ").strip()
            
            num_bets = int(num_bets_input)
            bet_amount = Decimal(bet_amount_input)
            win_probability = float(probability_input)
            
            # Place consecutive bets
            results, summary = BettingService.consecutive_bets(
                self.current_gambler_id,
                bet_amount,
                win_probability,
                num_bets
            )
            
            print(f"\n{'=' * 60}")
            print("BETTING SUMMARY")
            print(f"{'=' * 60}")
            
            for i, result in enumerate(results, 1):
                print(f"\nBet {i}: {'🎉 WIN' if result['is_win'] else '❌ LOSS'} - "
                      f"Stake: ${result['stake_after']}")
            
            print(f"\n{'-' * 60}")
            print(f"Total Bets: {summary['total_bets']}")
            print(f"Wins: {summary['wins']}")
            print(f"Losses: {summary['losses']}")
            print(f"Final Stake: ${summary['final_stake']}")
            
        except ValueError:
            print("✗ Invalid input. Please enter valid numbers.")
        except ValidationException as e:
            print(f"✗ Validation Error: {e}")
        except DatabaseException as e:
            print(f"✗ Database Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_betting_history(self):
        """View betting history"""
        self.clear_screen()
        
        if not self.current_gambler_id:
            print("✗ No gambler selected. Please select a gambler first.")
            input("\nPress Enter to continue...")
            return
        
        try:
            history = BettingService.get_gambler_betting_history(self.current_gambler_id, limit=10)
            
            print("BETTING HISTORY (Last 10 Bets)")
            print("-" * 60)
            
            if not history:
                print("No bets placed yet.")
            else:
                for bet in history:
                    status = f"{'✓ SET' if bet['is_settled'] else '‣ UNSETTLED'}"
                    result = f"{bet['bet_result']}" if bet['bet_result'] else "PENDING"
                    print(f"\nBet {bet['bet_id']}: ${bet['bet_amount']} @ {bet['win_probability']:.1%} "
                          f"- {status} ({result})")
            
        except DatabaseException as e:
            print(f"✗ Database Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_stake_statistics(self):
        """View stake statistics"""
        self.clear_screen()
        
        if not self.current_gambler_id:
            print("✗ No gambler selected. Please select a gambler first.")
            input("\nPress Enter to continue...")
            return
        
        try:
            stats = StakeService.get_stake_statistics(self.current_gambler_id)
            
            print("STAKE STATISTICS")
            print("-" * 60)
            print(f"Initial Balance: ${stats['initial_balance']}")
            print(f"Current Balance: ${stats['current_balance']}")
            print(f"Peak Balance: ${stats['peak_balance']}")
            print(f"Lowest Balance: ${stats['lowest_balance']}")
            print(f"Net Change: ${stats['net_change']}")
            print(f"Volatility: ${stats['volatility']}")
            print(f"Total Transactions: {stats['total_transactions']}")
            print(f"Wins: {stats['win_count']}")
            print(f"Losses: {stats['loss_count']}")
            print(f"Deposits: {stats['deposit_count']}")
            print(f"Withdrawals: {stats['withdrawal_count']}")
            
        except DatabaseException as e:
            print(f"✗ Database Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_betting_statistics(self):
        """View betting statistics"""
        self.clear_screen()
        
        if not self.current_gambler_id:
            print("✗ No gambler selected. Please select a gambler first.")
            input("\nPress Enter to continue...")
            return
        
        try:
            stats = BettingService.get_betting_statistics(self.current_gambler_id)
            
            print("BETTING STATISTICS")
            print("-" * 60)
            print(f"Total Bets: {stats['total_bets']}")
            print(f"Wins: {stats['win_count']}")
            print(f"Losses: {stats['loss_count']}")
            print(f"Unsettled: {stats['unsettled_count']}")
            print(f"Total Wagered: ${stats['total_wagered']}")
            print(f"Average Bet: ${stats['avg_bet']}")
            
            if stats['total_bets'] > 0:
                win_rate = (stats['win_count'] / (stats['win_count'] + stats['loss_count'])) * 100 if (stats['win_count'] + stats['loss_count']) > 0 else 0
                print(f"Win Rate: {win_rate:.1f}%")
            
        except DatabaseException as e:
            print(f"✗ Database Error: {e}")
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the CLI"""
        while True:
            self.clear_screen()
            self.show_main_menu()
            
            choice = input("Enter your choice (1-10): ").strip()
            
            match choice:
                case "1":
                    self.create_gambler()
                case "2":
                    self.select_gambler()
                case "3":
                    self.view_gambler_info()
                case "4":
                    if self.current_gambler_id:
                        try:
                            StakeService.initialize_stake(self.current_gambler_id)
                            print("\n✓ Stake initialized successfully!")
                        except Exception as e:
                            print(f"\n✗ Error: {e}")
                        input("\nPress Enter to continue...")
                    else:
                        print("\n✗ No gambler selected. Please select a gambler first.")
                        input("\nPress Enter to continue...")
                case "5":
                    self.place_single_bet()
                case "6":
                    self.place_consecutive_bets()
                case "7":
                    self.view_betting_history()
                case "8":
                    self.view_stake_statistics()
                case "9":
                    self.view_betting_statistics()
                case "10":
                    print("\n👋 Goodbye!")
                    break
                case _:
                    print("\n✗ Invalid choice. Please enter 1-10.")
                    input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    try:
        cli = GamblingCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
