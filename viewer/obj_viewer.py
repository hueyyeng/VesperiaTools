import pyrender
import trimesh

WIDTH = 640
HEIGHT = 480
BG_COLOR = (0.5, 0.5, 0.5, 0.5)


def show_viewer(obj_path=None):
    obj_trimesh = trimesh.load(obj_path)
    if isinstance(obj_trimesh, trimesh.scene.scene.Scene):
        scene = pyrender.Scene.from_trimesh_scene(obj_trimesh)
    else:
        mesh = pyrender.Mesh.from_trimesh(obj_trimesh)
        scene = pyrender.Scene()
        scene.add(mesh)

    scene.bg_color = BG_COLOR
    scene.ambient_light = (1.0, 1.0, 1.0)
    kwargs = {
        "use_direct_lighting": True,
    }
    pyrender.Viewer(
        scene,
        render_flags={
            'cull_faces': False,
        },
        **kwargs,
    )
