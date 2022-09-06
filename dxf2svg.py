import matplotlib.pyplot as plt
import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.properties import Properties, LayoutProperties
from ezdxf.addons.drawing.config import Configuration
import re
import os

# DXF
def parse_autocad(path, save_path):
    # https://stackoverflow.com/questions/58906149/python-converting-dxf-files-to-pdf-or-png-or-jpeg
    print("parsing autocad")

    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    # Recommended: audit & repair DXF document before rendering
    auditor = doc.audit()
    # The auditor.errors attribute stores severe errors,
    # which *may* raise exceptions when rendering.
    if len(auditor.errors) != 0:
        raise Exception("The DXF document is damaged and can't be converted!")
    else :
        fig = plt.figure()
        ctx = RenderContext(doc)
        # Better control over the LayoutProperties used by the drawing frontend
        layout_properties = LayoutProperties.from_layout(msp)
        layout_properties.set_colors(bg='#000000')
        ax = fig.add_axes([0, 0, 1, 1])
        out = MatplotlibBackend(ax)
        config = Configuration.defaults()
        config = config.with_changes(lineweight_scaling=0, min_lineweight=0.02, hatch_policy="SHOW_SOLID")
        Frontend(ctx, out, config=config).draw_layout(msp, layout_properties=layout_properties, finalize=True)
        fig.savefig(save_path, format="svg")
        svg_fill(save_path)

def svg_fill(path): # fill polylines in svg for visibility improvement
    lines = []
    with open(path, "r") as f:
        lines = f.readlines()
        for count in range(len(lines)):
            matches = re.search(r"; stroke:(.*?);", lines[count])
            if matches is not None:
                color = matches.groups()[0]
                lines[count] = re.sub(r'fill:(.*?);', fr'fill:{color};', lines[count]) # add fill color
                lines[count] = re.sub(r'fill:', fr'fill-opacity=50%;fill:', lines[count]) # add fill opacity

    with open(path, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    path = f"{os.environ['userprofile']}\\Dropbox\\lab\\c0_software\\G2i\\Gerber\\sy_coil_and_hamr_20220902\\sy_coil_and_hamr_20220902.dxf"
    save_path = f"{os.environ['userprofile']}\\Dropbox\\lab\\c0_software\\G2i\\Gerber\\sy_coil_and_hamr_20220902\\sy_coil_and_hamr_20220902.svg"
    parse_autocad(path, save_path)