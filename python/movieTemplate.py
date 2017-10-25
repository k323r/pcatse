from paraview.simple import *

import os

representationType = 'Surface With Edges'

animation = False

path = os.getcwd()

casefoam = OpenFOAMReader(FileName=os.path.join(path, 'case.foam'))

renderview = GetActiveViewOrCreate('RenderView')

slice1 = Slice(Input=casefoam)

slice1.SliceType.Origin = [0.0, 0.0, 0.0]
slice1.SliceType.Normal = [0.0, 0.0, 1.0]
slice1.Triangulatetheslice = 0

slice1Display = Show(slice1, renderview)
slice1Display.Representation = representationType


if animation:
    # set scalar coloring
    ColorBy(slice1Display, ('CELLS', 'U', 'Magnitude'))

    # get color transfer function/color map for 'U'
    uLUT = GetColorTransferFunction('U')

    # Rescale transfer function
    uLUT.RescaleTransferFunction(0.8, 1.2)

    # get opacity transfer function/opacity map for 'U'
    uPWF = GetOpacityTransferFunction('U')

    # Rescale transfer function
    uPWF.RescaleTransferFunction(0.8, 1.2)

    # get color legend/bar for uLUT in view renderView1
    uLUTColorBar = GetScalarBar(uLUT, renderview)

    SaveAnimation(os.path.join(path, 'U.ogv'),
        renderview,
        ImageResolution=[1500, 750],
        FrameWindow = [0, 59])

else:
    # save screenshot
    SaveScreenshot(os.path.join(path, 'screenshot.png'),
        renderview,
        ImageResolution=[1459, 743],
        FontScaling='Scale fonts proportionally',
        OverrideColorPalette='',
        StereoMode='No change',
        TransparentBackground=0,
        ImageQuality=100)


