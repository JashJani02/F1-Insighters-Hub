import os
import fastf1
from fastf1 import get_session

CACHE_DIR = "data/cache"

os.makedirs(CACHE_DIR,exist_ok=True)

fastf1.Cache.enable_cache(CACHE_DIR)


def load_session(year:int, gp_name:str, session_type:str):

    session = get_session(year,gp_name,session_type)

    session.load()

    return session