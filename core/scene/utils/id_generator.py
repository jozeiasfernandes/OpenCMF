import uuid


class IDGenerator:
    @staticmethod
    def generate() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def short() -> str:
        return uuid.uuid4().hex[:12]