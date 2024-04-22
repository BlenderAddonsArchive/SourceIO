from dataclasses import dataclass
from enum import IntFlag
from typing import Optional, Tuple

from SourceIO.library.shared.types import Vector3
from SourceIO.library.utils import Buffer


class StudioHDRFlags(IntFlag):
    AUTOGENERATED_HITBOX = (1 << 0)

    #  NOTE:  This flag is set at loadtime, not mdl build time so that we don't have to rebuild
    #  models when we change materials.
    USES_ENV_CUBEMAP = (1 << 1)

    # Use this when there are translucent parts to the model but we're not going to sort it
    FORCE_OPAQUE = (1 << 2)

    #  Use this when we want to render the opaque parts during the opaque pass
    #  and the translucent parts during the translucent pass
    TRANSLUCENT_TWOPASS = (1 << 3)

    #  This is set any time the .qc files has $staticprop in it
    #  Means there's no bones and no transforms
    STATIC_PROP = (1 << 4)

    #  NOTE:  This flag is set at loadtime, not mdl build time so that we don't have to rebuild
    #  models when we change materials.
    USES_FB_TEXTURE = (1 << 5)

    #  This flag is set by studiomdl.exe if a separate "$shadowlod" entry was present
    #   for the .mdl (the shadow lod is the last entry in the lod list if present)
    HASSHADOWLOD = (1 << 6)

    #  NOTE:  This flag is set at loadtime, not mdl build time so that we don't have to rebuild
    #  models when we change materials.
    USES_BUMPMAPPING = (1 << 7)

    #  NOTE:  This flag is set when we should use the actual materials on the shadow LOD
    # instead of overriding them with the default one (necessary for
    # translucent shadows)
    USE_SHADOWLOD_MATERIALS = (1 << 8)

    OBSOLETE = (1 << 9)
    UNUSED = (1 << 10)

    #  NOTE:  This flag is set at mdl build time
    NO_FORCED_FADE = (1 << 11)

    # NOTE:  The npc will lengthen the viseme check to always include two
    # phonemes
    FORCE_PHONEME_CROSSFADE = (1 << 12)

    #  This flag is set when the .qc has $constantdirectionallight in it
    #  If set, we use constantdirectionallightdot to calculate light intensity
    #  rather than the normal directional dot product
    #  only valid if STATIC_PROP is also set
    CONSTANT_DIRECTIONAL_LIGHT_DOT = (1 << 13)

    # Flag to mark delta flexes as already converted from disk format to
    # memory format
    FLEXES_CONVERTED = (1 << 14)

    #  Indicates the studiomdl was built in preview mode
    BUILT_IN_PREVIEW_MODE = (1 << 15)

    #  Ambient boost (runtime flag)
    AMBIENT_BOOST = (1 << 16)

    #  Don't cast shadows from this model (useful on first-person models)
    DO_NOT_CAST_SHADOWS = (1 << 17)

    # alpha textures should cast shadows in vrad on this model (ONLY prop_static!)
    CAST_TEXTURE_SHADOWS = (1 << 18)

    SUBDIVISION_SURFACE = (1 << 19)

    #  flagged on load to indicate no animation events on this model
    VERT_ANIM_FIXED_POINT_SCALE = (1 << 21)


@dataclass(slots=True)
class MdlHeaderV36:
    version: int
    checksum: int
    name: str
    file_size: int

    eye_position: Vector3[float]
    illumination_position: Vector3[float]
    hull_min: Vector3[float]
    hull_max: Vector3[float]
    view_bbox_min: Vector3[float]
    view_bbox_max: Vector3[float]

    flags: StudioHDRFlags

    bone_count: int
    bone_offset: int
    bone_controller_count: int
    bone_controller_offset: int
    hitbox_set_count: int
    hitbox_set_offset: int
    local_animation_count: int
    local_animation_offset: int
    local_sequence_count: int
    local_sequence_offset: int
    sequences_indexed_flag: int
    sequence_group_count: int
    sequence_group_offset: int
    texture_count: int
    texture_offset: int
    texture_path_count: int
    texture_path_offset: int
    skin_reference_count: int
    skin_family_count: int
    skin_family_offset: int
    body_part_count: int
    body_part_offset: int
    local_attachment_count: int
    local_attachment_offset: int
    transition_count: int
    transition_offset: int

    flex_desc_count: int
    flex_desc_offset: int
    flex_controller_count: int
    flex_controller_offset: int
    flex_rule_count: int
    flex_rule_offset: int
    ik_chain_count: int
    ik_chain_offset: int
    mouth_count: int
    mouth_offset: int
    local_pose_paramater_count: int
    local_pose_parameter_offset: int

    surface_prop: str

    key_value_offset: int
    key_value_size: int
    local_ik_auto_play_lock_count: int
    local_ik_auto_play_lock_offset: int
    mass: float
    contents: int
    reserved: tuple[int, ...]

    @classmethod
    def is_valid_file(cls, buffer: Buffer):
        with buffer.save_current_offset():
            fourcc = buffer.read_fourcc()
        return fourcc == "IDST"

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        ident = buffer.read_fourcc()
        assert ident == "IDST"
        version, checksum = buffer.read_fmt('ii')
        name = buffer.read_ascii_string(64)
        file_size = buffer.read_uint32()

        eye_position = buffer.read_fmt('3f')
        illumination_position = buffer.read_fmt('3f')
        hull_min = buffer.read_fmt('3f')
        hull_max = buffer.read_fmt('3f')

        view_bbox_min = buffer.read_fmt('3f')
        view_bbox_max = buffer.read_fmt('3f')

        flags = StudioHDRFlags(buffer.read_uint32())

        bone_count, bone_offset = buffer.read_fmt('2I')
        bone_controller_count, bone_controller_offset = buffer.read_fmt('2I')

        hitbox_set_count, hitbox_set_offset = buffer.read_fmt('2I')

        local_animation_count, local_animation_offset = buffer.read_fmt('2I')
        local_sequence_count, local_sequence_offset = buffer.read_fmt('2I')
        buffer.skip(16)
        sequences_indexed_flag, sequence_group_count = buffer.read_fmt('2I')
        sequence_group_offset = buffer.read_int32()

        texture_count, texture_offset = buffer.read_fmt('2I')
        texture_path_count, texture_path_offset = buffer.read_fmt('2I')
        skin_reference_count, skin_family_count, skin_family_offset = buffer.read_fmt('3I')

        body_part_count, body_part_offset = buffer.read_fmt('2I')
        local_attachment_count, local_attachment_offset = buffer.read_fmt('2I')

        transition_count, transition_offset = buffer.read_fmt('2I')

        flex_desc_count, flex_desc_offset = buffer.read_fmt('2I')
        flex_controller_count, flex_controller_offset = buffer.read_fmt('2I')
        flex_rule_count, flex_rule_offset = buffer.read_fmt('2I')

        ik_chain_count, ik_chain_offset = buffer.read_fmt('2I')
        mouth_count, mouth_offset = buffer.read_fmt('2I')

        local_pose_paramater_count, local_pose_parameter_offset = buffer.read_fmt('2I')

        surface_prop = buffer.read_source1_string(0)

        key_value_offset, key_value_size = buffer.read_fmt('2I')
        local_ik_auto_play_lock_count, local_ik_auto_play_lock_offset = buffer.read_fmt('2I')
        mass, contents = buffer.read_fmt('fI')
        reserved = buffer.read_fmt('9i')
        return cls(version, checksum, name, file_size, eye_position, illumination_position, hull_min, hull_max,
                   view_bbox_min, view_bbox_max, flags, bone_count, bone_offset, bone_controller_count,
                   bone_controller_offset, hitbox_set_count, hitbox_set_offset, local_animation_count,
                   local_animation_offset, local_sequence_count, local_sequence_offset, sequences_indexed_flag,
                   sequence_group_count, sequence_group_offset, texture_count,
                   texture_offset, texture_path_count, texture_path_offset, skin_reference_count, skin_family_count,
                   skin_family_offset, body_part_count, body_part_offset, local_attachment_count,
                   local_attachment_offset, transition_count, transition_offset, flex_desc_count,
                   flex_desc_offset, flex_controller_count, flex_controller_offset, flex_rule_count, flex_rule_offset,
                   ik_chain_count, ik_chain_offset, mouth_count, mouth_offset, local_pose_paramater_count,
                   local_pose_parameter_offset,
                   surface_prop,
                   key_value_offset,
                   key_value_size,
                   local_ik_auto_play_lock_count,
                   local_ik_auto_play_lock_offset,
                   mass,
                   contents,
                   reserved,
                   )


@dataclass(slots=True)
class MdlHeaderV44:
    version: int
    checksum: int
    name: str
    file_size: int

    eye_position: Vector3[float]
    illumination_position: Vector3[float]
    hull_min: Vector3[float]
    hull_max: Vector3[float]
    view_bbox_min: Vector3[float]
    view_bbox_max: Vector3[float]

    flags: StudioHDRFlags

    bone_count: int
    bone_offset: int
    bone_controller_count: int
    bone_controller_offset: int
    hitbox_set_count: int
    hitbox_set_offset: int
    local_animation_count: int
    local_animation_offset: int
    local_sequence_count: int
    local_sequence_offset: int
    activity_list_version: int
    events_indexed: int
    texture_count: int
    texture_offset: int
    texture_path_count: int
    texture_path_offset: int
    skin_reference_count: int
    skin_family_count: int
    skin_family_offset: int
    body_part_count: int
    body_part_offset: int
    local_attachment_count: int
    local_attachment_offset: int
    local_node_count: int
    local_node_offset: int
    local_node_name_offset: int

    flex_desc_count: int
    flex_desc_offset: int
    flex_controller_count: int
    flex_controller_offset: int
    flex_rule_count: int
    flex_rule_offset: int
    ik_chain_count: int
    ik_chain_offset: int
    mouth_count: int
    mouth_offset: int
    local_pose_paramater_count: int
    local_pose_parameter_offset: int

    surface_prop: str

    key_value_offset: int
    key_value_size: int
    local_ik_auto_play_lock_count: int
    local_ik_auto_play_lock_offset: int
    mass: float
    contents: int
    reserved: tuple[int, ...]
    include_model_count: int
    include_model_offset: int
    virtual_model_pointer: int
    anim_block_name: str
    anim_block_count: int
    anim_block_offset: int
    anim_block_model_pointer: int
    bone_table_by_name_offset: int
    vertex_base_pointer: int
    index_base_pointer: int
    directional_light_dot: int
    root_lod: int
    unused: int
    zero_frame_cache_offset: int
    flex_controller_ui_count: int
    flex_controller_ui_offset: int
    unused3: tuple[int, ...]
    studio_header2_offset: int
    unused2: int

    source_bone_transform_count: int
    source_bone_transform_offset: int
    illum_position_attachment_index: int
    max_eye_deflection: int
    linear_bone_offset: int

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        ident = buffer.read_fourcc()
        assert ident == "IDST"
        version, checksum = buffer.read_fmt('ii')
        name = buffer.read_ascii_string(64)
        file_size = buffer.read_uint32()
        eye_position = buffer.read_fmt('3f')
        illumination_position = buffer.read_fmt('3f')
        hull_min = buffer.read_fmt('3f')
        hull_max = buffer.read_fmt('3f')

        view_bbox_min = buffer.read_fmt('3f')
        view_bbox_max = buffer.read_fmt('3f')

        flags = StudioHDRFlags(buffer.read_uint32())

        bone_count, bone_offset = buffer.read_fmt('2I')
        bone_controller_count, bone_controller_offset = buffer.read_fmt('2I')

        hitbox_set_count, hitbox_set_offset = buffer.read_fmt('2I')

        local_animation_count, local_animation_offset = buffer.read_fmt('2I')
        local_sequence_count, local_sequence_offset = buffer.read_fmt('2I')
        activity_list_version, events_indexed = buffer.read_fmt('2I')

        texture_count, texture_offset = buffer.read_fmt('2I')
        texture_path_count, texture_path_offset = buffer.read_fmt('2I')
        skin_reference_count, skin_family_count, skin_family_offset = buffer.read_fmt('3I')

        body_part_count, body_part_offset = buffer.read_fmt('2I')
        local_attachment_count, local_attachment_offset = buffer.read_fmt('2I')
        local_node_count, local_node_offset, local_node_name_offset = buffer.read_fmt('3I')

        flex_desc_count, flex_desc_offset = buffer.read_fmt('2I')
        flex_controller_count, flex_controller_offset = buffer.read_fmt('2I')
        flex_rule_count, flex_rule_offset = buffer.read_fmt('2I')

        ik_chain_count, ik_chain_offset = buffer.read_fmt('2I')
        mouth_count, mouth_offset = buffer.read_fmt('2I')

        local_pose_paramater_count, local_pose_parameter_offset = buffer.read_fmt('2I')

        surface_prop = buffer.read_source1_string(0)

        key_value_offset, key_value_size = buffer.read_fmt('2I')
        local_ik_auto_play_lock_count, local_ik_auto_play_lock_offset = buffer.read_fmt('2I')
        mass, contents = buffer.read_fmt('fI')

        include_model_count, include_model_offset = buffer.read_fmt('2I')
        virtual_model_pointer = buffer.read_uint32()
        anim_block_name = buffer.read_source1_string(0)
        anim_block_count, anim_block_offset = buffer.read_fmt('2I')

        anim_block_model_pointer, bone_table_by_name_offset = buffer.read_fmt('2I')

        vertex_base_pointer, index_base_pointer = buffer.read_fmt('2I')

        directional_light_dot, root_lod, *unused = buffer.read_fmt('4b')
        zero_frame_cache_offset = buffer.read_int32()
        with buffer.save_current_offset():
            _, scal = buffer.read_fmt('2I')
        if scal == 1279345491:
            buffer.skip(5 * 4)
        flex_controller_ui_count, flex_controller_ui_offset = buffer.read_fmt('2I')
        unused3 = buffer.read_fmt('4I')

        studio_header2_offset, unused2 = buffer.read_fmt('2I')
        buffer.skip(4 * 9)
        source_bone_transform_count, source_bone_transform_offset = buffer.read_fmt('2I')
        illum_position_attachment_index, max_eye_deflection = buffer.read_fmt('If')
        linear_bone_offset, name_offset = buffer.read_fmt('2I')

        reserved = buffer.read_fmt('58i')

        return cls(version, checksum, name, file_size, eye_position, illumination_position, hull_min, hull_max,
                   view_bbox_min, view_bbox_max, flags, bone_count, bone_offset, bone_controller_count,
                   bone_controller_offset, hitbox_set_count, hitbox_set_offset, local_animation_count,
                   local_animation_offset, local_sequence_count, local_sequence_offset, activity_list_version,
                   events_indexed, texture_count, texture_offset, texture_path_count,
                   texture_path_offset, skin_reference_count, skin_family_count, skin_family_offset, body_part_count,
                   body_part_offset, local_attachment_count, local_attachment_offset, local_node_count,
                   local_node_offset, local_node_name_offset, flex_desc_count, flex_desc_offset, flex_controller_count,
                   flex_controller_offset, flex_rule_count, flex_rule_offset, ik_chain_count, ik_chain_offset,
                   mouth_count, mouth_offset, local_pose_paramater_count, local_pose_parameter_offset, surface_prop,
                   key_value_offset, key_value_size, local_ik_auto_play_lock_count, local_ik_auto_play_lock_offset,
                   mass, contents, reserved, include_model_count, include_model_offset, virtual_model_pointer,
                   anim_block_name, anim_block_count, anim_block_offset, anim_block_model_pointer,
                   bone_table_by_name_offset, vertex_base_pointer, index_base_pointer, directional_light_dot, root_lod,
                   unused, zero_frame_cache_offset, flex_controller_ui_count, flex_controller_ui_offset, unused3,
                   studio_header2_offset, unused2, source_bone_transform_count, source_bone_transform_offset,
                   illum_position_attachment_index, max_eye_deflection, linear_bone_offset, )


@dataclass(slots=True)
class MdlHeaderV49:
    version: int
    checksum: int
    name: str
    file_size: int

    eye_position: Vector3[float]
    illumination_position: Vector3[float]
    hull_min: Vector3[float]
    hull_max: Vector3[float]
    view_bbox_min: Vector3[float]
    view_bbox_max: Vector3[float]

    flags: StudioHDRFlags

    bone_count: int
    bone_offset: int
    bone_controller_count: int
    bone_controller_offset: int
    hitbox_set_count: int
    hitbox_set_offset: int
    local_animation_count: int
    local_animation_offset: int
    local_sequence_count: int
    local_sequence_offset: int
    activity_list_version: int
    events_indexed: int
    texture_count: int
    texture_offset: int
    texture_path_count: int
    texture_path_offset: int
    skin_reference_count: int
    skin_family_count: int
    skin_family_offset: int
    body_part_count: int
    body_part_offset: int
    local_attachment_count: int
    local_attachment_offset: int
    local_node_count: int
    local_node_offset: int
    local_node_name_offset: int

    flex_desc_count: int
    flex_desc_offset: int
    flex_controller_count: int
    flex_controller_offset: int
    flex_rule_count: int
    flex_rule_offset: int
    ik_chain_count: int
    ik_chain_offset: int
    mouth_count: int
    mouth_offset: int
    local_pose_paramater_count: int
    local_pose_parameter_offset: int

    surface_prop: str

    key_value_offset: int
    key_value_size: int
    local_ik_auto_play_lock_count: int
    local_ik_auto_play_lock_offset: int
    mass: float
    contents: int

    include_model_count: int
    include_model_offset: int
    virtual_model_pointer: int
    anim_block_name: str
    anim_block_count: int
    anim_block_offset: int
    anim_block_model_pointer: int
    bone_table_by_name_offset: int
    vertex_base_pointer: int
    index_base_pointer: int

    allowed_root_lod_count: int
    unused4: int

    flex_controller_ui_count: int
    flex_controller_ui_offset: int
    vert_anim_fixed_point_scale: float
    unused3: int
    studio_header2_offset: int
    unused2: int

    source_bone_transform_count: int
    source_bone_transform_offset: int
    illum_position_attachment_index: int
    max_eye_deflection: float
    linear_bone_offset: int

    bone_flex_driver_count: Optional[int]
    bone_flex_driver_offset: Optional[int]

    reserved: tuple[int, ...]

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        ident = buffer.read_fourcc()
        assert ident == "IDST"
        version, checksum = buffer.read_fmt('ii')
        name = buffer.read_ascii_string(64)
        file_size = buffer.read_uint32()
        assert file_size == buffer.size()

        eye_position = buffer.read_fmt('3f')
        illumination_position = buffer.read_fmt('3f')
        hull_min = buffer.read_fmt('3f')
        hull_max = buffer.read_fmt('3f')

        view_bbox_min = buffer.read_fmt('3f')
        view_bbox_max = buffer.read_fmt('3f')

        flags = StudioHDRFlags(buffer.read_uint32())

        bone_count, bone_offset = buffer.read_fmt('2I')
        bone_controller_count, bone_controller_offset = buffer.read_fmt('2I')

        hitbox_set_count, hitbox_set_offset = buffer.read_fmt('2I')

        local_animation_count, local_animation_offset = buffer.read_fmt('2I')
        local_sequence_count, local_sequence_offset = buffer.read_fmt('2I')
        activity_list_version, events_indexed = buffer.read_fmt('2I')

        texture_count, texture_offset = buffer.read_fmt('2I')
        texture_path_count, texture_path_offset = buffer.read_fmt('2I')
        skin_reference_count, skin_family_count, skin_family_offset = buffer.read_fmt('3I')

        body_part_count, body_part_offset = buffer.read_fmt('2I')
        local_attachment_count, local_attachment_offset = buffer.read_fmt('2I')
        local_node_count, local_node_offset, local_node_name_offset = buffer.read_fmt('3I')

        flex_desc_count, flex_desc_offset = buffer.read_fmt('2I')
        flex_controller_count, flex_controller_offset = buffer.read_fmt('2I')
        flex_rule_count, flex_rule_offset = buffer.read_fmt('2I')

        ik_chain_count, ik_chain_offset = buffer.read_fmt('2I')
        mouth_count, mouth_offset = buffer.read_fmt('2I')
        local_pose_paramater_count, local_pose_parameter_offset = buffer.read_fmt('2I')

        surface_prop = buffer.read_source1_string(0)

        key_value_offset, key_value_size = buffer.read_fmt('2I')
        local_ik_auto_play_lock_count, local_ik_auto_play_lock_offset = buffer.read_fmt('2I')
        mass, contents = buffer.read_fmt('fI')

        include_model_count, include_model_offset = buffer.read_fmt('2I')
        virtual_model_pointer = buffer.read_uint32()
        anim_block_name = buffer.read_source1_string(0)
        anim_block_count, anim_block_offset = buffer.read_fmt('2I')

        anim_block_model_pointer, bone_table_by_name_offset = buffer.read_fmt('2I')

        vertex_base_pointer, index_base_pointer = buffer.read_fmt('2I')

        directional_light_dot, root_lod, allowed_root_lod_count, unused = buffer.read_fmt('4b')

        unused4 = buffer.read_uint32()

        flex_controller_ui_count, flex_controller_ui_offset = buffer.read_fmt('2I')
        vert_anim_fixed_point_scale, unused3 = buffer.read_fmt('fI')
        studio_header2_offset, unused2 = buffer.read_fmt('2I')

        source_bone_transform_count, source_bone_transform_offset = buffer.read_fmt('2I')
        illum_position_attachment_index, max_eye_deflection = buffer.read_fmt('If')
        linear_bone_offset, name_offset = buffer.read_fmt('2I')

        if version > 47:
            bone_flex_driver_count, bone_flex_driver_offset = buffer.read_fmt('2I')
        else:
            bone_flex_driver_count, bone_flex_driver_offset = None, None

        reserved = buffer.read_fmt('56i')
        return cls(version, checksum, name, file_size, eye_position, illumination_position, hull_min, hull_max,
                   view_bbox_min, view_bbox_max, flags, bone_count, bone_offset, bone_controller_count,
                   bone_controller_offset, hitbox_set_count, hitbox_set_offset, local_animation_count,
                   local_animation_offset, local_sequence_count, local_sequence_offset, activity_list_version,
                   events_indexed, texture_count, texture_offset, texture_path_count,
                   texture_path_offset, skin_reference_count, skin_family_count, skin_family_offset, body_part_count,
                   body_part_offset, local_attachment_count, local_attachment_offset, local_node_count,
                   local_node_offset, local_node_name_offset, flex_desc_count, flex_desc_offset,
                   flex_controller_count, flex_controller_offset, flex_rule_count, flex_rule_offset, ik_chain_count,
                   ik_chain_offset, mouth_count, mouth_offset, local_pose_paramater_count, local_pose_parameter_offset,
                   surface_prop, key_value_offset, key_value_size, local_ik_auto_play_lock_count,
                   local_ik_auto_play_lock_offset, mass, contents, include_model_count, include_model_offset,
                   virtual_model_pointer, anim_block_name, anim_block_count, anim_block_offset,
                   anim_block_model_pointer, bone_table_by_name_offset, vertex_base_pointer, index_base_pointer,
                   allowed_root_lod_count, unused4, flex_controller_ui_count, flex_controller_ui_offset,
                   vert_anim_fixed_point_scale, unused3, studio_header2_offset, unused2, source_bone_transform_count,
                   source_bone_transform_offset, illum_position_attachment_index, max_eye_deflection,
                   linear_bone_offset, bone_flex_driver_count, bone_flex_driver_offset, reserved)