from typing import Any

import bpy
import numpy as np

from SourceIO.blender_bindings.material_loader.shader_base import Nodes, ExtraMaterialParameters
from SourceIO.blender_bindings.material_loader.shaders.source2_shader_base import Source2ShaderBase
from SourceIO.blender_bindings.utils.bpy_utils import is_blender_4_3


class VrComplex(Source2ShaderBase):
    SHADER: str = 'hero.vfx'

    @property
    def color_texture(self):
        texture_path = self._material_resource.get_texture_property('g_tColor', None)
        if texture_path is not None:
            image = self.load_texture_or_default(texture_path, (0.3, 0.3, 0.3, 1.0))
            return image
        return None

    @property
    def normal_texture(self):
        texture_path = self._material_resource.get_texture_property('g_tNormal', None)
        if texture_path is not None:
            image = self.load_texture_or_default(texture_path, (0.5, 0.5, 1.0, 1.0))
            image.colorspace_settings.is_data = True
            image.colorspace_settings.name = 'Non-Color'
            return image
        return None

    @property
    def detail_2(self):
        texture_path = self._material_resource.get_texture_property('g_tDetail2', None)
        if texture_path is not None:
            image = self.load_texture_or_default(texture_path, (0.5, 0.5, 1.0, 1.0))
            image.colorspace_settings.is_data = True
            image.colorspace_settings.name = 'Non-Color'
            return image
        return None

    @property
    def mask_2(self):
        texture_path = self._material_resource.get_texture_property('g_tMasks2', None)
        if texture_path is not None:
            image = self.load_texture_or_default(texture_path, (0.5, 0.5, 1.0, 1.0))
            image.colorspace_settings.is_data = True
            image.colorspace_settings.name = 'Non-Color'
            return image
        return None

    @property
    def mask_1(self):
        texture_path = self._material_resource.get_texture_property('g_tMasks1', None)
        if texture_path is not None:
            image = self.load_texture_or_default(texture_path, (0.5, 0.5, 1.0, 1.0))
            image.colorspace_settings.is_data = True
            image.colorspace_settings.name = 'Non-Color'
            return image
        return None

    @property
    def self_illum_mask_texture(self):
        texture_path = self._material_resource.get_texture_property('g_tSelfIllumMask', None)
        if texture_path is not None:
            image = self.load_texture_or_default(texture_path, (1.0, 1.0, 1.0, 1.0))
            image.colorspace_settings.is_data = True
            image.colorspace_settings.name = 'Non-Color'
            return image
        return None

    @property
    def color(self):
        return self._material_resource.get_vector_property('g_vColorTint', np.ones(4, dtype=np.float32))

    @property
    def alpha_test(self):
        return self._material_resource.get_int_property('F_ALPHA_TEST', 0)

    @property
    def mask_2_enabled(self):
        return self._material_resource.get_int_property('F_MASKS_2', 0)

    @property
    def mask_1_enabled(self):
        return self._material_resource.get_int_property('F_MASKS_1', 0)

    @property
    def metalness(self):
        return self._material_resource.get_int_property('F_METALNESS_TEXTURE', 0)

    @property
    def translucent(self):
        return self._material_resource.get_int_property('F_TRANSLUCENT', 0)

    @property
    def specular(self):
        return self._material_resource.get_int_property('F_SPECULAR', 0)

    @property
    def roughness_value(self):
        value = self._material_resource.get_vector_property('TextureRoughness', None)
        if value is None:
            return
        return value[0]

    def create_nodes(self, material:bpy.types.Material, extra_parameters: dict[ExtraMaterialParameters, Any]):

        material_output = self.create_node(Nodes.ShaderNodeOutputMaterial)
        shader = self.create_node(Nodes.ShaderNodeBsdfPrincipled, self.SHADER)
        self.connect_nodes(shader.outputs['BSDF'], material_output.inputs['Surface'])

        color_texture = self.color_texture
        normal_texture = self.normal_texture
        self_illum_mask_texture = self.self_illum_mask_texture

        albedo_node = self.create_node(Nodes.ShaderNodeTexImage, 'albedo')
        albedo_node.image = color_texture

        if self.color[0] != 1.0 and self.color[1] != 1.0 and self.color[2] != 1.0:
            color_mix = self.create_node(Nodes.ShaderNodeMixRGB)
            color_mix.blend_type = 'MULTIPLY'
            self.connect_nodes(albedo_node.outputs['Color'], color_mix.inputs['Color1'])
            color = self.color
            if sum(color) > 3:
                color = list(np.divide(color, 255))
            color_mix.inputs['Color2'].default_value = color
            color_mix.inputs['Fac'].default_value = 1.0
            self.connect_nodes(color_mix.outputs['Color'], shader.inputs['Base Color'])
        else:
            self.connect_nodes(albedo_node.outputs['Color'], shader.inputs['Base Color'])

        if self.translucent or self.alpha_test:
            if not is_blender_4_3():
                self.bpy_material.blend_method = 'HASHED'
                self.bpy_material.shadow_method = 'HASHED'
            self.connect_nodes(albedo_node.outputs['Alpha'], shader.inputs['Alpha'])
        elif self.metalness:
            self.connect_nodes(albedo_node.outputs['Alpha'], shader.inputs['Metallic'])

        normal_map_texture = self.create_node(Nodes.ShaderNodeTexImage, 'normal')
        normal_map_texture.image = normal_texture

        normalmap_node = self.create_node(Nodes.ShaderNodeNormalMap)

        self.connect_nodes(normal_map_texture.outputs['Color'], normalmap_node.inputs['Color'])
        self.connect_nodes(normalmap_node.outputs['Normal'], shader.inputs['Normal'])

        if self.specular and self.self_illum_mask_texture:
            r, g, b, a = self.split_to_channels(self.self_illum_mask_texture)
            b = 1 - b
            roughness_texture = self.make_texture(
                self.new_texture_name_with_suffix(self.self_illum_mask_texture.name, 'roughness', 'tga'),
                self_illum_mask_texture.size, np.dstack((b, b, b, np.ones_like(b))))
            roughness_node = self.create_node(Nodes.ShaderNodeTexImage, 'roughness')
            roughness_node.image = roughness_texture
            self.connect_nodes(roughness_node.outputs['Color'], shader.inputs['Roughness'])
        elif self.roughness_value is None:
            self.connect_nodes(normal_map_texture.outputs['Alpha'], shader.inputs['Roughness'])
        elif self.roughness_value is not None:
            shader.inputs['Roughness'].default_value = self.roughness_value
        # if self.selfillum:
        #     selfillummask = self.selfillummask
        #     albedo_node = self.get_node('$basetexture')
        #     if selfillummask is not None:
        #         selfillummask_node = self.create_node(Nodes.ShaderNodeTexImage, '$selfillummask')
        #         selfillummask_node.image = selfillummask
        #         self.connect_nodes(selfillummask_node.outputs['Color'], shader.inputs['Emission Strength'])
        #
        #     else:
        #         self.connect_nodes(albedo_node.outputs['Alpha'], shader.inputs['Emission Strength'])
        #     self.connect_nodes(albedo_node.outputs['Color'], shader.inputs['Emission'])
