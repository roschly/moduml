# moduml


## Purpose
A Python module for representing python code (modules and packages) as UML-inspired class diagrams.
Similarly to the intended role of UML diagrams in static languages, moduml is intented to help with getting an overview and comprehending a python code base at a higher level. Without looking at the code itself via an editor.

## Quick example
...

## Caveats
- Static analysis + dynamic language = rough approximation. But most python code is written in a static fashion.
- Requires GraphViz for visualization. Without this installed it is only possible to get the textual representation (feed it to an online GraphViz site if needed).
- Needs testing!
- Hobby project that evolved from something else. With custom (read: sub-optimal) language analysis.

## 2 main features
1. Graphical outline with directory hierarchy and file/module "interface" (globally defined functions, vars and types).
2. Import dependencies between modules and packages.


## How-to-use
``moduml <dir> [options]``
