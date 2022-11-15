import re
import string
from pathlib import Path
from typing import ClassVar

from tinydb import TinyDB, where
from faker import Faker
from dataclasses import dataclass


@dataclass
class User:
    first_name: str
    last_name: str
    phone_number: str = ""
    address: str = ""

    DB: ClassVar[TinyDB] = TinyDB(Path(__file__).resolve().parent / "db.json", indent=4)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def db_instance(self):
        return User.DB.get((where("first_name") == self.first_name) & (where("last_name") == self.last_name))

    def __str__(self):
        return f"{self.full_name}\n{self.address}"

    def _checks(self):
        """
        Checks the validity of both names and phone_number
        Returns: None

        """
        self._check_names()
        self._check_phone_number()

    def _check_names(self):
        """
        Checks if first_name and last_name are valid
        Returns: None and raise an ValueError is the name isn't valid

        """
        if not (self.first_name and self.last_name):
            raise ValueError("Firstname and Lastname can't be empty")

        special_character = string.punctuation + string.digits

        for character in self.first_name + self.last_name:
            if character in special_character:
                raise ValueError(f"Invalid Name {self.full_name}.")

    def _check_phone_number(self):
        """
        Verify if the phone_number is valid

        Returns: None

        """
        phone_number = re.sub(r"[+()\s]*", "", self.phone_number)
        if len(phone_number) < 10 or not phone_number.isdigit():
            raise ValueError(f"Invalid Phone Number {self.phone_number}.")

    def exists(self):
        """
        Verify if a user exist in the database
        Returns: bool

        """
        return bool(self.db_instance)

    def delete(self) -> list[int]:
        """
        Remove user from the database
        Returns: a list of the user id removed

        """
        if self.exists():
            return User.DB.remove(doc_ids=[self.db_instance.doc_id])
        return []

    def save(self, validate_data: bool = False) -> int:
        """
        Save user in the database
        Args:
            validate_data: bool

        Returns: the id of the user in the database

        """
        if validate_data:
            self._checks()
        if self.exists():
            return -1
        else:
            return User.DB.insert(self.__dict__)


def get_all_user() -> list:
    """
    Get all the users from the database

    Returns: a list of users

    """
    return [User(**user) for user in User.DB.all()]


if __name__ == "__main__":
    fake = Faker(locale="en-US")
    martin = User("Teesa", "Brke")
    print(martin.exists())
    user = User(fake.first_name(), fake.last_name(), fake.phone_number(), fake.address())
    print(user)
    print(user.save())
    print("-" * 10)
