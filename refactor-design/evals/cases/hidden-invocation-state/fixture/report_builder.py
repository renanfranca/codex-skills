class ReportBuilder:
  def __init__(self):
    self._lines = []

  def build_report(self, sections):
    self._lines.clear()
    for title, facts in sections:
      self._append_section(title, facts)
    return "\n".join(self._lines)

  def _append_section(self, title, facts):
    self._lines.append(title.upper())
    self._lines.extend(f"- {fact}" for fact in facts)
