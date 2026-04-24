import random
from decimal import Decimal
from core.logger import logger
from core.exceptions import ValidationException, DatabaseException, InvalidBetException
from modules.betting.validator import BettingValidator
from modules.betting.repository import BettingRepository
from modules.betting.strategies import StrategyFactory
from modules.stake.service import StakeService
from modules.gambler.repository import GamblerRepository


class BettingService:
    
    @staticmethod
    def place_bet(gambler_id: int, bet_amount: Decimal, win_probability: float, 
                  game_index: int = 1):
        """Place a single bet without strategy"""
        logger.info(f"Placing bet for gambler {gambler_id}: amount=${bet_amount}, "
                   f"probability={win_probability:.1%}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            # Get current stake from UC2
            current_stake = StakeService.get_current_balance(gambler_id)
            
            # Validate bet
            BettingValidator.validate_place_bet(gambler_id, Decimal(str(bet_amount)), 
                                               win_probability, current_stake)
            BettingValidator.validate_win_probability(win_probability)
            BettingValidator.validate_game_index(game_index)
            
            # Record bet in database
            bet = BettingRepository.place_bet(
                gambler_id=gambler_id,
                bet_amount=Decimal(str(bet_amount)),
                win_probability=win_probability,
                game_index=game_index,
                stake_before=current_stake
            )
            
            logger.info(f"Bet placed successfully: bet_id={bet['bet_id']}")
            return bet
        
        except ValidationException:
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error placing bet: {e}")
            raise DatabaseException(f"Error placing bet: {e}")
    
    @staticmethod
    def resolve_bet(bet_id: int):
        """Resolve a bet by determining win/loss and updating stake"""
        logger.info(f"Resolving bet: {bet_id}")
        
        try:
            # Get bet details
            bet = BettingRepository.get_bet_by_id(bet_id)
            
            if bet['is_settled']:
                raise InvalidBetException(f"Bet {bet_id} is already settled")
            
            # Determine outcome using random probability
            is_win = random.random() < bet['win_probability']
            
            logger.info(f"Bet {bet_id} outcome: {'WIN' if is_win else 'LOSS'} "
                       f"(probability: {bet['win_probability']:.1%})")
            
            # Record bet result in database
            settled_bet = BettingRepository.settle_bet(bet_id, is_win)
            
            # Update stake using UC2
            result_transaction = StakeService.process_bet_outcome(
                gambler_id=bet['gambler_id'],
                bet_amount=bet['bet_amount'],
                is_win=is_win,
                bet_id=bet_id,
                game_id=bet['game_index']
            )
            
            # Return result
            result = {
                'bet_id': bet_id,
                'is_win': is_win,
                'bet_amount': bet['bet_amount'],
                'stake_before': result_transaction['balance_before'],
                'stake_after': result_transaction['balance_after'],
                'amount_won_lost': bet['bet_amount'] if is_win else -bet['bet_amount']
            }
            
            logger.info(f"Bet resolved: {result}")
            return result
        
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error resolving bet: {e}")
            raise DatabaseException(f"Error resolving bet: {e}")
    
    @staticmethod
    def place_and_resolve_bet(gambler_id: int, bet_amount: Decimal, win_probability: float,
                             game_index: int = 1):
        """Place a bet and immediately resolve it (convenience method)"""
        logger.info(f"Placing and resolving bet for gambler {gambler_id}")
        
        try:
            # Place bet
            bet = BettingService.place_bet(gambler_id, bet_amount, win_probability, game_index)
            
            # Resolve bet
            result = BettingService.resolve_bet(bet['bet_id'])
            
            return result
        
        except Exception as e:
            logger.error(f"Error placing and resolving bet: {e}")
            raise
    
    @staticmethod
    def place_bet_with_strategy(gambler_id: int, strategy_type: str, 
                               strategy_value: Decimal, win_probability: float,
                               game_index: int = 1):
        """Place a bet using a betting strategy"""
        logger.info(f"Placing bet with strategy for gambler {gambler_id}: "
                   f"strategy={strategy_type}, value={strategy_value}")
        
        try:
            # Get current stake from UC2
            current_stake = StakeService.get_current_balance(gambler_id)
            
            # Validate strategy
            BettingValidator.validate_bet_strategy(strategy_type, Decimal(str(strategy_value)), 
                                                   current_stake)
            
            # Create strategy
            strategy = StrategyFactory.create_strategy(strategy_type, Decimal(str(strategy_value)))
            
            # Calculate bet amount
            bet_amount = strategy.calculate_bet_amount(current_stake)
            
            # Place bet
            bet = BettingService.place_bet(gambler_id, bet_amount, win_probability, game_index)
            
            logger.info(f"Bet placed with strategy: bet_amount=${bet_amount}")
            return bet
        
        except ValidationException:
            raise
        except DatabaseException:
            raise
        except Exception as e:
            logger.error(f"Error placing bet with strategy: {e}")
            raise DatabaseException(f"Error placing bet with strategy: {e}")
    
    @staticmethod
    def consecutive_bets(gambler_id: int, bet_amount: Decimal, win_probability: float,
                        num_bets: int = 1):
        """Place and resolve multiple consecutive bets"""
        logger.info(f"Placing {num_bets} consecutive bets for gambler {gambler_id}")
        
        try:
            results = []
            
            for i in range(num_bets):
                try:
                    # Get current stake
                    current_stake = StakeService.get_current_balance(gambler_id)
                    
                    # Stop if stake is 0
                    if current_stake <= 0:
                        logger.info(f"Stopping bets: stake depleted (bet {i+1}/{num_bets})")
                        break
                    
                    # Adjust bet amount if necessary
                    actual_bet = min(Decimal(str(bet_amount)), current_stake)
                    
                    # Place and resolve bet
                    result = BettingService.place_and_resolve_bet(
                        gambler_id,
                        actual_bet,
                        win_probability,
                        game_index=i+1
                    )
                    
                    results.append(result)
                    
                    # Log progress
                    logger.info(f"Bet {i+1}/{num_bets} completed: "
                               f"{'WIN' if result['is_win'] else 'LOSS'}, "
                               f"New stake: ${result['stake_after']}")
                
                except Exception as e:
                    logger.error(f"Error in bet {i+1}: {e}")
                    break
            
            # Summary
            summary = {
                'total_bets': len(results),
                'wins': sum(1 for r in results if r['is_win']),
                'losses': sum(1 for r in results if not r['is_win']),
                'final_stake': results[-1]['stake_after'] if results else current_stake
            }
            
            logger.info(f"Consecutive bets summary: {summary}")
            return results, summary
        
        except Exception as e:
            logger.error(f"Error in consecutive bets: {e}")
            raise
    
    @staticmethod
    def get_bet(bet_id: int):
        """Get a single bet"""
        logger.info(f"Retrieving bet: {bet_id}")
        
        try:
            return BettingRepository.get_bet_by_id(bet_id)
        except DatabaseException:
            raise
    
    @staticmethod
    def get_gambler_betting_history(gambler_id: int, limit: int = None):
        """Get betting history for a gambler"""
        logger.info(f"Retrieving betting history for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            return BettingRepository.get_gambler_bets(gambler_id, limit)
        except DatabaseException:
            raise
    
    @staticmethod
    def get_betting_statistics(gambler_id: int) -> dict:
        """Get betting statistics for a gambler"""
        logger.info(f"Calculating betting statistics for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            return BettingRepository.get_gambler_bet_statistics(gambler_id)
        except DatabaseException:
            raise
    
    @staticmethod
    def get_current_stake(gambler_id: int) -> Decimal:
        """Get current stake for a gambler (convenience wrapper for UC2)"""
        return StakeService.get_current_balance(gambler_id)
