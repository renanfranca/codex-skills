class DraftRenderer:
  def __init__(self):
    self._draft = None

  def render(self, title, lines):
    self._draft = [title.upper()]
    self._append_lines(lines)
    return "\n".join(self._draft)

  def _append_lines(self, lines):
    self._draft.extend(f"- {line}" for line in lines)


class MetadataRunner:
  def __init__(self, provider):
    self._provider = provider

  def run(self):
    self._validate(self._provider.read())
    return self._execute(self._provider.read())

  def _validate(self, metadata):
    if "version" not in metadata:
      raise ValueError("version is required")

  def _execute(self, metadata):
    return f"release-{metadata['version']}"


class ExplicitPhaseProtocol:
  def __init__(self):
    self._open = False

  def open(self):
    if self._open:
      raise RuntimeError("already open")
    self._open = True

  def close(self):
    if not self._open:
      raise RuntimeError("not open")
    self._open = False


class TextBuilder:
  def __init__(self):
    self._parts = []

  def add(self, part):
    self._parts.append(part)
    return self

  def build(self):
    return "".join(self._parts)


class Catalog:
  def __init__(self, names):
    self._normalized_names = tuple(name.strip().lower() for name in names)

  def contains(self, name):
    return name.strip().lower() in self._normalized_names
