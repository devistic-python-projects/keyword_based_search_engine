from app.utils.db import init_db
import os
db_path = os.path.join('database', 'search_engine.db')
init_db(db_path)