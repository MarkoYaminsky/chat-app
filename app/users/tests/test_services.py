from app.common.test_factories import UserFactory
from app.users.services import verify_user_password


class TestVerifyUserPasswordService:
    password = "password"

    def test_successful_case(self, session):
        user = UserFactory(password=self.password)

        is_password_correct = verify_user_password(user, self.password)

        assert is_password_correct is True

    def test_failure_case(self, session):
        user = UserFactory(password=self.password)

        is_password_correct = verify_user_password(user, f"{self.password}/incorrect")

        assert is_password_correct is False
