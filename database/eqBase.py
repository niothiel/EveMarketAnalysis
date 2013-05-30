class EqBase(object):
    def __eq__(self, other):
        return type(self) == type(other) and self.ID == other.ID

    def __ne__(self, other):
        return type(self) != type(other) or self.ID != other.ID

    def __hash__(self):
        return id(type(self)) + self.ID