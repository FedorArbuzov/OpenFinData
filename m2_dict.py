# Mappers for requests
mappers = {
    # Expenditures' mappers
    '2.3.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-4])',
    '2.2.0.1.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-3])',
    '2.3.0.1.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[MARKS].[03-4])',
    '2.5.0.0.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-1],[Marks].[03-3])',
    '2.4.0.0.1.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-1],[Marks].[03-4])',

    '2.3.0.1.0.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-4])',
    '2.2.0.1.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-3])',
    '2.3.0.1.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-4])',
    '2.5.0.0.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Marks].[03-3])',
    '2.4.0.0.1.1': 'SELECT {[Measures].[VALUE]} ON COLUMNS, {*4} dimension properties [RZPR].[Tab1],[Tab2],[Tab3] ON ROWS FROM [EXDO01.DB] WHERE ([BGLevels].[09-3],[Territories].[*5],[Marks].[03-4])',

    # Profits' mappers
    '3.0.0.1.0.0': 'SELECT {[Measures].[VALUE]}  ON COLUMNS FROM [INYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-2])',
    # no details
    '3.2.0.1.0.0': 'SELECT {[Measures].[VALUE]}  ON COLUMNS FROM [INYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-1])',
    # no details
    '3.0.1.1.0.0': 'SELECT {[Measures].[VALUE]}  ON COLUMNS, {*2} ON ROWS FROM [INYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-2])',
    '3.2.1.1.0.0': 'SELECT {[Measures].[VALUE]}  ON COLUMNS, {*2} ON ROWS FROM [INYR03.DB] WHERE ([BGLevels].[09-1],[Years].[*3],[Marks].[03-1])',
    '3.2.0.0.0.0': 'SELECT {[Measures].[PLANONYEAR]} ON COLUMNS, {[BIFB].[25-1],[BIFB].[25-4],[BIFB].[25-5],[BIFB].[25-6],[BIFB].[25-7]} ON ROWS FROM [CLDO01.DB]',
    '3.2.1.0.0.0': 'SELECT {[Measures].[PLANONYEAR]} ON COLUMNS FROM [CLDO01.DB] WHERE ([BIFB].[*2])',  # no details
    '3.4.0.0.0.0': 'SELECT {[Measures].[FACTBGYEAR]} ON COLUMNS, {[BIFB].[25-1],[BIFB].[25-4],[BIFB].[25-5],[BIFB].[25-6],[BIFB].[25-7]} ON ROWS FROM [CLDO01.DB]',
    '3.4.1.0.0.0': 'SELECT {[Measures].[FACTBGYEAR]} ON COLUMNS FROM [CLDO01.DB] WHERE ([BIFB].[*2])',  # no details
    '3.0.0.1.0.1': 'SELECT {[Measures].[VALUE]}  ON COLUMNS FROM [INYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Marks].[03-2],[Territories].[*5])',
    # no details
    '3.2.0.1.0.1': 'SELECT {[Measures].[VALUE]}  ON COLUMNS FROM [INYR03.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Marks].[03-1],[Territories].[*5])',
    # no details
    '3.2.0.0.0.1': 'SELECT {[Measures].[VALUE]}  ON COLUMNS FROM [INDO01.DB] WHERE ([BGLevels].[09-3],[Marks].[03-1],[Territories].[*5])',
    # no details
    '3.2.1.0.0.1': 'SELECT {[Measures].[VALUE]}  ON COLUMNS, {*2} ON ROWS FROM [INDO01.DB] WHERE ([BGLevels].[09-3],[Marks].[03-1],[Territories].[*5])',
    '3.4.0.0.0.1': 'SELECT {[Measures].[VALUE]}  ON COLUMNS FROM [INDO01.DB] WHERE ([BGLevels].[09-3],[Marks].[03-2],[Territories].[*5])',
    # no details
    '3.4.1.0.0.1': 'SELECT {[Measures].[VALUE]}  ON COLUMNS, {*2} ON ROWS FROM [INDO01.DB] WHERE ([BGLevels].[09-3],[Marks].[03-2],[Territories].[*5])',

    # Deficit/surplus's mappers
    '4.4.0.0.0.0': 'SELECT {[Measures].[PLANONYEAR]} ON COLUMNS FROM [CLDO01.DB] WHERE ([BIFB].[25-20])',
    '4.2.0.0.0.0': 'SELECT {[Measures].[FACTBGYEAR]} ON COLUMNS FROM [CLDO01.DB] WHERE ([BIFB].[25-20])',
    '4.0.0.1.0.0': 'SELECT {[Measures].[VALUE]} ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-1], [Marks].[03-6],[Years].[*3])',
    '4.0.0.1.0.1': 'SELECT {[Measures].[VALUE]}  ON COLUMNS FROM [FSYR01.DB] WHERE ([BGLevels].[09-3],[Years].[*3],[Territories].[*5],[Marks].[03-6])',
    '4.2.0.0.0.1': None,
    '4.4.0.0.0.1': None
}

# Outer codes for substitution in MDX-query
param2 = {

    'налоговый': ('[KDGROUPS].[05-12], [KDGROUPS].[05-19], [KDGROUPS].[05-23], [KDGROUPS].[05-20], '
                  '[KDGROUPS].[05-21], [KDGROUPS].[05-22], [KDGROUPS].[05-33], [KDGROUPS].[05-34], '
                  '[KDGROUPS].[05-35], [KDGROUPS].[05-36]', '25-6'),
    'неналоговый': ('[KDGROUPS].[05-13], [KDGROUPS].[05-25], [KDGROUPS].[05-26], [KDGROUPS].[05-27], '
                    '[KDGROUPS].[05-28], [KDGROUPS].[05-29], [KDGROUPS].[05-30], [KDGROUPS].[05-31], '
                    '[KDGROUPS].[05-32], [KDGROUPS].[05-37]', '25-7')
}

sphere = {
    'null': '[RZPR], [RZPR].[14-848223],[RZPR].[14-413284],[RZPR].[14-850484],[RZPR].[14-848398],'
            '[RZPR].[14-848260],[RZPR].[14-1203414],[RZPR].[14-848266],[RZPR].[14-848294],'
            '[RZPR].[14-848302],[RZPR].[14-848345],[RZPR].[14-1203401],[RZPR].[14-413259],'
            '[RZPR].[14-413264],[RZPR].[14-413267],[RZPR].[14-1203208],[RZPR].[14-1203195]',

    'общегосударственные вопросы': '[RZPR].[14-848223],[RZPR].[14-413272],[RZPR].[14-342647],'
                                   '[RZPR].[14-413273],[RZPR].[14-413274],[RZPR].[14-413275],'
                                   '[RZPR].[14-413276],[RZPR].[14-413277],[RZPR].[14-413278],'
                                   '[RZPR].[14-413279],[RZPR].[14-848224],[RZPR].[14-413281],'
                                   '[RZPR].[14-413282],[RZPR].[14-848249]',

    'национальная оборона': '[RZPR].[14-413284],[RZPR].[14-413285],[RZPR].[14-413286],[RZPR].[14-413287],'
                            '[RZPR].[14-413288],[RZPR].[14-413289],[RZPR].[14-413290],[RZPR].[14-413291]',

    'национальная безопасность и правоохранительная деятельность': '[RZPR].[14-850484],[RZPR].[14-413293],'
                                                                   '[RZPR].[14-413294],[RZPR].[14-853732],'
                                                                   '[RZPR].[14-413296],[RZPR].[14-855436],'
                                                                   '[RZPR].[14-854333],[RZPR].[14-854342],'
                                                                   '[RZPR].[14-854482],[RZPR].[14-108129],'
                                                                   '[RZPR].[14-852920],[RZPR].[14-850760],'
                                                                   '[RZPR].[14-1203368],[RZPR].[14-853005],'
                                                                   '[RZPR].[14-850485]',

    'национальная экономика': '[RZPR].[14-848398],[RZPR].[14-848399],[RZPR].[14-1203160],'
                              '[RZPR].[14-850771],[RZPR].[14-857652],[RZPR].[14-850172],'
                              '[RZPR].[14-849065],[RZPR].[14-849070],[RZPR].[14-851151],'
                              '[RZPR].[14-1203167],[RZPR].[14-1203168],[RZPR].[14-1203169],'
                              '[RZPR].[14-848501]',

    'жилищно-коммунальное хозяйство': '[RZPR].[14-848260],[RZPR].[14-848261],[RZPR].[14-850428],'
                                      '[RZPR].[14-1203187],[RZPR].[14-881303],[RZPR].[14-849768]',

    'охрана окружающей среды': '[RZPR].[14-1203414],[RZPR].[14-1203191],[RZPR].[14-872910],'
                               '[RZPR].[14-872714],[RZPR].[14-848836]',

    'образование': '[RZPR].[14-848266],[RZPR].[14-848267],[RZPR].[14-849320],'
                   '[RZPR].[14-343261],[RZPR].[14-848274],[RZPR].[14-849333],[RZPR].[14-873227],'
                   '[RZPR].[14-850050],[RZPR].[14-849520],[RZPR].[14-849303]',

    'культура, кинематография': '[RZPR].[14-848294],[RZPR].[14-848295],[RZPR].[14-873473],'
                                '[RZPR].[14-873499],[RZPR].[14-873512]',

    'здравоохранение': '[RZPR].[14-848302],[RZPR].[14-872659],[RZPR].[14-848317],[RZPR].[14-343881],'
                       '[RZPR].[14-108717],[RZPR].[14-349151],[RZPR].[14-349155],[RZPR].[14-349159],'
                       '[RZPR].[14-849621],[RZPR].[14-349163]',

    'социальная политика': '[RZPR].[14-848345],[RZPR].[14-349188],[RZPR].[14-349196],'
                           '[RZPR].[14-848346],[RZPR].[14-874840],[RZPR].[14-851908],'
                           '[RZPR].[14-849729]',

    'физическая культура и спорт': '[RZPR].[14-1203401],[RZPR].[14-850455],[RZPR].[14-866083],'
                                   '[RZPR].[14-850952],[RZPR].[14-413257],[RZPR].[14-413258],'
                                   '[RZPR].[14-413259],[RZPR].[14-413260],[RZPR].[14-851607],'
                                   '[RZPR].[14-413262],[RZPR].[14-413263],[RZPR].[14-413264],'
                                   '[RZPR].[14-413265],[RZPR].[14-413266],[RZPR].[14-413267],'
                                   '[RZPR].[14-413268],[RZPR].[14-413269],[RZPR].[14-413270]'
}

places = {
    'байконур': '93015',
    'приволжский': '3417',
    'северо-западный': '10249',
    'сибирский': '12097',
    'уральский': '16333',
    'центральный': '19099',
    'амурская': '67708',
    'еврейская': '67705',
    'камчатский': '67728',
    'магаданская': '67703',
    'приморский': '67706',
    'саха': '67642',
    'якутия': '67642',
    'сахалинская': '67704',
    'хабаровский': '67707',
    'чукотский': '67640',
    'дальневосточный': '17698',
    'севастополь': '93011',
    'крым': '93010',
    'крымский': '91128',
    'кировская': '67663',
    'нижегородская': '67656',
    'оренбургская': '67659',
    'пензенская': '67667',
    'пермский': '67727',
    'башкортостан': '67655',
    'марий эл': '67666',
    'мордовия': '67662',
    'татарстан': '67661',
    'самарская': '67658',
    'саратовская': '67665',
    'удмуртская': '67668',
    'ульяновская': '67660',
    'чувашская': '67664',
    'чувашия': '67664',
    'архангельская': '67678',
    'вологодская': '67674',
    'санкт-петербург': '67639',
    'калининградская': '67670',
    'ленинградская': '67676',
    'мурманская': '67669',
    'ненецкий': '67672',
    'новгородская': '67675',
    'псковская': '67671',
    'карелия': '67677',
    'коми': '67673',
    'кабардино-балкарская': '67651',
    'карачаево-черкесская': '67638',
    'дагестан': '67643',
    'ингушетия': '67649',
    'осетия': '67652',
    'алания': '67652',
    'ставропольский': '67654',
    'чеченская': '67650',
    'северо-кавказский': '24604',
    'алтайский': '67688',
    'забайкальский': '67729',
    'иркутская': '67682',
    'кемеровская': '67689',
    'красноярский': '67694',
    'новосибирская': '67690',
    'омская': '67687',
    'алтай': '67684',
    'бурятия': '67691',
    'тыва': '67683',
    'хакасия': '67681',
    'томская': '67692',
    'курганская': '67699',
    'свердловская': '67698',
    'тюменская': '67697',
    'ханты-мансийский': '67695',
    'югра': '67695',
    'челябинская': '67700',
    'ямало-ненецкий': '67696',
    'белгородская': '67721',
    'брянская': '67719',
    'владимирская': '67716',
    'воронежская': '67723',
    'москва': '67724',
    'ивановская': '67722',
    'калужская': '67712',
    'костромская': '67714',
    'курская': '67710',
    'липецкая': '67711',
    'московская': '67709',
    'орловская': '67726',
    'рязанская': '67720',
    'смоленская': '67718',
    'тамбовская': '67725',
    'тверская': '67717',
    'тульская': '67715',
    'ярославская': '67713',
    'астраханская': '67645',
    'волгоградская': '67647',
    'краснодарский': '67644',
    'адыгея': '67646',
    'калмыкия': '67648',
    'ростовская': '67653',
    'южный': '3',
    'российская федерация': '2',
    'россия': '2',
    'рф': '2'
}