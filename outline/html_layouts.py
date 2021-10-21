from xml.etree import ElementTree as ET
from pathlib import Path

from .data_types import ModuleData


class ModuleLayout:
    def __init__(self, filepath: Path, module: ModuleData) -> None:
        self.module = ModuleData
        mod = ET.Element("div", attrib={"class": "module"})
        span = ET.Element("span", attrib={"class": "module_path"})
        span.text = str(filepath)
        mod.append(span)

        for cls in module.classes:
            cls_div = ET.Element("div", attrib={"class": "classs"})
            cls_span = ET.Element("span", attrib={"class": "class_name"})
            cls_span.text = cls.name
            cls_div.append(cls_span)
            mod.append(cls_div)

        self.html = mod
