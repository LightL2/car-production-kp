# -*- coding: utf-8 -*-
import re
import zipfile
from pathlib import Path

PPTX = Path(__file__).parent / "Anor Bureau x 8BIT x BYD Presentation.pptx"

with zipfile.ZipFile(PPTX) as z:
    for i in range(1, 10):
        rel_xml = z.read(f"ppt/slides/_rels/slide{i}.xml.rels").decode("utf-8")
        slide_xml = z.read(f"ppt/slides/slide{i}.xml").decode("utf-8")
        rid_map = {}
        for rid, target in re.findall(r'Id="(rId\d+)"[^>]*Target="([^"]+)"', rel_xml):
            rid_map[rid] = target
        print(f"\nSLIDE {i}")
        for rid in re.findall(r'r:embed="(rId\d+)"', slide_xml):
            print("  IMG", rid, "->", rid_map.get(rid))
        for rid in re.findall(r'r:link="(rId\d+)"', slide_xml):
            print("  LINK", rid, "->", rid_map.get(rid))
