"""
Here are various helper functions
"""
def truncate(string, max_length, raw=False, reverse=False):
        """
        :param string[str] - string to truncate
        :param max_length[int] - max length of the string
        :param raw[bool] - Whether to do raw truncate or add trailing "..." to indicate truncation.
        """
        if len(string) > max_length:
            if raw:
                if not reverse:
                    return string[:max_length]
                if reverse:
                    return string[-max_length::]
            if reverse:
                return '...' + string[-(max_length - 3)::]
            return string[:max_length - 3] + '...'
        return string