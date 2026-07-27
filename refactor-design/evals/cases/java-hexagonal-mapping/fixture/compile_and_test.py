from pathlib import Path
import subprocess
import tempfile


def main():
  sources = sorted(str(path) for path in Path("src").rglob("*.java"))
  with tempfile.TemporaryDirectory(prefix="java-mapping-classes-") as output:
    subprocess.run(["javac", "-d", output, *sources], check=True)
    subprocess.run(["java", "-cp", output, "StatusAdapterTest"], check=True)


if __name__ == "__main__":
  main()
