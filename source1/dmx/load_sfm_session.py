import math
from pathlib import Path
import bpy
from mathutils import Vector, Quaternion, Matrix, Euler

from .sfm.animation_set import AnimationSet
from .sfm.film_clip import FilmClip
from ...source_shared.content_manager import ContentManager
from ...source_shared.model_container import Source1ModelContainer
from ...utilities.math_utilities import HAMMER_UNIT_TO_METERS
from ...utilities.path_utilities import find_vtx, backwalk_file_resolver, find_vtx_cm
from .sfm import open_session
from .sfm.camera import Camera
from ..bsp.import_bsp import BSP
from ..mdl.import_mdl import import_model, import_materials


def _convert_quat(quat):
    # return Quaternion(quat[1:] + [quat[0]])
    return quat


def import_gamemodel(mdl_path, scale=HAMMER_UNIT_TO_METERS):
    mdl_path = Path(mdl_path)
    mld_file = ContentManager().find_file(mdl_path)
    if mld_file:
        vvd_file = ContentManager().find_file(mdl_path.with_suffix('.vvd'))
        vtx_file = find_vtx_cm(mdl_path, ContentManager())
        model_container = import_model(mld_file, vvd_file, vtx_file, scale, False, None, True, True)
        # import_materials(model_container.mdl)
        return model_container


def create_camera(dme_camera: Camera, scale=HAMMER_UNIT_TO_METERS):
    camera = bpy.data.cameras.new(name=dme_camera.name)
    camera_obj = bpy.data.objects.new(dme_camera.name, camera)

    bpy.context.scene.collection.objects.link(camera_obj)

    camera_obj.location = Vector(dme_camera.transform.position) * scale
    camera_obj.rotation_quaternion = Quaternion(dme_camera.transform.orientation)
    camera.lens = dme_camera.milliliters
    camera_obj.rotation_mode = 'QUATERNION'


def _apply_transforms(container: Source1ModelContainer, animset: AnimationSet, scale=HAMMER_UNIT_TO_METERS):
    for control in animset.controls:
        if control.type == 'DmElement':
            pass  # flex
        elif control.type == 'DmeTransformControl':
            bone_name = control.name
            tmp = control['valuePosition']
            pos = Vector(tmp)
            rot = _convert_quat(control['valueOrientation'])
            if container.armature:
                arm = container.armature
                bone = arm.pose.bones.get(bone_name, None)
                if bone:
                    qrot = Quaternion()
                    qrot.x, qrot.y, qrot.z, qrot.w = rot
                    # rot.x,rot.y,rot.z,rot.w = bone_.valueOrientation
                    erot = qrot.to_euler('YXZ')

                    if not bone.parent:
                        pos = arm.data.bones.get(bone_name).head - pos
                    # new_rot = Euler([math.pi / 2, 0, 0]).rotate(erot)
                    mat = Matrix.Translation(pos * scale) @ erot.to_matrix().to_4x4()
                    bone.matrix_basis.identity()
                    bone.matrix = bone.parent.matrix @ mat if bone.parent else mat


def load_animset(animset: AnimationSet, shot: FilmClip, scale=HAMMER_UNIT_TO_METERS):
    if animset.game_model:
        container = import_gamemodel(animset.game_model.model_name, scale)
        if container.armature:
            qrot = Quaternion()
            qrot.w, qrot.x, qrot.y, qrot.z = animset.game_model.transform.orientation
            # rot.x,rot.y,rot.z,rot.w = bone_.valueOrientation
            erot = qrot.to_euler('YXZ')
            new_rot = Euler([math.pi, 0, 0])
            new_rot.rotate(erot)
            mat = Matrix.Translation(Vector(animset.game_model.transform.position) * scale) @ new_rot.to_matrix().to_4x4()
            container.armature.matrix_basis.identity()
            container.armature.matrix_world = mat
        else:
            for obj in container.objects:
                qrot = Quaternion()
                qrot.w, qrot.x, qrot.y, qrot.z = animset.game_model.transform.orientation
                # rot.x,rot.y,rot.z,rot.w = bone_.valueOrientation
                erot = qrot.to_euler('YXZ')
                new_rot = Euler([math.pi, 0, 0])
                new_rot.rotate(erot)
                mat = Matrix.Translation(
                    Vector(animset.game_model.transform.position) * scale) @ new_rot.to_matrix().to_4x4()
                obj.matrix_basis.identity()
                obj.matrix_world = mat
        _apply_transforms(container, animset, scale)


def load_session(session_path: Path, scale=HAMMER_UNIT_TO_METERS):
    session = open_session(session_path)
    active_clip = session.active_clip
    map_file = active_clip.map_file
    if map_file:
        print(f'Loading {active_clip.map_name}')

        bsp_map = BSP(map_file, scale=scale)

        # bsp_map.load_disp()
        bsp_map.load_entities()
        # bsp_map.load_static_props()
        # bsp_map.load_detail_props()
        # bsp_map.load_materials()

    for shot in active_clip.sub_clip_track_group.tracks[0].children[:1]:
        camera = shot.camera
        create_camera(camera)
        for anim_set in shot.animation_sets:
            load_animset(anim_set, shot, scale)
