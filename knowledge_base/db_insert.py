from knowledge_base.db_creation import *

# region Data for fulling KB
TYPES = ('плановый', 'фактический', 'текущий')

NALOG_NENALOG = {

    'налоговый': ('[KDGROUPS].[05-12], [KDGROUPS].[05-19], [KDGROUPS].[05-23], [KDGROUPS].[05-20], '
                  '[KDGROUPS].[05-21], [KDGROUPS].[05-22], [KDGROUPS].[05-33], [KDGROUPS].[05-34], '
                  '[KDGROUPS].[05-35], [KDGROUPS].[05-36]', '25-6'),
    'неналоговый': ('[KDGROUPS].[05-13], [KDGROUPS].[05-25], [KDGROUPS].[05-26], [KDGROUPS].[05-27], '
                    '[KDGROUPS].[05-28], [KDGROUPS].[05-29], [KDGROUPS].[05-30], [KDGROUPS].[05-31], '
                    '[KDGROUPS].[05-32], [KDGROUPS].[05-37]', '25-7')
}

SPHERES = {
    'null': (
        '', '[RZPR], [RZPR].[14-848223],[RZPR].[14-413284],[RZPR].[14-850484],[RZPR].[14-848398],'
            '[RZPR].[14-848260],[RZPR].[14-1203414],[RZPR].[14-848266],[RZPR].[14-848294],'
            '[RZPR].[14-848302],[RZPR].[14-848345],[RZPR].[14-1203401],[RZPR].[14-413259],'
            '[RZPR].[14-413264],[RZPR].[14-413267],[RZPR].[14-1203208],[RZPR].[14-1203195]'),

    'общегосударственные': (
        'на общегосударственные вопросы',
        '[RZPR].[14-848223],[RZPR].[14-413272],[RZPR].[14-342647],'
        '[RZPR].[14-413273],[RZPR].[14-413274],[RZPR].[14-413275],'
        '[RZPR].[14-413276],[RZPR].[14-413277],[RZPR].[14-413278],'
        '[RZPR].[14-413279],[RZPR].[14-848224],[RZPR].[14-413281],'
        '[RZPR].[14-413282],[RZPR].[14-848249]'),

    'оборона': (
        'на национальную оборону',
        '[RZPR].[14-413284],[RZPR].[14-413285],[RZPR].[14-413286],[RZPR].[14-413287],'
        '[RZPR].[14-413288],[RZPR].[14-413289],[RZPR].[14-413290],[RZPR].[14-413291]'),

    'безопасность': (
        'на национальную безопасность и правоохранительную деятельность',
        '[RZPR].[14-850484],[RZPR].[14-413293],[RZPR].[14-413294],[RZPR].[14-853732],'
        '[RZPR].[14-413296],[RZPR].[14-855436],[RZPR].[14-854333],[RZPR].[14-854342],'
        '[RZPR].[14-854482],[RZPR].[14-108129],[RZPR].[14-852920],[RZPR].[14-850760],'
        '[RZPR].[14-1203368],[RZPR].[14-853005],[RZPR].[14-850485]'),

    'экономика': (
        'на национальную экономику',
        '[RZPR].[14-848398],[RZPR].[14-848399],[RZPR].[14-1203160],'
        '[RZPR].[14-850771],[RZPR].[14-857652],[RZPR].[14-850172],'
        '[RZPR].[14-849065],[RZPR].[14-849070],[RZPR].[14-851151],'
        '[RZPR].[14-1203167],[RZPR].[14-1203168],[RZPR].[14-1203169],'
        '[RZPR].[14-848501]'),

    'жкх': (
        'на жилищно-коммунальное хозяйство',
        '[RZPR].[14-848260],[RZPR].[14-848261],[RZPR].[14-850428],'
        '[RZPR].[14-1203187],[RZPR].[14-881303],[RZPR].[14-849768]'),

    'окружающей': (
        'на охрану окружающей среды',
        '[RZPR].[14-1203414],[RZPR].[14-1203191],[RZPR].[14-872910],'
        '[RZPR].[14-872714],[RZPR].[14-848836]'),

    'образование': (
        'на образование',
        '[RZPR].[14-848266],[RZPR].[14-848267],[RZPR].[14-849320],'
        '[RZPR].[14-343261],[RZPR].[14-848274],[RZPR].[14-849333],'
        '[RZPR].[14-873227],[RZPR].[14-850050],[RZPR].[14-849520],'
        '[RZPR].[14-849303]'),

    'культура': (
        'на культуру и кинематографию',
        '[RZPR].[14-848294],[RZPR].[14-848295],[RZPR].[14-873473],'
        '[RZPR].[14-873499],[RZPR].[14-873512]'),

    'здравоохранение': (
        'на здравоохранение',
        '[RZPR].[14-848302],[RZPR].[14-872659],[RZPR].[14-848317],'
        '[RZPR].[14-343881],[RZPR].[14-108717],[RZPR].[14-349151],'
        '[RZPR].[14-349155],[RZPR].[14-349159],[RZPR].[14-849621],'
        '[RZPR].[14-349163]'),

    # социальная политика
    'социальная': (
        'на социальную политику',
        '[RZPR].[14-848345],[RZPR].[14-349188],[RZPR].[14-349196],'
        '[RZPR].[14-848346],[RZPR].[14-874840],[RZPR].[14-851908],'
        '[RZPR].[14-849729]'),

    # физическая культура и спорт
    'спорт': (
        'на спорт',
        '[RZPR].[14-1203401],[RZPR].[14-850455],[RZPR].[14-866083],'
        '[RZPR].[14-850952],[RZPR].[14-413257],[RZPR].[14-413258]')
}
PLACES = {
    'адыгея': ('67646', '1451', 'республики Адыгеи'),
    'алания': ('67652', '2507', 'республики Алании'),
    'алтай': ('67684', '12792', 'республики Алтай'),
    'алтайский': ('67688', '13781', 'Алтайского края'),
    'амурская': ('67708', '18776', 'Амурской области'),
    'архангельская': ('67678', '11867', 'Архангельской области'),
    'астраханская': ('67645', '1176', 'Астраханской области'),
    'байконур': ('93015', '93015', 'Байконура'),
    'башкортостан': ('67655', '3418', 'республики Башкортостан'),
    'белгородская': ('67721', '22729', 'Белгородской области'),
    'брянская': ('67719', '22143', 'Брянской области'),
    'бурятия': ('67691', '15295', 'республики Бурятия'),
    'владимирская': ('67716', '21258', 'Владимирской области'),
    'волгоградская': ('67647', '1512', 'Волгоградской области'),
    'вологодская': ('67674', '10809', 'Вологодской области'),
    'воронежская': ('67723', '23249', 'Воронежской области'),
    'дагестан': ('67643', '4', 'республики Дагестан'),
    'дальневосточный': ('17698', '17698', 'Дальневосточного федерального округа'),
    'еврейская': ('67705', '18317', 'Еврейской автономной области'),
    'забайкальский': ('67729', '24584', 'Забайкальского края'),
    'ивановская': ('67722', '23067', 'Ивановской области'),
    'ингушетия': ('67649', '2135', 'республики Ингушетия'),
    'иркутская': ('67682', '12232', 'Иркутской области'),
    'кабардино-балкарская': ('67651', '2374', 'Кабардино-Балкарской республики'),
    'калининградская': ('67670', '10293', 'Калининградской области'),
    'калмыкия': ('67648', '2006', 'Калмыкии'),
    'калужская': ('67712', '20350', 'Калужской области'),
    'камчатский': ('67728', '24543', 'Камчатского края'),
    'карачаево-черкесская': ('67638', '1354', 'Карачаево-Черкесской республики'),
    'карелия': ('67677', '11627', 'республики Карелия'),
    'кемеровская': ('67689', '14580', 'Кемеровской области'),
    'кировская': ('67663', '7726', 'Кировской области'),
    'коми': ('67673', '10597', 'республики Коми'),
    'костромская': ('67714', '20774', 'Костромской области'),
    'краснодарский': ('67644', '749', 'Краснодарского края'),
    'красноярский': ('67694', '15777', 'Красноярского края'),
    'крым': ('93010', '91129', 'республики Крым'),
    'крымский': ('91128', '91128', 'Крымского федерального округа'),
    'курганская': ('67699', '16921', 'Курганской области'),
    'курская': ('67710', '19479', 'Курской области'),
    'ленинградская': ('67676', '11404', 'Ленинградской области'),
    'липецкая': ('67711', '20018', 'Липецкой области'),
    'магаданская': ('67703', '18239', 'Магаданской области'),
    'марий': ('67666', '9301', 'республики Марий Эл'),
    'мордовия': ('67662', '7265', 'республики Мордовия'),
    'москва': ('67724', '23783', 'Москвы'),
    'московская': ('67709', '19100', 'Московской области'),
    'мурманская': ('67669', '10250', 'Мурманской области'),
    'ненецкий': ('67672', '10575', 'Ненецкого автономного округа'),
    'нижегородская': ('67656', '4439', 'Нижегородской области'),
    'новгородская': ('67675', '11182', 'Новгородской области'),
    'новосибирская': ('67690', '14804', 'Новосибирской области'),
    'омская': ('67687', '13356', 'Омской области'),
    'оренбургская': ('67659', '5483', 'Оренбургской области'),
    'орловская': ('67726', '24262', 'Орловской области'),
    'осетия': ('67652', '2507', 'республики Северная Осетия'),
    'пензенская': ('67667', '9475', 'Пензенской области'),
    'пермский': ('67727', '24541', 'Пермского края'),
    'приволжский': ('3417', '3417', 'Приволожского федерального округа'),
    'приморский': ('67706', '18354', 'Приморского края'),
    'псковская': ('67671', '10330', 'Псковской области'),
    'россия': ('2', '2', 'России'),
    'ростовская': ('67653', '2', 'Ростовской области'),
    'рф': ('2', '2622', 'России'),
    'рязанская': ('67720', '22433', 'Рязанской области'),
    'самарская': ('67658', '5140', 'Самарской области'),
    'санкт-петербург': ('67639', '11755', 'Санкт-Петербурга'),
    'саратовская': ('67665', '8860', 'Саратовской области'),
    'саха': ('67642', '17699', 'республики Саха'),
    'сахалинская': ('67704', '18294', 'Сахалинской области'),
    'свердловская': ('67698', '16827', 'Свердловской области'),
    'севастополь': ('93011', '91139', 'Севастополя'),
    'северо-западный': ('10249', '10249', 'Северо-Западного федерального округа'),
    'северо-кавказский': ('24604', '24604', 'Северо-Кавказского федерального округа'),
    'сибирский': ('12097', '12097', 'Сибирского федерального округа'),
    'смоленская': ('67718', '21792', 'Смоленской области'),
    'ставропольский': ('67654', '3086', 'Ставропольского края'),
    'ставрополье': ('67654', '3086', 'Ставрополья'),  # Another version of 'ставропольский
    'тамбовская': ('67725', '23909', 'Тамбовской области'),
    'татарстан': ('67661', '6265', 'республики Татарстан'),
    'тверская': ('67717', '21386', 'Тверской области'),
    'томская': ('67692', '15593', 'Томской области'),
    'тульская': ('67715', '21078', 'Тульской области'),
    'тыва': ('67683', '12649', 'руспублики Тыва'),
    'тува': ('67683', '12649', 'Тувы'),  # Another version of 'тыва
    'тюменская': ('67697', '16507', 'Тюменской области'),
    'удмуртская': ('67668', '9907', 'республики Удмуртия'),
    'ульяновская': ('67660', '6097', 'Ульяновской области'),
    'уральский': ('16333', '16333', 'Уральского федерального округа'),
    'хабаровский': ('67707', '18540', 'Хабаровского края'),
    'хакасия': ('67681', '12130', 'республики Хакасия'),
    'ханты-мансийский': ('67695', '16334', 'Ханты-Мансийского автономного округа'),
    'центральный': ('19099', '19099', 'Центрального федерального округа'),
    'челябинская': ('67700', '17380', 'Челябинской области'),
    'чеченская': ('67650', '2136', 'Чеченской республики'),
    'чечня': ('67650', '2136', 'Чечни'),  # Another version of 'чеченская
    'чувашия': ('67664', '8208', 'Чувашии'),
    'чувашская': ('67664', '8208', 'Чувашской республики'),
    'чукотский': ('67640', '18184', 'Чукотского автономного округа'),
    'югра': ('67695', '16334', 'Югры'),
    'южный': ('3', '3', 'Южного федерального округа'),
    'якутия': ('67642', '17699', 'Якутии'),
    'ямало-ненецкий': ('67696', '16448', 'Ямало-Ненецкого автономного округа'),
    'ярославская': ('67713', '20670', 'Ярославской области')
}

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
# endregion

create_tables()


# drop_tables()

# theme_type1 = ThemeType.create(type='расходы')
# theme_type2 = ThemeType.create(type='доходы')
# theme_type3 = ThemeType.create(type='профицит/дефицит')
#
# tag1 = Tag.create(tag='расходы', weight=1.0)
# tag2 = Tag.create(tag='доходы', weight=1.0)
# tag3 = Tag.create(tag='дефицит', weight=1.0)
# tag4 = Tag.create(tag='профицит', weight=1.0)
#
# t1 = Theme.create(type=theme_type1, tag=tag1)
# t2 = Theme.create(type=theme_type2, tag=tag2)
# t3 = Theme.create(type=theme_type3, tag=tag3)
# t4 = Theme.create(type=theme_type3, tag=tag4)
#
# param_type1 = ParameterType.create(type='территория')
# param_type2 = ParameterType.create(type='год')
# param_type3 = ParameterType.create(type='сфера')
# param_type42 = ParameterType.create(type='плановый')
# param_type43 = ParameterType.create(type='фактический')
# param_type44 = ParameterType.create(type='текущий')
# param_type5 = ParameterType.create(type='тип доходов')
# param_type6 = ParameterType.create(type='прошлый год')
#
# cube = ResourceType.create(type='куб')
#
# previous_year = Parameter.create(type=param_type6, tagValue='прошлый')
# year = Parameter.create(type=param_type2)
#
#
# def p_territories():
#     for key, value in PLACES.items():
#         Parameter.create(type=param_type1, tagValue=key, feedbackValue=value[2], value1=value[0], value2=value[1])
#
#
# def p_spheres():
#     for key, value in SPHERES.items():
#         Parameter.create(type=param_type3, tagValue=key, feedbackValue=value[0], value1=value[1])
#
#
# def p_nalog_nenalog():
#     Parameter.create(type=param_type5, tagValue='налоговый',
#                      feedbackValue='налоговые', value1=NALOG_NENALOG['налоговый'][0],
#                      value2=NALOG_NENALOG['налоговый'][1])
#
#     Parameter.create(type=param_type5, tagValue='неналоговый',
#                      feedbackValue='неналоговые', value1=NALOG_NENALOG['неналоговый'][0],
#                      value2=NALOG_NENALOG['неналоговый'][1])
#
#
# def p_planned_current_fact():
#     Parameter.create(type=param_type42, tagValue=TYPES[0], feedbackValue=TYPES[0][:-2] + '%s')
#     Parameter.create(type=param_type43, tagValue=TYPES[1], feedbackValue=TYPES[1][:-2] + '%s')
#     Parameter.create(type=param_type44, tagValue=TYPES[2], feedbackValue=TYPES[2][:-2] + '%s')
#
#
# def parameter_map():
#     param_set = 1
#     sql_queries = []
#
#     for mapper, sql_q in MAPPERS.items():
#         mapper = list(map(int, mapper.split('.')))
#
#         t = None
#         if mapper[0] == 2:
#             t = t1
#         elif mapper[0] == 3:
#             t = t2
#         else:
#             t = t3
#
#         if mapper[1] > 0:
#             if mapper[1] == 2:
#                 ParameterMap.create(paramSet=param_set, theme_type=t, parameter_type=param_type42)
#             elif mapper[1] == 3:
#                 ParameterMap.create(paramSet=param_set, theme_type=t, parameter_type=param_type43)
#             else:
#                 ParameterMap.create(paramSet=param_set, theme_type=t, parameter_type=param_type44)
#
#         if mapper[2] > 0:
#             ParameterMap.create(paramSet=param_set, theme_type=t, parameter_type=param_type5)
#
#         if mapper[3] > 0:
#             ParameterMap.create(paramSet=param_set, theme_type=t, parameter_type=param_type2)
#
#         if mapper[4] > 0:
#             ParameterMap.create(paramSet=param_set, theme_type=t, parameter_type=param_type3)
#
#         if mapper[5] > 0:
#             ParameterMap.create(paramSet=param_set, theme_type=t, parameter_type=param_type1)
#
#         sql_queries.append(sql_q)
#         param_set += 1
#
#     return sql_queries
#
#
# def query():
#     sql_queries = parameter_map()
#
#     for _paramSet in range(1, 33):
#         param_map = ParameterMap.select().where(ParameterMap.paramSet == _paramSet) \
#             .order_by(ParameterMap.id).limit(1)
#         Query.create(parameterMap=param_map, resource1=cube, templateQuery1=sql_queries[_paramSet - 1])
#
#
# def full_db():
#     p_territories()
#     p_spheres()
#     p_nalog_nenalog()
#     p_planned_current_fact()
#     query()
#
#
# full_db()

