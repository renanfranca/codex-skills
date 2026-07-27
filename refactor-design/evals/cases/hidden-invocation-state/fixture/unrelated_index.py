class UnrelatedIndex:
  def __init__(self):
    self._entries = []

  def build(self, values):
    self._entries.clear()
    self._entries.extend((value, position) for position, value in enumerate(values))
    return dict(self._entries)
