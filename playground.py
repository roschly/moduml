
# %%

from pathlib import Path

# %%

# pattern = "moduml/**/*.py"
pattern = "**/network/*.py"

# path = Path.cwd()
path = Path("moduml")

excl = list(path.rglob(pattern))
excl

# %%
