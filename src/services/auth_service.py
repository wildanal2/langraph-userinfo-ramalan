import httpx
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

class AuthService:
    def __init__(self):
        self.url = settings.check_email_url
        self.auth = (settings.auth_username, settings.auth_password)

    async def check_email(self, email: str) -> tuple[bool, str | None]:
        """
        Check if email is available.
        Returns:
            (is_available: bool, error_message: str | None)
        """
        try:
            logger.info(f"Validating email availability for: {email}")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    auth=self.auth,
                    data={"email": email},
                    timeout=5.0
                )
                
                logger.info(f"Email validation response: {response.status_code}")
                
                if response.status_code == 200:
                    return True, None
                elif response.status_code == 409:
                    return False, "Email ini sudah terdaftar, silahkan kamu ketik ulang email yang lainnya."
                else:
                    logger.error(f"Email check failed with status {response.status_code}: {response.text}")
                    return False, "Terjadi kesalahan saat memvalidasi email. Silakan coba lagi nanti."
                        
        except httpx.TimeoutException:
            logger.error(f"Email check timed out for: {email}")
            return False, "Koneksi ke server validasi timeout. Silakan coba lagi."
        except Exception as e:
            logger.error(f"Error checking email: {e}")
            return False, "Terjadi kesalahan koneksi saat memvalidasi email."
