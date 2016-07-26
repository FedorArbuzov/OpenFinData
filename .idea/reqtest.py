import urllib.request
import urllib.parse

url = 'http://conf.test.fm.epbs.ru/mdxexpert/CellsetByMdx'
mdxQuery = ("SELECT " +
            "{[Measures].[VALUE]}  ON COLUMNS, " +
            "NON EMPTY {[Territories].[08-17698], [Territories].[08-91128]} ON ROWS " +
            "FROM [BLYR01.DB] " +
            "WHERE ([BGLevels].[09-3])")
values = 1