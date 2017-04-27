from kb.db_filling import KnowledgeBaseSupport
from kb.docs_generating_alternative import DocsGenerationAlternative
from collections import Counter
from config import PATH_TO_DB_DIMA, PATH_TO_DB_SERVER

# 1. Создание и заполнение БД
#db_file = PATH_TO_DB_SERVER.split('\\')[Counter(PATH_TO_DB_SERVER)['\\']]
# kbs = KnowledgeBaseSupport('CLMR02, CLQR01, CRDO01.csv', db_file)
#kbs = KnowledgeBaseSupport('knowledge_base.db.sql', db_file)
#kbs.set_up_db(overwrite=True)

# 2. Генерация и индексация документов
# Создайте ядро, для этого в папке solr-6.3.0/bin выполните команду "solr create -c <название ядра>"
dga = DocsGenerationAlternative(core='kb_3c')
# dga.clear_index() # Удаление документов из ядра
#dga.generate_docs()  # Генерация документов
dga.index_created_documents_via_curl() # Индексация документов
# Если видете ошибку: pycurl.error: (6, 'Could not resolve: localhost (Domain name not found)')
# Или просто метод выполняется очень долго то закоментируйте строчку dga.index_created_documents()
# и раскомментируйте 2 строчки ниже
#from config import PATH_TO_SOLR_POST_JAR_FILE_DIMA,PATH_TO_SOLR_POST_JAR_FILE_SERVER # в конфиге добавьте ваш путь до post.jar файла
#dga.index_created_documents_via_cmd(PATH_TO_SOLR_POST_JAR_FILE_SERVER) # Индексация документов
