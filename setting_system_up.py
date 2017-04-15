from kb.docs_generating_alternative import generate_docs
from kb.db_filling import KnowledgeBaseSupport
from collections import Counter
from config import PATH_TO_DB_DIMA

db_file = PATH_TO_DB_DIMA.split('\\')[Counter(PATH_TO_DB_DIMA)['\\']]
# kbs = KnowledgeBaseSupport('CLMR02, CLQR01, CRDO01.csv', db_file)
kbs = KnowledgeBaseSupport('knowledge_base.db.sql', db_file)
kbs.set_up_db()
