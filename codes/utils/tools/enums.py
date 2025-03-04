"""
Author: Xander Peng
Date: 2025/3/4
Description: 
"""

import enum

class AggLevel(enum.Enum):
    COUNTY = 'county'
    STATE = 'state'
    BOTH = 'both'

class Region(enum.Enum):
    CHINA = 'china'
    USA = 'usa'
    EUROPE = 'europe'

