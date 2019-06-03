from pathlib import Path

from tqdm import tqdm
from pyevtk.hl import gridToVTK
import xarray as xr
import vtk


def _create_vtk_files(ds, path):
    for n, t in enumerate(tqdm(ds.time.values)):
        fp = path/"grid_{:05d}".format(n)

        x, y, z = ds.xt.values, ds.yt.values, ds.zt.values

        # Output a rectilinear grid file with dimensions and point data
        # included
        ds_ = ds.sel(time=t)
        point_data = dict([(v, ds_[v].values) for v in ds.data_vars])
        gridToVTK(str(fp), x, y, z, pointData=point_data)

def _render_frame_with_vtk(fname, isosurface='cvrxp_p_stddivs', isovalue=3.0):
    # Read the source file, as XML.
    reader = vtk.vtkXMLRectilinearGridReader()

    def update_reader(fname):
        reader.SetFileName(fname)
        reader.Modified()
        reader.Update()
    update_reader(fname)

    # Get the output
    output = reader.GetOutput()

    # Printing basic data
    print("The dimensions are: " , output.GetDimensions())
    print("The number of points are: " , output.GetNumberOfPoints())

    # Contour Filters
    plane = vtk.vtkContourFilter()
    plane.SetInputDataObject(output)
    plane.SetInputArrayToProcess(0, 0, 0, 0, isosurface)

    # Set number of contours
    plane.SetNumberOfContours(1)

    # Set values
    plane.SetValue(0, isovalue)
    # plane.GenerateValues(10, [0,1])

    # Polydata Mapper
    rgrid_mapper = vtk.vtkPolyDataMapper()
    rgrid_mapper.SetInputConnection(plane.GetOutputPort())

    # Scalar Visibilty.. Controls whether to auto color the isosurfaces
    rgrid_mapper.ScalarVisibilityOff()

    # Actor
    actor = vtk.vtkActor()
    actor.SetMapper(rgrid_mapper)
    actor.GetProperty().SetOpacity(1)
    actor.GetProperty().SetColor(0.8, 0.8, 0.8)
    actor.RotateX(-90)

    # Create the usual rendering stuff.
    renderer = vtk.vtkRenderer()
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetOffScreenRendering(1)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(render_window)

    # Renderer
    renderer.AddActor(actor)
    renderer.SetBackground(0, 0, 0)
    renderer.ResetCamera()
    render_window.SetSize(2400, 2400)
    renderer.GetActiveCamera().Zoom(0.5)
    render_window.Render()

    # Initilize
    iren.Initialize()
    iren.Start()

    # for fname in filenames:
        # #Update the file name
        # update_reader(fname)


        # for i in range (50):
            # renderer.GetActiveCamera().Azimuth(-0.3)
            # iren.GetRenderWindow().Render()
            
        # iren.GetRenderWindow().Render()
        


if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser()
    argparser.add_argument('input')

    args = argparser.parse_args()

    ds = xr.open_dataset(args.input, decode_times=False)

    path = Path('temp/')
    path.mkdir(exist_ok=True)

    vtr_file = str(list(path.glob('*.vtr'))[0])

    # _create_vtk_files(ds=ds, path=path)
    _render_frame_with_vtk(vtr_file)
