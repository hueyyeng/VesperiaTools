class InvalidFileException(Exception):
    def __init__(self, file_path):
        Exception.__init__(self, f"Invalid file or file path: {file_path}")


class InvalidFourCCException(Exception):
    def __init__(self, expected_value, found_value):
        Exception.__init__(self, f"Expected {expected_value}. Got {found_value} instead.")
