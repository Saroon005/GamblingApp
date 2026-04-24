from core.logger import logger
from core.exceptions import ValidationException
from modules.gambler.validator import GamblerValidator
from modules.gambler.repository import GamblerRepository
from decimal import Decimal


class GamblerService:
    @staticmethod
    def create_gambler(gambler_create):
        logger.info(f"Creating gambler with username: {gambler_create.username}")
        
        # Validate creation data
        GamblerValidator.validate_creation_data(gambler_create)
        
        # Create gambler
        gambler_data = GamblerRepository.create(gambler_create)
        
        logger.info(f"Gambler created successfully: {gambler_data['gambler_id']}")
        return gambler_data
    
    @staticmethod
    def get_gambler_profile(gambler_id: int):
        logger.info(f"Retrieving gambler profile: {gambler_id}")
        
        gambler = GamblerRepository.get_by_id(gambler_id)
        
        logger.info(f"Gambler profile retrieved: {gambler_id}")
        return gambler
    
    @staticmethod
    def update_gambler(gambler_id: int, gambler_update):
        logger.info(f"Updating gambler: {gambler_id}")
        
        gambler = GamblerRepository.update(gambler_id, gambler_update)
        
        logger.info(f"Gambler updated successfully: {gambler_id}")
        return gambler
    
    @staticmethod
    def check_eligibility(gambler_id: int) -> bool:
        logger.info(f"Checking eligibility for gambler: {gambler_id}")
        
        gambler = GamblerRepository.get_by_id(gambler_id)
        
        is_eligible = GamblerValidator.validate_eligibility(
            gambler['current_stake'],
            gambler['min_required_stake']
        )
        
        logger.info(f"Gambler {gambler_id} eligibility: {is_eligible}")
        return is_eligible
    
    @staticmethod
    def reset_gambler_profile(gambler_id: int):
        logger.info(f"Resetting gambler profile: {gambler_id}")
        
        gambler = GamblerRepository.reset(gambler_id)
        
        logger.info(f"Gambler profile reset successfully: {gambler_id}")
        return gambler
