from db.init_db import Database
from modules.gambler.schemas import GamblerCreate, GamblerUpdate
from modules.gambler.service import GamblerService
from core.logger import logger
from core.exceptions import ValidationException, DatabaseException, GamblerNotFoundException
from decimal import Decimal


def main():
    try:
        # Initialize database
        logger.info("Starting Gambling App...")
        Database.init()
        
        # Create a sample gambler
        logger.info("\n" + "="*60)
        logger.info("OPERATION 1: CREATE GAMBLER")
        logger.info("="*60)
        gambler_create = GamblerCreate(
            username="john_doe",
            full_name="John Doe",
            email="john@example.com",
            initial_stake=Decimal("1000.00"),
            win_threshold=Decimal("2000.00"),
            loss_threshold=Decimal("500.00"),
            min_required_stake=Decimal("100.00")
        )
        
        created_gambler = GamblerService.create_gambler(gambler_create)
        logger.info(f"\n✓ Created Gambler:")
        logger.info(f"  ID: {created_gambler['gambler_id']}")
        logger.info(f"  Username: {created_gambler['username']}")
        logger.info(f"  Full Name: {created_gambler['full_name']}")
        logger.info(f"  Email: {created_gambler['email']}")
        logger.info(f"  Initial Stake: ${created_gambler['initial_stake']}")
        logger.info(f"  Current Stake: ${created_gambler['current_stake']}")
        
        # Retrieve gambler profile
        logger.info("\n" + "="*60)
        logger.info("OPERATION 2: RETRIEVE GAMBLER PROFILE")
        logger.info("="*60)
        gambler_id = created_gambler['gambler_id']
        profile = GamblerService.get_gambler_profile(gambler_id)
        logger.info(f"\n✓ Retrieved Profile for ID {gambler_id}:")
        logger.info(f"  Username: {profile['username']}")
        logger.info(f"  Full Name: {profile['full_name']}")
        logger.info(f"  Current Stake: ${profile['current_stake']}")
        
        # Check eligibility
        logger.info("\n" + "="*60)
        logger.info("OPERATION 3: CHECK ELIGIBILITY")
        logger.info("="*60)
        is_eligible = GamblerService.check_eligibility(gambler_id)
        logger.info(f"\n✓ Eligibility Check:")
        logger.info(f"  Current Stake: ${profile['current_stake']}")
        logger.info(f"  Min Required: ${profile['min_required_stake']}")
        logger.info(f"  Is Eligible: {is_eligible}")
        
        # Update gambler
        logger.info("\n" + "="*60)
        logger.info("OPERATION 4: UPDATE GAMBLER DETAILS")
        logger.info("="*60)
        gambler_update = GamblerUpdate(
            full_name="John Updated Doe",
            min_required_stake=Decimal("150.00")
        )
        updated_gambler = GamblerService.update_gambler(gambler_id, gambler_update)
        logger.info(f"\n✓ Updated Gambler:")
        logger.info(f"  Full Name: {updated_gambler['full_name']}")
        logger.info(f"  Min Required Stake: ${updated_gambler['min_required_stake']}")
        
        # Reset gambler profile
        logger.info("\n" + "="*60)
        logger.info("OPERATION 5: RESET GAMBLER PROFILE")
        logger.info("="*60)
        reset_gambler = GamblerService.reset_gambler_profile(gambler_id)
        logger.info(f"\n✓ Profile Reset:")
        logger.info(f"  Current Stake: ${reset_gambler['current_stake']} (reset to initial)")
        logger.info(f"  Win Threshold: ${reset_gambler['win_threshold']} (2x initial)")
        logger.info(f"  Loss Threshold: ${reset_gambler['loss_threshold']} (0.5x initial)")
        
        logger.info("\n" + "="*60)
        logger.info("✓ ALL OPERATIONS COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        logger.info("\n→ You can now view the data in MySQL Workbench")
        logger.info(f"  Database: {gambler_create.full_name}")
        logger.info(f"  Table: gambler\n")
    
    except ValidationException as e:
        logger.error(f"\n✗ Validation Error: {e}")
    except DatabaseException as e:
        logger.error(f"\n✗ Database Error: {e}")
    except GamblerNotFoundException as e:
        logger.error(f"\n✗ Gambler Not Found: {e}")
    except Exception as e:
        logger.error(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
