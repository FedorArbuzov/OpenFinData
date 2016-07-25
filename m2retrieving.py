# Module, which is responsible for getting required from user data
class M2Retrieving:
    @staticmethod
    def get_data(input_string):
        """Getting JSON data based on input parameters"""

        # 1. Преобразовать входную строку в лист                                -> get_data
        params = input_string.split(',')

        # 2. Создать мэп списка                                                 -> _list_to_map
        mapper = M2Retrieving._list_to_map(params)

        # 3. Проверить какому из существующих мэпов соответствует данный мэп
        # 4. Получить MDX запрос для мэпа                                       -> _get_mdx_skeleton_for_map

        mdx_skeleton = M2Retrieving._get_mdx_skeleton_for_mapper(mapper)
        if len(mdx_skeleton) == 0:
            return False
        else:
            # 5. Подставить в MDX запрос вместо "*1, *2, *3 и тд" параметры
            # 6. Отправить MDX запрос                                           -> _refactor_mdx_skeleton
            mdx_query = M2Retrieving._refactor_mdx_skeleton(mdx_skeleton, params)
            result = M2Retrieving._send_mdx_request(mdx_query)
            if len(result == 0):
                return False
            return result

    @staticmethod
    def _list_to_map(parameters):
        return

    @staticmethod
    def _get_mdx_skeleton_for_mapper(mapper):
        return

    @staticmethod
    def _refactor_mdx_skeleton(mdx_skeleton, params):
        return

    @staticmethod
    def _send_mdx_request(mdx_query):
        return
