import secrets
import string
from datetime import datetime, timedelta
from helper.database import MongoDB

class VerificationManager:
    """
    Manages the two-tier verification system:
    1. First verification (token_1) with gap time
    2. Second verification (token_2) after gap time expires
    3. Full verification after second token is used
    """
    
    async def initialize_verification_for_file(self, file_id: str, user_id: int, mongodb: MongoDB):
        """Initialize verification record for a file access"""
        verification_data = {
            "_id": f"verification_{user_id}_{file_id}",
            "user_id": user_id,
            "file_id": file_id,
            "current_step": 0,
            "token_1": None,
            "token_1_used": False,
            "token_2": None,
            "token_2_used": False,
            "gap_end": None,
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
        
        # Store in MongoDB
        await mongodb.user_data.update_one(
            {"_id": f"verification_{user_id}_{file_id}"},
            {"$set": verification_data},
            upsert=True
        )
        return verification_data
    
    @staticmethod
    def generate_token(length: int = 16) -> str:
        """Generate a secure random token"""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))
    
    async def start_first_verification(self, file_id: str, user_id: int, mongodb: MongoDB) -> str:
        """Generate token_1 and start first verification"""
        token_1 = self.generate_token()
        
        await mongodb.user_data.update_one(
            {"_id": f"verification_{user_id}_{file_id}"},
            {
                "$set": {
                    "user_id": user_id,
                    "file_id": file_id,
                    "token_1": token_1,
                    "token_1_used": False,
                    "current_step": 0,
                    "last_updated": datetime.now()
                }
            },
            upsert=True
        )
        return token_1
    
    async def verify_token_1(self, file_id: str, user_id: int, token: str, gap_time_minutes: int, mongodb: MongoDB) -> dict:
        """
        Verify token_1 and transition to step 1 with gap time
        
        Returns: {
            "success": bool,
            "message": str,
            "current_step": int,
            "gap_end": datetime
        }
        """
        ver_doc = await mongodb.user_data.find_one({"token_1": token, "token_1_used": False})
        
        if not ver_doc:
            return {"success": False, "message": "Verification record not found or token already used"}
        
        if ver_doc.get("token_1_used"):
            return {"success": False, "message": "Token already used"}
        
        if ver_doc.get("current_step") != 0:
            return {"success": False, "message": "Invalid verification state"}
        
        # Calculate gap_end time
        gap_end = datetime.now() + timedelta(minutes=gap_time_minutes)
        
        # Update verification record
        await mongodb.user_data.update_one(
            {"_id": ver_doc["_id"]},
            {
                "$set": {
                    "token_1_used": True,
                    "current_step": 1,
                    "gap_end": gap_end,
                    "last_updated": datetime.now()
                }
            }
        )
        
        return {
            "success": True,
            "message": "First verification successful",
            "current_step": 1,
            "gap_end": gap_end
        }
    
    async def start_second_verification(self, file_id: str, user_id: int, mongodb: MongoDB) -> str:
        """Generate token_2 and start second verification"""
        token_2 = self.generate_token()
        
        await mongodb.user_data.update_one(
            {"_id": f"verification_{user_id}_{file_id}"},
            {
                "$set": {
                    "token_2": token_2,
                    "token_2_used": False,
                    "last_updated": datetime.now()
                }
            },
            upsert=True
        )
        return token_2
    
    async def verify_token_2(self, file_id: str, user_id: int, token: str, mongodb: MongoDB) -> dict:
        """
        Verify token_2 and transition to step 2 (fully verified)
        
        Returns: {
            "success": bool,
            "message": str,
            "current_step": int
        }
        """
        ver_doc = await mongodb.user_data.find_one({"token_2": token, "token_2_used": False})
        
        if not ver_doc:
            return {"success": False, "message": "Verification record not found or token already used"}
        
        if ver_doc.get("token_2_used"):
            return {"success": False, "message": "Token already used"}
        
        if ver_doc.get("current_step") != 1:
            return {"success": False, "message": "Invalid verification state"}
        
        # Update verification record
        await mongodb.user_data.update_one(
            {"_id": ver_doc["_id"]},
            {
                "$set": {
                    "token_2_used": True,
                    "current_step": 2,
                    "last_updated": datetime.now()
                }
            }
        )
        
        return {
            "success": True,
            "message": "Second verification successful - fully verified",
            "current_step": 2
        }
    
    async def check_verification_status(self, file_id: str, user_id: int, mongodb: MongoDB, gap_time_minutes: int = 0) -> dict:
        """
        Check current verification status and determine next action
        Only checks user's own verification records
        
        Returns: {
            "current_step": int,  # 0 = no verification, 1 = first verified, 2 = fully verified
            "needs_first_verification": bool,
            "needs_second_verification": bool,
            "can_access_file": bool,
            "gap_expired": bool,
            "token_1": str (if needed),
            "token_2": str (if needed)
        }
        """
        ver_doc = await mongodb.user_data.find_one({
            "_id": f"verification_{user_id}_{file_id}"
        })
        
        if not ver_doc:
            # No record, needs first verification
            return {
                "current_step": 0,
                "needs_first_verification": True,
                "needs_second_verification": False,
                "can_access_file": False,
                "gap_expired": False
            }
        
        current_step = ver_doc.get("current_step", 0)
        gap_end = ver_doc.get("gap_end")
        
        if current_step == 0:
            # Needs first verification
            return {
                "current_step": 0,
                "needs_first_verification": True,
                "needs_second_verification": False,
                "can_access_file": False,
                "gap_expired": False
            }
        
        elif current_step == 1:
            # First verification done, check gap time
            if gap_end and datetime.now() < gap_end:
                # Still within gap time, can access file without second verification
                return {
                    "current_step": 1,
                    "needs_first_verification": False,
                    "needs_second_verification": False,
                    "can_access_file": True,
                    "gap_expired": False
                }
            else:
                # Gap time expired, needs second verification
                return {
                    "current_step": 1,
                    "needs_first_verification": False,
                    "needs_second_verification": True,
                    "can_access_file": False,
                    "gap_expired": True
                }
        
        elif current_step == 2:
            # Fully verified, always allow access
            return {
                "current_step": 2,
                "needs_first_verification": False,
                "needs_second_verification": False,
                "can_access_file": True,
                "gap_expired": False
            }
        
        return {
            "current_step": 0,
            "needs_first_verification": True,
            "needs_second_verification": False,
            "can_access_file": False,
            "gap_expired": False
        }
