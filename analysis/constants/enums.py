from common.constants.enums import ChoicesEnum


class AnalysisSessionStatus(str, ChoicesEnum):
    INITIALIZED = "initialized"
    ANALYZING = "analyzing"
    DONE = "done"
