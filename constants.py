from json import dumps

# Strings for 1m_main
START_MSG = '''
Я - экспертная система Datatron😊 Со мной вы можете быстро получить доступ к финансовым данным как России в целом, так и любого ее региона.

Для работы в кнопочном режиме нажмите /search. Кроме того, вы также можете ввести запрос с помощью текстового или голосового сообщения.

<b>Текстовый режим</b>
После команды /search через пробел напишите ваш запрос. Примеры:

<code>/search расходы Москвы на спорт в 2013 году
/search дефицит Ярославской области</code>

<b>Голосовой режим</b>
Воспользуйтесь встроенной в Telegram записью голоса.'''

HELP_MSG = '''<b>Описание:</b>
Дататрон предоставляет пользователю доступ к открытым финансовым данным России и её субъектов.

<b>Функционал:</b>
Доступны inline-режим, кнопочный ввод, обработка естественного языка и голосовой ввод.

<b>Разработчики:</b>
Студенты Высшей школы экономики с факультетов Бизнес-информатики и Программной инженерии, которые стараются изменить мир к лучшему.

<b>Обратная связь</b>
Для нас важно ваше мнение о работе Datatron. Вы можете оставить отзыв о боте, написав на почту datatron.bot@gmail.com или нажав кнопку "Оценить".

<b>Дополнительно:</b>
Использует <a href="https://tech.yandex.ru/speechkit/cloud/">Yandex SpeechKit Cloud</a>.'''

ERROR_CANNOT_UNDERSTAND_VOICE = 'Не удалось распознать текст сообщения😥 Попробуйте еще раз!'
ERROR_NULL_DATA_FOR_SUCH_REQUEST_LONG = 'К сожалению, этих данных у меня нет🤕 Не отчаивайтесь! Есть много ' \
                                        'других цифр😉 Нажмите /search'
ERROR_NULL_DATA_FOR_SUCH_REQUEST_SHORT = 'К сожалению, этих данных в системе нет🤕'
ERROR_SERVER_DOES_NOT_RESPONSE = 'К сожалению, сейчас сервер не доступен😩 Попробуйте снова чуть позже!'

MSG_WE_WILL_FORM_DATA_AND_SEND_YOU = "Спасибо! Сейчас я сформирую ответ и отправлю его вам🙌"

HELP_KEYBOARD = dumps({
    'inline_keyboard': [
        [
            {'text': 'Inline-режим', 'callback_data': '',
             'switch_inline_query': 'расходы Ростовской области на социальную политику в прошлом году'},
            {'text': 'Оценить', 'url': 'https://telegram.me/storebot?start=datatron_bot'}
        ],
        [
            {'text': 'Руководство пользователя', 'callback_data': 'full_documentation'},
        ],
        [
            {'text': 'Ознакомительный ролик', 'callback_data': 'intro_video'}
        ]
    ]
})

# for m1_req neural network
KEY_WORDS = ('год',
             'налоговые',
             'неналоговые',
             'текущий',
             'прошлый',
             'доход',
             'расход',
             'дефицит',
             'плановый',
             'фактический',
             'этот',
             'россия',
             'рф',
             'алания',
             'северо-кавказский',
             'югра',
             'ставропольский',
             'ставрополье',
             'ингушетия',
             'дагестан',
             'кабардино-балкарская',
             'осетия',
             'карачаево-черкесская',
             'чеченская',
             'чечня',
             'южный',
             'краснодарский',
             'астраханская',
             'волгоградская',
             'ростовская',
             'адыгея',
             'калмыкия',
             'приволжский',
             'нижегородская',
             'кировская',
             'самарская',
             'оренбургская',
             'пензенская',
             'пермский',
             'саратовская',
             'ульяновская',
             'башкортостан',
             'марий',  # meant 'марий эл'
             'мордовия',
             'татарстан',
             'удмуртская', 'удмуртия',
             'чувашская', 'чувашия',
             'северо-западный',
             'архангельская',
             'ненецкий',
             'вологодская',
             'калининградская',
             'санкт-петербург',
             'ленинградская',
             'мурманская',
             'новгородская',
             'псковская',
             'карелия',
             'коми',
             'сибирский',
             'алтайский',
             'красноярский',
             'кемеровская',
             'иркутская',
             'новосибирская',
             'омская',
             'томская',
             'забайкальский',
             'бурятия',
             'алтай',
             'тыва',
             'тува',
             'хакасия',
             'уральский',
             'курганская',
             'свердловская',
             'тюменская',
             'ханты-мансийский',
             'ямало-ненецкий',
             'челябинская',
             'центральный',
             'белгородская',
             'брянская',
             'владимирская',
             'воронежская',
             'ивановская',
             'тверская',
             'калужская',
             'костромская',
             'курская',
             'липецкая',
             'москва',
             'московская',
             'орловская',
             'рязанская',
             'смоленская',
             'тамбовская',
             'тульская',
             'ярославская',
             'дальневосточный',
             'приморский',
             'хабаровский',
             'амурская',
             'камчатский',
             'магаданская',
             'сахалинская',
             'чукотский',
             'саха', 'якутия',
             'еврейская',
             'крымский',
             'крым',
             'севастополь',
             'байконур',  # sections of rev and cons
             'общегосударственные',
             'оборона',
             'безопасность',
             'экономика',
             'жкх',
             'окружающей',
             'образование',
             'культура',
             'здравоохранение',
             'социальная',
             'спорт')

USELESS_PILE_OF_CRAP = (
    'в', 'без', 'до', 'из', 'к', 'на', 'по', 'о', 'от', 'перед', 'при', 'через', 'с', 'у', 'за', 'над', 'об', 'под',
    'про', 'для', 'не',
    'республика', 'республики',
    'республики', 'республик',
    'республике', 'республикам',
    'республику', 'республики',
    'республикой',
    'республикою', 'республиками',
    'республике', 'республиках',
    'область', 'области', 'областью', 'областей', 'областям', 'областями', 'областях',
    'автономный', 'автономного', 'автономному', 'автономного', 'автономным', 'автономном', 'автномном', 'автономная',
    'автономной', 'автономную', 'автономною', 'автономна', 'автономные', 'автономных', 'автономными',
    'федеральный', 'федерального', 'федеральному', 'федеральным', 'федеральном', 'федерален', 'федеральных',
    'федеральным', 'федеральными',
    'край', 'края', 'краю', 'краем', 'крае', 'краев', 'краям', 'краями', 'краях')

SPHERE = ('налоговые', 'неналоговые')

HELLO = ('хай',
         'привет',
         'здравствуйте',
         'приветствую',
         'прифки',
         'дратути',
         'hello')

HELLO_ANSWER = ('Привет! Начни работу со мной командой /search или сделай голосовой запрос',
                'Здравствуйте! Самое время ввести команду /search',
                'Приветствую!',
                'Здравствуйте! Пришли за финансовыми данными? Задайте мне вопрос!',
                'Доброго времени суток! С вами Datatron😊, и мы начинаем /search')

HOW_ARE_YOU = ('дела', 'поживаешь', 'жизнь')

HOW_ARE_YOU_ANSWER = ('У меня все отлично, спасибо :-)',
                      'Все хорошо! Дела идут в гору',
                      'Замечательно!',
                      'Бывало и лучше! Без твоих запросов только и делаю, что прокрастинирую🙈',
                      'Чудесно! Данные расходятся, как горячие пирожки! 😄')

# dictionaries for m2_main
MAPPERS = {
    # Expenditures' mappers
    '2.2.0.1.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-3])',
    '2.2.0.0.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-1],[Marks].[03-3])',
    '2.2.0.1.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-3])',
    '2.2.0.0.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Marks].[03-3])',
    '2.3.0.1.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[MARKS].[03-4])',
    '2.3.0.1.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-4])',
    '2.4.0.0.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Marks].[03-4])',
    '2.4.0.0.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-1],[Marks].[03-4])',

    # Profits' mappers
    '3.2.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [INYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-1])',
    '3.2.1.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*2} dimension properties [KDGROUPS].[Tab1],[Tab2],[Tab3] ON ROWS FROM [INYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-1])',
    '3.2.1.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*2} dimension properties [KDGROUPS].[Tab1],[Tab2],[Tab3] ON ROWS FROM [INYR03.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Years].[*3],[Marks].[03-1])',
    '3.2.1.0.0.0': 'SELECT {[Measures].[PLANONYEAR]} ON COLUMNS FROM [CLDO01.DB] WHERE ([BIFB].[*2])',
    '3.2.0.0.0.0': 'SELECT {[Measures].[PLANONYEAR]} ON COLUMNS, {[BIFB].[25-1]} ON ROWS FROM [CLDO01.DB]',
    '3.2.0.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [INYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Marks].[03-1],[Territories].[*5])',
    '3.2.0.0.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [INDO01.DB] WHERE ([BGLevels].[09-3],[Marks].[03-1],[Territories].[*5])',
    '3.2.1.0.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*2} dimension properties [KDGROUPS].[Tab1],[Tab2],[Tab3] ON ROWS FROM [INDO01.DB] WHERE ([BGLevels].[09-3],[Marks].[03-1],[Territories].[*5])',
    '3.3.1.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*2} dimension properties [KDGROUPS].[Tab1],[Tab2],[Tab3] ON ROWS FROM [INYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-2])',
    '3.3.1.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*2} dimension properties [KDGROUPS].[Tab1],[Tab2],[Tab3] ON ROWS FROM [INYR03.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Years].[*3],[Marks].[03-2])',
    '3.3.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [INYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-2])',
    '3.3.0.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [INYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Marks].[03-2],[Territories].[*5])',
    '3.4.0.0.0.0': 'SELECT {[Measures].[FACTBGYEAR]} ON COLUMNS, {[BIFB].[25-1]} ON ROWS FROM [CLDO01.DB]',
    '3.4.1.0.0.0': 'SELECT {[Measures].[FACTBGYEAR]} ON COLUMNS FROM [CLDO01.DB] WHERE ([BIFB].[*2])',
    '3.4.0.0.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [INDO01.DB] WHERE ([BGLevels].[09-3],[Marks].[03-2],[Territories].[*5])',
    '3.4.1.0.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*2} dimension properties [KDGROUPS].[Tab1],[Tab2],[Tab3] ON ROWS FROM [INDO01.DB] WHERE ([BGLevels].[09-3],[Marks].[03-2],[Territories].[*5])',

    # Deficit/surplus's mappers
    '4.2.0.0.0.0': 'SELECT {[Measures].[PLANONYEAR]} ON COLUMNS FROM [CLDO01.DB] WHERE ([BIFB].[25-20])',
    '4.2.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-1],[Marks].[03-5],[Years].[*3])',
    '4.2.0.0.0.1': 'SELECT {[Measures].[PLAN_ONYEAR]} ON COLUMNS FROM [CLDO02.DB] WHERE ([BGLevels].[09-3],[Marks].[03-6],[Territories].[*5])',
    '4.2.0.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Marks].[03-5],[Years].[*3])',
    '4.3.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-1], [Marks].[03-6],[Years].[*3])',
    '4.3.0.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-6])',
    '4.4.0.0.0.0': 'SELECT {[Measures].[FACTBGYEAR]} ON COLUMNS FROM [CLDO01.DB] WHERE ([BIFB].[25-20])',
    '4.4.0.0.0.1': 'SELECT {[Measures].[FACT_BGYEAR]} ON COLUMNS FROM [CLDO02.DB] WHERE ([BGLevels].[09-3],[Marks].[03-6],[Territories].[*5])'
}

PARAM2 = {

    'налоговый': ('[KDGROUPS].[05-12], [KDGROUPS].[05-19], [KDGROUPS].[05-23], [KDGROUPS].[05-20], '
                  '[KDGROUPS].[05-21], [KDGROUPS].[05-22], [KDGROUPS].[05-33], [KDGROUPS].[05-34], '
                  '[KDGROUPS].[05-35], [KDGROUPS].[05-36]', '25-6'),
    'неналоговый': ('[KDGROUPS].[05-13], [KDGROUPS].[05-25], [KDGROUPS].[05-26], [KDGROUPS].[05-27], '
                    '[KDGROUPS].[05-28], [KDGROUPS].[05-29], [KDGROUPS].[05-30], [KDGROUPS].[05-31], '
                    '[KDGROUPS].[05-32], [KDGROUPS].[05-37]', '25-7')
}

SPHERES = {
    'null': '[RZPR], [RZPR].[14-848223],[RZPR].[14-413284],[RZPR].[14-850484],[RZPR].[14-848398],'
            '[RZPR].[14-848260],[RZPR].[14-1203414],[RZPR].[14-848266],[RZPR].[14-848294],'
            '[RZPR].[14-848302],[RZPR].[14-848345],[RZPR].[14-1203401],[RZPR].[14-413259],'
            '[RZPR].[14-413264],[RZPR].[14-413267],[RZPR].[14-1203208],[RZPR].[14-1203195]',

    # общегосударственные вопросы
    '2': '[RZPR].[14-848223],[RZPR].[14-413272],[RZPR].[14-342647],'
         '[RZPR].[14-413273],[RZPR].[14-413274],[RZPR].[14-413275],'
         '[RZPR].[14-413276],[RZPR].[14-413277],[RZPR].[14-413278],'
         '[RZPR].[14-413279],[RZPR].[14-848224],[RZPR].[14-413281],'
         '[RZPR].[14-413282],[RZPR].[14-848249]',

    # национальная оборона
    '3': '[RZPR].[14-413284],[RZPR].[14-413285],[RZPR].[14-413286],[RZPR].[14-413287],'
         '[RZPR].[14-413288],[RZPR].[14-413289],[RZPR].[14-413290],[RZPR].[14-413291]',

    # национальная безопасность и правоохранительная деятельность
    '4': '[RZPR].[14-850484],[RZPR].[14-413293],[RZPR].[14-413294],[RZPR].[14-853732],'
         '[RZPR].[14-413296],[RZPR].[14-855436],[RZPR].[14-854333],[RZPR].[14-854342],'
         '[RZPR].[14-854482],[RZPR].[14-108129],[RZPR].[14-852920],[RZPR].[14-850760],'
         '[RZPR].[14-1203368],[RZPR].[14-853005],[RZPR].[14-850485]',

    # национальная экономика
    '5': '[RZPR].[14-848398],[RZPR].[14-848399],[RZPR].[14-1203160],'
         '[RZPR].[14-850771],[RZPR].[14-857652],[RZPR].[14-850172],'
         '[RZPR].[14-849065],[RZPR].[14-849070],[RZPR].[14-851151],'
         '[RZPR].[14-1203167],[RZPR].[14-1203168],[RZPR].[14-1203169],'
         '[RZPR].[14-848501]',

    # жилищно-коммунальное хозяйство
    '6': '[RZPR].[14-848260],[RZPR].[14-848261],[RZPR].[14-850428],'
         '[RZPR].[14-1203187],[RZPR].[14-881303],[RZPR].[14-849768]',

    # охрана окружающей среды
    '7': '[RZPR].[14-1203414],[RZPR].[14-1203191],[RZPR].[14-872910],'
         '[RZPR].[14-872714],[RZPR].[14-848836]',

    # образование
    '8': '[RZPR].[14-848266],[RZPR].[14-848267],[RZPR].[14-849320],'
         '[RZPR].[14-343261],[RZPR].[14-848274],[RZPR].[14-849333],'
         '[RZPR].[14-873227],[RZPR].[14-850050],[RZPR].[14-849520],'
         '[RZPR].[14-849303]',

    # культура, кинематография
    '9': '[RZPR].[14-848294],[RZPR].[14-848295],[RZPR].[14-873473],'
         '[RZPR].[14-873499],[RZPR].[14-873512]',

    # здравоохранение
    '10': '[RZPR].[14-848302],[RZPR].[14-872659],[RZPR].[14-848317],'
          '[RZPR].[14-343881],[RZPR].[14-108717],[RZPR].[14-349151],'
          '[RZPR].[14-349155],[RZPR].[14-349159],[RZPR].[14-849621],'
          '[RZPR].[14-349163]',

    # социальная политика
    '11': '[RZPR].[14-848345],[RZPR].[14-349188],[RZPR].[14-349196],'
          '[RZPR].[14-848346],[RZPR].[14-874840],[RZPR].[14-851908],'
          '[RZPR].[14-849729]',

    # физическая культура и спорт
    '12': '[RZPR].[14-1203401],[RZPR].[14-850455],[RZPR].[14-866083],'
          '[RZPR].[14-850952],[RZPR].[14-413257],[RZPR].[14-413258]'
}

PLACES = {
    'адыгея': ('67646', 'республики Адыгеи'),
    'алания': ('67652', 'республики Алании'),
    'алтай': ('67684', 'республики Алтай'),
    'алтайский': ('67688', 'Алтайского края'),
    'амурская': ('67708', 'Амурской области'),
    'архангельская': ('67678', 'Архангельской области'),
    'астраханская': ('67645', 'Астраханской области'),
    'байконур': ('93015', 'Байконура'),
    'башкортостан': ('67655', 'республики Башкортостан'),
    'белгородская': ('67721', 'Белгородской области'),
    'брянская': ('67719', 'Брянской области'),
    'бурятия': ('67691', 'республики Бурятия'),
    'владимирская': ('67716', 'Владимирской области'),
    'волгоградская': ('67647', 'Волгоградской области'),
    'вологодская': ('67674', 'Вологодской области'),
    'воронежская': ('67723', 'Воронежской области'),
    'дагестан': ('67643', 'республики Дагестан'),
    'дальневосточный': ('17698', 'Дальневосточного федерального округа'),
    'еврейская': ('67705', 'Еврейской автономной области'),
    'забайкальский': ('67729', 'Забайкальского края'),
    'ивановская': ('67722', 'Ивановской области'),
    'ингушетия': ('67649', 'республики Ингушетия'),
    'иркутская': ('67682', 'Иркутской области'),
    'кабардино-балкарская': ('67651', 'Кабардино-Балкарской республики'),
    'калининградская': ('67670', 'Калининградской области'),
    'калмыкия': ('67648', 'Калмыкии'),
    'калужская': ('67712', 'Калужской области'),
    'камчатский': ('67728', 'Камчатского края'),
    'карачаево-черкесская': ('67638', 'Карачаево-Черкесской республики'),
    'карелия': ('67677', 'республики Карелия'),
    'кемеровская': ('67689', 'Кемеровской области'),
    'кировская': ('67663', 'Кировской области'),
    'коми': ('67673', 'республики Коми'),
    'костромская': ('67714', 'Костромской области'),
    'краснодарский': ('67644', 'Краснодарского края'),
    'красноярский': ('67694', 'Красноярского края'),
    'крым': ('93010', 'республики Крым'),
    'крымский': ('91128', 'Крымского федерального округа'),
    'курганская': ('67699', 'Курганской области'),
    'курская': ('67710', 'Курской области'),
    'ленинградская': ('67676', 'Ленинградской области'),
    'липецкая': ('67711', 'Липецкой области'),
    'магаданская': ('67703', 'Магаданской области'),
    'марий': ('67666', 'республики Марий Эл'),  # Meant 'Марий Эл'
    'мордовия': ('67662', 'республики Мордовия'),
    'москва': ('67724', 'Москвы'),
    'московская': ('67709', 'Московской области'),
    'мурманская': ('67669', 'Мурманской области'),
    'ненецкий': ('67672', 'Ненецкого автономного округа'),
    'нижегородская': ('67656', 'Нижегородской области'),
    'новгородская': ('67675', 'Новгородской области'),
    'новосибирская': ('67690', 'Новосибирской области'),
    'омская': ('67687', 'Омской области'),
    'оренбургская': ('67659', 'Оренбургской области'),
    'орловская': ('67726', 'Орловской области'),
    'осетия': ('67652', 'республики Северная Осетия'),
    'пензенская': ('67667', 'Пензенской области'),
    'пермский': ('67727', 'Пермского края'),
    'приволжский': ('3417', 'Приволожского федерального округа'),
    'приморский': ('67706', 'Приморского края'),
    'псковская': ('67671', 'Псковской области'),
    'россия': ('2', 'России'),
    'ростовская': ('67653', 'Ростовской области'),
    'рф': ('2', 'России'),
    'рязанская': ('67720', 'Рязанской области'),
    'самарская': ('67658', 'Самарской области'),
    'санкт-петербург': ('67639', 'Санкт-Петербурга'),
    'саратовская': ('67665', 'Саратовской области'),
    'саха': ('67642', 'республики Саха'),
    'сахалинская': ('67704', 'Сахалинской области'),
    'свердловская': ('67698', 'Свердловской области'),
    'севастополь': ('93011', 'Севастополя'),
    'северо-западный': ('10249', 'Северо-Западного федерального округа'),
    'северо-кавказский': ('24604', 'Северо-Кавказского федерального округа'),
    'сибирский': ('12097', 'Сибирского федерального округа'),
    'смоленская': ('67718', 'Смоленской области'),
    'ставропольский': ('67654', 'Ставропольского края'),
    'ставрополье': ('67654', 'Ставрополья'),  # Another version of 'ставропольский
    'тамбовская': ('67725', 'Тамбовской области'),
    'татарстан': ('67661', 'республики Татарстан'),
    'тверская': ('67717', 'Тверской области'),
    'томская': ('67692', 'Томской области'),
    'тульская': ('67715', 'Тульской области'),
    'тыва': ('67683', 'руспублики Тыва'),
    'тува': ('67683', 'Тувы'),  # Another version of 'тыва
    'тюменская': ('67697', 'Тюменской области'),
    'удмуртская': ('67668', 'республики Удмуртия'),
    'ульяновская': ('67660', 'Ульяновской области'),
    'уральский': ('16333', 'Уральского федерального округа'),
    'хабаровский': ('67707', 'Хабаровского края'),
    'хакасия': ('67681', 'республики Хакасия'),
    'ханты-мансийский': ('67695', 'Ханты-Мансийского автономного округа'),
    'центральный': ('19099', 'Центрального федерального округа'),
    'челябинская': ('67700', 'Челябинской области'),
    'чеченская': ('67650', 'Чеченской республики'),
    'чечня': ('67650', 'Чечни'),  # Another version of 'чеченская
    'чувашия': ('67664', 'Чувашии'),
    'чувашская': ('67664', 'Чувашской республики'),
    'чукотский': ('67640', 'Чукотского автономного округа'),
    'югра': ('67695', 'Югры'),
    'южный': ('3', 'Южного федерального округа'),
    'якутия': ('67642', 'Якутии'),
    'ямало-ненецкий': ('67696', 'Ямало-Ненецкого автономного округа'),
    'ярославская': ('67713', 'Ярославской области')
}

PLACES_FOR_CLDO02 = {
    'адыгея': '1451',
    'алания': '2507',
    'алтай': '12792',
    'алтайский': '13781',
    'амурская': '18776',
    'архангельская': '11867',
    'астраханская': '1176',
    'байконур': '93015',
    'башкортостан': '3418',
    'белгородская': '22729',
    'брянская': '22143',
    'бурятия': '15295',
    'владимирская': '21258',
    'волгоградская': '1512',
    'вологодская': '10809',
    'воронежская': '23249',
    'дагестан': '4',
    'дальневосточный': '17698',
    'еврейская': '18317',
    'забайкальский': '24584',
    'ивановская': '23067',
    'ингушетия': '2135',
    'иркутская': '12232',
    'кабардино-балкарская': '2374',
    'калининградская': '10293',
    'калмыкия': '2006',
    'калужская': '20350',
    'камчатский': '24543',
    'карачаево-черкесская': '1354',
    'карелия': '11627',
    'кемеровская': '14580',
    'кировская': '7726',
    'коми': '10597',
    'костромская': '20774',
    'краснодарский': '749',
    'красноярский': '15777',
    'крым': '91129',
    'крымский': ' 91128',
    'курганская': '16921',
    'курская': '19479',
    'ленинградская': '11404',
    'липецкая': '20018',
    'магаданская': '18239',
    'марий': '9301',  # Meant 'Марий Эл'
    'мордовия': '7265',
    'москва': '23783',
    'московская': '19100',
    'мурманская': '10250',
    'ненецкий': '10575',
    'нижегородская': '4439',
    'новгородская': '11182',
    'новосибирская': '14804',
    'омская': '13356',
    'оренбургская': '5483',
    'орловская': '24262',
    'осетия': '2507',
    'пензенская': '9475',
    'пермский': '24541',
    'приволжский': '3417',
    'приморский': '18354',
    'псковская': '10330',
    'россия': '2',
    'рф': '2',
    'ростовская': '2622',
    'рязанская': '22433',
    'самарская': '5140',
    'санкт-петербург': '11755',
    'саратовская': '8860',
    'саха': '17699',
    'сахалинская': '18294',
    'свердловская': '16827',
    'севастополь': '91139',
    'северо-западный': '10249',
    'северо-кавказский': '24604',
    'сибирский': '12097',
    'смоленская': '21792',
    'ставропольский': '3086',
    'ставрополье': '3086',
    'тамбовская': '23909',
    'татарстан': '6265',
    'тверская': '21386',
    'томская': '15593',
    'тульская': '21078',
    'тыва': '12649',
    'тува': '12649',
    'тюменская': '16507',
    'удмуртская': '9907',
    'ульяновская': '6097',
    'уральский': '16333',
    'хабаровский': '18540',
    'хакасия': '12130',
    'ханты-мансийский': '16334',
    'центральный': '19099',
    'челябинская': '17380',
    'чеченская': '2136',
    'чечня': '2136',
    'чувашская': '8208',
    'чувашия': '8208',
    'чукотский': '18184',
    'югра': '16334',
    'южный': '3',
    'якутия': '17699',
    'ямало-ненецкий': '16448',
    'ярославская': '20670'
}
