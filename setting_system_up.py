from kb.db_filling import KnowledgeBaseSupport
from kb.docs_generating_alternative import DocsGenerationAlternative
from collections import Counter
from config import SETTINGS

# 1. Создание и заполнение БД
kb_path = SETTINGS.get('PATH_TO_KNOWLEDGEBASE')
db_file = kb_path.split('\\')[Counter(kb_path)['\\']] #для сервера
#kbs = KnowledgeBaseSupport('CLMR02.csv', db_file)
kbs = KnowledgeBaseSupport('knowledge_base_db_old.sql', db_file) #для сервера
kbs.set_up_db(overwrite=True) #для сервера

# 2. Генерация и индексация документов
# Создайте ядро, для этого в папке solr-6.3.0/bin выполните команду "solr create -c <название ядра>"
dga = DocsGenerationAlternative(core='kb_3c')
dga.clear_index()  # Удаление документов из ядра
dga.generate_docs()  # Генерация документов
dga.index_created_documents_via_curl()  # Индексация документов
# Если видете ошибку: pycurl.error: (6, 'Could not resolve: localhost (Domain name not found)')
# Или просто метод выполняется очень долго то закоментируйте строчку dga.index_created_documents()
# и раскомментируйте 2 строчки ниже
#dga.index_created_documents_via_cmd(SETTINGS.get('PATH_TO_SOLR_POST_JAR_FILE'))  # Индексация документов


# cd C:\Users\User\Desktop\solr\solr-6.3.0\solr-6.3.0\bin
# solr.cmd start -f