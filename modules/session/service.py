from decimal import Decimal
from core.logger import logger
from core.exceptions import DatabaseException
from modules.session.repository import SessionRepository
from modules.gambler.repository import GamblerRepository
from modules.stake.service import StakeService


class SessionService:
    """Simple service for session management"""
    
    @staticmethod
    def start_session(gambler_id: int):
        """Start a new session"""
        logger.info(f"Starting session for gambler {gambler_id}")
        
        try:
            # Validate gambler exists
            GamblerRepository.get_by_id(gambler_id)
            
            # Get current stake
            current_stake = StakeService.get_current_balance(gambler_id)
            
            # Create session
            session_id = SessionRepository.create_session(gambler_id, current_stake)
            
            logger.info(f"Session started: {session_id}")
            return {"session_id": session_id}
        
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            raise
    
    @staticmethod
    def end_session(session_id: int, end_reason: str):
        """End a session"""
        logger.info(f"Ending session {session_id}: reason={end_reason}")
        
        try:
            # Get session to retrieve gambler_id
            session = SessionRepository.get_session(session_id)
            
            if not session:
                raise Exception(f"Session {session_id} not found")
            
            gambler_id = session['gambler_id']
            
            # Get current stake as ending stake
            ending_stake = StakeService.get_current_balance(gambler_id)
            
            # End session in repository
            SessionRepository.end_session(session_id, end_reason, ending_stake)
            
            logger.info(f"Session ended successfully: {session_id}")
        
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            raise
    
    @staticmethod
    def get_active_session(gambler_id: int):
        """Get active session for gambler"""
        logger.info(f"Getting active session for gambler {gambler_id}")
        
        try:
            return SessionRepository.get_active_session(gambler_id)
        
        except Exception as e:
            logger.error(f"Error getting active session: {e}")
            raise
    
    @staticmethod
    def record_bet_in_session(session_id: int):
        """Record a bet was played in session"""
        try:
            SessionRepository.increment_games_played(session_id)
        
        except Exception as e:
            logger.error(f"Error recording bet in session: {e}")
            raise
