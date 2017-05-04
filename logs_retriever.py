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
                if line[1] not in ('DEBUG', 'ERROR'):
                    log_data = LogsRetriever._get_dt_from_line(line[0])
                    query_id = LogsRetriever._get_value_from_log_part(line[2])
                    if log_data >= log_start_analyze_datetime:
                        logs.append('\t'.join(line))
            except IndexError:
                pass

        queries_id = []
        for log in logs:
            log = log.split('\t')
            try:
                if str(user_id) == LogsRetriever._get_value_from_log_part(log[4]):
                    queries_id.append(LogsRetriever._get_value_from_log_part(log[2]))
            except IndexError:
                pass

        for log in list(logs):
            try:
                if LogsRetriever._get_value_from_log_part(log.split('\t')[2]) not in queries_id:
                    logs.remove(log)
            except IndexError:
                pass

        return '\n'.join(list(reversed(logs)))

    def _get_request_logs(self, user_id):
        logs = []
        query_id = None

        for line in reversed(list(open(self.path_to_log_file, encoding='utf-8'))):
            line = line.split('\t')

            try:
                if line[1] not in ('DEBUG', 'ERROR'):
                    logs.append('\t'.join(line))
                    if str(user_id) == LogsRetriever._get_value_from_log_part(line[4]):
                        query_id = LogsRetriever._get_value_from_log_part(line[2])
                        break
            except IndexError:
                pass

        for log in list(logs):
            try:
                if LogsRetriever._get_value_from_log_part(log.split('\t')[2]) != query_id:
                    logs.remove(log)
            except IndexError:
                pass

        return '\n'.join(list(reversed(logs)))

    # TODO: доделать метод получения логов
    @staticmethod
    def _get_info_logs(log):
        return log

    @staticmethod
    def _get_dt_from_line(data_log_part):
        return datetime.datetime.strptime(data_log_part, '%Y-%m-%d  %H:%M')

    @staticmethod
    def _get_value_from_log_part(user_log_part):
        return user_log_part.split(':')[1].strip()
