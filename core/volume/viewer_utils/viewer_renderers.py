import vtk
from typing import Optional

class ViewerRenderers:
    @staticmethod
    def configure_3d_renderer(renderer: vtk.vtkRenderer,
                              volume_data: vtk.vtkImageData,
                              color_func: vtk.vtkColorTransferFunction,
                              opacity_func: vtk.vtkPiecewiseFunction) -> vtk.vtkVolume:
        renderer.RemoveAllViewProps()

        mapper = vtk.vtkSmartVolumeMapper()
        mapper.SetInputData(volume_data)

        prop = vtk.vtkVolumeProperty()
        prop.SetColor(color_func)
        prop.SetScalarOpacity(opacity_func)
        prop.SetInterpolationTypeToLinear()
        prop.SetShade(True)

        volume_actor = vtk.vtkVolume()
        volume_actor.SetMapper(mapper)
        volume_actor.SetProperty(prop)

        renderer.AddActor(volume_actor)
        return volume_actor

    @staticmethod
    def configure_mpr_renderer(renderer: vtk.vtkRenderer,
                               volume_data: vtk.vtkImageData,
                               normal: tuple,
                               origin: tuple) -> vtk.vtkImageSlice:
        renderer.RemoveAllViewProps()

        mapper = vtk.vtkImageResliceMapper()
        mapper.SetInputData(volume_data)
        mapper.SliceFacesCameraOff()
        mapper.SliceAtFocalPointOff()

        plane = vtk.vtkPlane()
        plane.SetNormal(normal)
        plane.SetOrigin(origin)
        mapper.SetSlicePlane(plane)

        vtk_prop = vtk.vtkImageProperty()
        vtk_prop.SetColorWindow(2000)
        vtk_prop.SetColorLevel(400)
        vtk_prop.SetInterpolationTypeToLinear()

        actor = vtk.vtkImageSlice()
        actor.SetMapper(mapper)
        actor.SetProperty(vtk_prop)

        renderer.AddActor(actor)
        return actor

    @staticmethod
    def update_reslice_position(mapper: vtk.vtkImageResliceMapper,
                                axis: int,
                                pos_fisica: float):
        plane = mapper.GetSlicePlane()
        if plane:
            nova_origem = list(plane.GetOrigin())
            nova_origem[axis] = pos_fisica
            plane.SetOrigin(nova_origem)

    @staticmethod
    def setup_camera_mpr(renderer: vtk.vtkRenderer,
                         centro: tuple,
                         axis: int,
                         view_up: tuple,
                         is_axial: bool):
        cam = renderer.GetActiveCamera()
        cam.SetParallelProjection(True)
        cam.SetFocalPoint(centro)

        pos_cam = list(centro)
        # Inverte direção da câmera para o plano Axial para manter orientação radiológica
        pos_cam[axis] += -1000 if is_axial else 1000

        cam.SetPosition(pos_cam)
        cam.SetViewUp(view_up)
        renderer.ResetCamera()