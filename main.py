from db.init_db import Database
from modules.gambler.schemas import GamblerCreate
from modules.gambler.service import GamblerService
from modules.stake.service import StakeService
from modules.betting.service import BettingService
from modules.session.service import SessionService
from modules.winloss.service import WinLossService
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
        print("\n" + "=" * 60)
        print("🎰 GAMBLING SIMULATION SYSTEM")
        print("=" * 60)
        print("1. Create Gambler")
        print("2. Select Gambler")
        print("3. Place Bet")
        print("4. Start Session")
        print("5. Show Statistics")
        print("6. Exit")
        print("=" * 60)
    
    def create_gambler(self):
        """Create a new gambler"""
        print("\n📝 CREATE GAMBLER")
        print("-" * 60)
        
        try:
            username = input("Username: ").strip()
            full_name = input("Full Name: ").strip()
            email = input("Email: ").strip()
            initial_stake = Decimal(input("Initial Stake ($): ").strip())
            win_threshold = Decimal(input("Win Threshold ($): ").strip())
            loss_threshold = Decimal(input("Loss Threshold ($): ").strip())
            min_required = Decimal(input("Min Bet Amount ($): ").strip())
            
            gambler_data = GamblerCreate(
                username=username,
                full_name=full_name,
                email=email,
                initial_stake=initial_stake,
                win_threshold=win_threshold,
                loss_threshold=loss_threshold,
                min_required_stake=min_required
            )
            
            gambler = GamblerService.create_gambler(gambler_data)
            StakeService.initialize_stake(gambler['gambler_id'])
            
            self.current_gambler_id = gambler['gambler_id']
            self.current_gambler = gambler
            
            print(f"\n✓ Gambler created: {gambler['username']} (ID: {gambler['gambler_id']})")
        
        except ValueError:
            print("✗ Invalid input")
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Error creating gambler: {e}")
    
    def select_gambler(self):
        """Select a gambler by ID"""
        print("\n👤 SELECT GAMBLER")
        print("-" * 60)
        
        try:
            gambler_id = int(input("Gambler ID: ").strip())
            gambler = GamblerService.get_gambler_profile(gambler_id)
            
            self.current_gambler_id = gambler_id
            self.current_gambler = gambler
            
            stake = StakeService.get_current_balance(gambler_id)
            print(f"\n✓ Selected: {gambler['username']} | Stake: ${stake}")
        
        except ValueError:
            print("✗ Invalid ID")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def place_bet(self):
        """Place a single bet"""
        print("\n💰 PLACE BET")
        print("-" * 60)
        
        if not self.current_gambler_id:
            print("✗ No gambler selected")
            return
        
        try:
            stake = StakeService.get_current_balance(self.current_gambler_id)
            print(f"Current Stake: ${stake}")
            
            amount = Decimal(input("Bet Amount ($): ").strip())
            probability = float(input("Win Probability (0-1): ").strip())
            
            result = BettingService.place_and_resolve_bet(
                self.current_gambler_id, amount, probability
            )
            
            status = "🎉 WIN" if result['is_win'] else "❌ LOSS"
            new_stake = result['stake_after']
            print(f"\n{status} | New Stake: ${new_stake}")
        
        except ValueError:
            print("✗ Invalid input")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def start_session(self):
        """Start a betting session with automatic win/loss tracking"""
        print("\n🎮 START SESSION")
        print("-" * 60)
        
        if not self.current_gambler_id:
            print("✗ No gambler selected")
            return
        
        try:
            gambler = self.current_gambler
            stake = StakeService.get_current_balance(self.current_gambler_id)
            
            print(f"Gambler: {gambler['username']}")
            print(f"Current Stake: ${stake}")
            print(f"Win Threshold: ${gambler['win_threshold']}")
            print(f"Loss Threshold: ${gambler['loss_threshold']}")
            print("\nEnter 'stop' to end session\n")
            
            # Start session and win/loss tracker
            session = SessionService.start_session(self.current_gambler_id)
            session_id = session['session_id']
            tracker = WinLossService()
            bet_count = 0
            
            while True:
                stake = BettingService.get_current_stake(self.current_gambler_id)
                print(f"\n[Bet #{bet_count + 1}] Stake: ${stake}")
                
                amount_input = input("Bet ($) or 'stop': ").strip()
                if amount_input.lower() == "stop":
                    break
                
                try:
                    amount = Decimal(amount_input)
                    prob = float(input("Probability (0-1): ").strip())
                    
                    # Place bet
                    result = BettingService.place_and_resolve_bet(
                        self.current_gambler_id, amount, prob
                    )
                    
                    # Record in session and track win/loss
                    SessionService.record_bet_in_session(session_id)
                    tracker.record_game_outcome(
                        session_id, self.current_gambler_id, result['bet_id'],
                        result['is_win'], amount, result['stake_before'], 
                        result['stake_after']
                    )
                    
                    status = "🎉 WIN" if result['is_win'] else "❌ LOSS"
                    print(f"{status} | Stake: ${result['stake_after']}")
                    
                    bet_count += 1
                    
                    # Check thresholds
                    if result['stake_after'] >= Decimal(gambler['win_threshold']):
                        print(f"\n🏆 WIN THRESHOLD REACHED!")
                        SessionService.end_session(session_id, "WIN_THRESHOLD")
                        break
                    elif result['stake_after'] <= Decimal(gambler['loss_threshold']):
                        print(f"\n💔 LOSS THRESHOLD REACHED!")
                        SessionService.end_session(session_id, "LOSS_THRESHOLD")
                        break
                
                except ValueError:
                    print("✗ Invalid input")
            
            # End session
            if bet_count > 0:
                SessionService.end_session(session_id, "MANUAL")
                stats = tracker.get_session_summary(session_id)
                
                print("\n" + "=" * 60)
                print("SESSION SUMMARY")
                print("=" * 60)
                print(f"Total Bets: {stats['total_games']}")
                print(f"Wins: {stats['total_wins']} | Losses: {stats['total_losses']}")
                print(f"Win Rate: {stats['win_rate']:.1f}%")
                print(f"Current Streak: {stats['current_win_streak'] if stats['current_win_streak'] > 0 else stats['current_loss_streak']} "
                      f"({'W' if stats['current_win_streak'] > 0 else 'L'})")
        
        except Exception as e:
            print(f"✗ Error: {e}")
            logger.error(f"Session error: {e}")
    
    def show_stats(self):
        """Show simple statistics"""
        print("\n📊 STATISTICS")
        print("-" * 60)
        
        if not self.current_gambler_id:
            print("✗ No gambler selected")
            return
        
        try:
            stake = StakeService.get_current_balance(self.current_gambler_id)
            stats = WinLossService.get_gambler_overall_stats(self.current_gambler_id)
            
            print(f"Current Stake: ${stake}")
            print(f"Total Games: {stats['total_games']}")
            print(f"Wins: {stats['total_wins']} | Losses: {stats['total_losses']}")
            print(f"Win Rate: {stats['win_rate']:.1f}%")
            print(f"Total Net Change: ${stats['total_net_change']}")
        
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def run(self):
        """Run CLI"""
        while True:
            self.show_menu()
            choice = input("\nChoice (1-6): ").strip()
            
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
                    print("\n👋 Goodbye!\n")
                    break
                case _:
                    print("✗ Invalid choice")


if __name__ == "__main__":
    cli = GamblingCLI()
    cli.run()
