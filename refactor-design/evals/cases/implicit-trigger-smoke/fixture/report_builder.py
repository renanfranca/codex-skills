class ReportBuilder:
  def __init__(self):
    self._lines = []

  def build_report(self, facts):
    self._lines.clear()
    for fact in facts:
      self._lines.append(f"- {fact}")
    return "\n".join(self._lines)
