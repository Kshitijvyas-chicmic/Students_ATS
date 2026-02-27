class StoreQuizDB:
    __quiz_store = {} # this is private variable where key is session_id and value is questions list

    @classmethod
    def save_quiz(cls, session_id: str, questions: list):
        cls.__quiz_store[session_id] = questions

    @classmethod
    def get_quiz(cls, session_id: str):
        return cls.__quiz_store.get(session_id)

    @classmethod
    def delete_quiz(cls, session_id: str):
        if session_id in cls.__quiz_store:
            del cls.__quiz_store[session_id]