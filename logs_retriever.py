import datetime


class LogsRetriever:
    def __init__(self, path_to_log_file):
        self.path_to_log_file = path_to_log_file

    def get_log(self, kind='all', user_id=None, time_delta=15):
        if kind == 'all':
            return self._get_all_logs()
        elif kind == 'session':
            return self._get_session_logs(user_id, time_delta)
        else:
            return self._get_request_logs(user_id)

    def _get_all_logs(self):
        with open(self.path_to_log_file, encoding='utf-8') as file:
            all_logs = file.read()
        return all_logs

    def _get_session_logs(self, user_id, time_delta):

        logs = []

        time_delta = datetime.timedelta(minutes=time_delta)
        log_start_analyze_datetime = (datetime.datetime.today() - time_delta)

        for line in reversed(list(open(self.path_to_log_file, encoding='utf-8'))):
            line = line.split('\t')

            try:
                log_user_id = LogsRetriever._get_user_id_from_log_part(line[2])
                log_data = LogsRetriever._get_dt_from_line(line[0])
                if log_user_id == str(user_id) and log_data >= log_start_analyze_datetime:
                    logs.append('\t'.join(line))
            except IndexError:
                continue

        return '\n'.join(list(reversed(logs)))

    def _get_request_logs(self, user_id):
        logs = []
        module_name = ''

        for line in reversed(list(open(self.path_to_log_file, encoding='utf-8'))):
            line = line.split('\t')

            try:
                if LogsRetriever._get_user_id_from_log_part(line[2]) == str(user_id):
                    log_module = LogsRetriever._get_module_from_log_part(line[1])
                    if module_name != log_module:
                        logs.append('\t'.join(line))
                        module_name = log_module

                    if len(logs) == 3:
                        break
            except IndexError:
                continue

        return '\n'.join(list(reversed(logs)))

    @staticmethod
    def _get_dt_from_line(data_log_part):
        return datetime.datetime.strptime(data_log_part, '%Y-%m-%d  %H:%M')

    @staticmethod
    def _get_user_id_from_log_part(user_log_part):
        return user_log_part.split(':')[1].strip()

    @staticmethod
    def _get_module_from_log_part(module_log_part):
        return module_log_part.split(':')[1].strip()
