class MinerModule:
    def __init__(self, uid: int, ss58: str, address: str):
        self.uid = uid
        self.ss58 = ss58
        self.address = address

    def __repr__(self):
        return f"MinerModule(UID={self.uid}, SS58={self.ss58}, Address={self.address})"

class ScoredMinerModule(MinerModule):
    def __init__(self, uid: int, ss58: str, address: str, score: int):
        super().__init__(uid=uid, ss58=ss58, address=address)
        self.score = score

    def __repr__(self):
        return f"ScoredMinerModule(UID={self.uid}, SS58={self.ss58}, Address={self.address}, Score={self.score})"
