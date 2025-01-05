class Entity:
    def __init__(self, pos: tuple, color: int):
        self.pos: tuple = pos
        self.color: int = color

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Entity: {self.pos}, color: {self.color}"

