from typing import Any

import factory

from app.auth.services import hash_password
from app.common.utilities import get_user_model

User = get_user_model()


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def set_sqlalchemy_session(cls, session):
        cls._meta.sqlalchemy_session = session


class UserFactory(BaseFactory):
    class Meta:
        model = User

    password = "password"
    username = factory.Faker("user_name")

    @classmethod
    def _create(cls, model_class, *args, **kwargs: Any) -> User:
        password = kwargs["password"]
        kwargs["password"] = hash_password(password)
        return super()._create(model_class, *args, **kwargs)
