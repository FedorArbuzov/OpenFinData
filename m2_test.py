from m2_main import M2Retrieving


# Testing functional
class Test:
    @staticmethod
    def testing(input_data):
        i = 1
        for req in input_data:
            print(i)
            response = M2Retrieving.get_data(req)
            print(response.status)
            print(response.message)
            print(response.response)
            # if response.status is False:
            #     print(response.response)
            i += 1

    test_expenditure = (
        # Expenditure
        'расходы,фактический,null,2011,null,null',
        'расходы,плановый,null,2012,образование,null',
        'расходы,фактический,null,2013,национальная оборона,null',
        'расходы,запланированный,null,null,физическая культура и спорт,null',
        'расходы,текущий,null,null,общегосударственные вопросы,null',
        'расходы,фактический,null,2010,null,крым',
        'расходы,плановый,null,2009,национальная экономика,москва',
        'расходы,фактический,null,2010,null,москва',
        'расходы,запланированный,null,null,здравоохранение,санкт-петербург',
        'расходы,текущий,null,null,охрана окружающей среды,москва')

    test_profit = (
        # Profit
        'доходы,null,null,2012,null,null',
        'доходы,плановый,null,2010,null,null',
        'доходы,плановый,налоговый,2009,null,null',
        'доходы,плановый,null,null,null,null',
        'доходы,плановый,налоговый,null,null,null',
        'доходы,текущий,null,null,null,null',
        'доходы,текущий,налоговый,null,null,null',
        'доходы,null,null,2012,null,ярославская',
        'доходы,плановый,null,2012,null,карелия',
        'доходы,плановый,null,null,null,коми',
        'доходы,плановый,налоговый,null,null,томская',
        'доходы,текущий,null,null,null,хакасия',
        'доходы,текущий,налоговый,null,null,югра'
    )

    test_surplus = (
        # Surplus
        'дефицит,плановый,null,null,null,null',
        'дефицит,текущий,null,null,null,null',
        'дефицит,null,null,2014,null,null',
        'дефицит,null,null,2007,null,московская',
        'дефицит,плановый,null,2007,null,санкт-петербург',
        'дефицит,текущий,null,null,null,москва',
    )

    test_errors = (
        'доходы,null,null,null,null,null',
        'расходы,фактический,null,null,null,null',
        'расходы,фактический,налоговый,null,null,null',
        'доходы,null,неналоговый,2008,null,москва',
        'доходы,null,неналоговый,null,null,москва',
        'расходы,null,null,2014,null,ярославская'
    )


# Test.testing(Test.test_expenditure)
# Test.testing(Test.test_profit)
# Test.testing(Test.test_surplus)
# Test.testing(Test.test_errors)
