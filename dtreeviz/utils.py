import xml.etree.cElementTree as ET
from numbers import Number
from typing import Tuple
from pathlib import Path


def inline_svg_images(svg) -> str:
    """
    Inline IMAGE tag refs in graphviz/dot -> SVG generated files.

    Convert all .png image tag refs directly under g tags like:

    <g id="node1" class="node">
        <image xlink:href="/tmp/node4.png" width="45px" height="76px" preserveAspectRatio="xMinYMin meet" x="76" y="-80"/>
    </g>

    to include the .svg equivalent:

    <g id="node1" class="node">
        <svg width="45px" height="76px" viewBox="0 0 49.008672 80.826687" preserveAspectRatio="xMinYMin meet" x="76" y="-80">
            XYZ
        </svg>
    </g>

    where XYZ is taken from ref'd svg image file:

    <?xml version="1.0" encoding="utf-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
      "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <!-- Created with matplotlib (http://matplotlib.org/) -->
    <svg height="80.826687pt" version="1.1" viewBox="0 0 49.008672 80.826687" width="49.008672pt"
         xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
        XYZ
    </svg>

    Note that width/height must be taken from ref'd svg image file. The <image/> tag
    values seem a bit off.

    :param svg: SVG string with <image/> tags.
    :return: svg with <image/> tags replaced with content of referenced svg image files.
    """
    ns = {"svg": "http://www.w3.org/2000/svg"}
    root = ET.fromstring(svg)
    tree = ET.ElementTree(root)
    parent_map = {c: p for p in tree.iter() for c in p}

    # Find all image tags in document (must use svg namespace)
    image_tags = tree.findall(".//svg:g/svg:image", ns)
    for img in image_tags:
        # load ref'd image and get svg root
        filename = img.attrib["{http://www.w3.org/1999/xlink}href"]
        svgfilename = filename.replace('.png', '.svg')

        with open(svgfilename) as f:
            imgsvg = f.read()
        imgroot = ET.fromstring(imgsvg)
        for k,v in img.attrib.items(): # copy IMAGE tag attributes to svg from image file
            if k not in {"{http://www.w3.org/1999/xlink}href"}:
                imgroot.attrib[k] = v
        # replace IMAGE with SVG tag
        p = parent_map[img]
        # print("BEFORE " + ', '.join([str(c) for c in p]))
        p.append(imgroot)
        p.remove(img)
        # print("AFTER " + ', '.join([str(c) for c in p]))

    ET.register_namespace('', "http://www.w3.org/2000/svg")
    ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")
    xml_str = ET.tostring(root).decode()
    return xml_str


def get_SVG_shape(filename) -> Tuple[Number,Number]:
    """
    Sample line from SVG file from which we can get w,h:
    <svg height="122.511795pt" version="1.1" viewBox="0 0 451.265312 122.511795"
         width="451.265312pt" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="...">
    """
    with open(filename, "r") as f:
        for line in f.readlines():
            if line.startswith("<svg "):
                args = line[len("<svg "):].split()
                d = {}
                for arg in args:
                    a = arg.split('=')
                    if len(a) == 2:
                        d[a[0]] = a[1].strip('"').strip('pt')
                return float(d['width']), float(d['height'])


def create_blank_png(filename):
    """
    Create a .png file from a predefined blank .png file stored as string here in this
    function.
    """
    with open(filename, "wb") as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x01YiTXtXML:com.adobe.xmp\x00\x00\x00\x00\x00<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 5.4.0">\n   <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n      <rdf:Description rdf:about=""\n            xmlns:tiff="http://ns.adobe.com/tiff/1.0/">\n         <tiff:Orientation>1</tiff:Orientation>\n      </rdf:Description>\n   </rdf:RDF>\n</x:xmpmeta>\nL\xc2\'Y\x00\x00\x00\x0cIDAT\x08\x1dc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\x9f\xca-\x13\x00\x00\x00\x00IEND\xaeB`\x82')


if __name__ == '__main__':
    # test rig
    with open("/tmp/foo.svg") as f:
        svg = f.read()

    svg2 = inline_svg_images(svg)
    print(svg2)

    with open("/tmp/bar.svg", "w") as f:
        f.write(svg2)
