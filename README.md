# moduml


## Purpose
A Python module for representing python code (modules and packages) as UML-inspired class diagrams.
Similarly to the intended role of UML diagrams in static languages, moduml is intented to help with getting an overview and comprehending a python code base at a higher level. Without looking at the code itself via an editor.


## Quick example
moduml applied to itself:
``moduml moduml --output-file moduml_example.png --show-interface --show-imports --dir-as cluster``
![moduml example](moduml_example.png)


## Caveats
- Static analysis + dynamic language = rough approximation. But most python code is written in a static fashion.
- Requires GraphViz for visualization. Without this installed it is only possible to get the textual representation (feed it to an online GraphViz site if needed).
- Needs testing!
- Hobby project that evolved from something else. Custom (read: sub-optimal) language analysis.


## Features
1. Graphical outline with directory hierarchy and file/module "interface" (globally defined functions, vars and types).
2. Import dependencies between modules and packages.


## How-to-use
``moduml <dir> [options]``


## Todos
- ~~use "concentrate" to merge multiple edges together. Maybe as option, maybe as permanent setting.~~
- ~~option for changing between the two possible 'rankdir' settings: 'TB' (top-bottom), 'LR' (left-right). OBS! explain that it screws with the interface layout.~~
- ~~add (maybe as option) 'constraint' to import links in 'dir-as node' view, causing the tree hiearchy between folders and files to be preserved.~~
- 'no directories'-view ('dir-as removed'), only files (with imports as only links) and fully qualified file names.
- add a couple of sensible default views, that ignores other specific args (or just overwrites the ones it uses), e.g. interface-view (dir-as node, only hiearchy imports, show-interface)
- streamlit app for exploring moduml's own source code (hosted as a streamlit share service).
- config file for style definitions, e.g. color schemes, node shapes, etc.
- replace paths2graph with network_creator script.
- ignore-files only works for files that are not imported themselves, i.e. test files (which was the intended use case).
