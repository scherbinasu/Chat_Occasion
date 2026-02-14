import re
from datetime import datetime
from hashlib import sha3_512, sha3_256
from random import choice
from typing import Literal

from sqlalchemy import String, Integer, Column, Text, ForeignKey, Enum, Float, Date, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Numeric, CheckConstraint
from decimal import Decimal

class Base(DeclarativeBase):
    pass