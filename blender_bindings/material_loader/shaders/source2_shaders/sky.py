from typing import Any

import bpy
import numpy as np

from ..source2_shader_base import Source2ShaderBase
from ...shader_base import Nodes, ExtraMaterialParameters
from SourceIO.library.shared.content_manager import ContentManager
from SourceIO.library.source2 import CompiledTextureResource
from SourceIO.library.source2.blocks.texture_data import VTexFormat
from SourceIO.library.utils.path_utilities import path_stem
from SourceIO.library.utils.thirdparty.equilib.cube2equi_numpy import run as convert_to_eq
from SourceIO.logger import SourceLogMan

log_manager = SourceLogMan()


class Skybox(Source2ShaderBase):
    SHADER: str = 'sky.vfx'

    def __init__(self, content_manager: ContentManager, source2_material):
        super().__init__(content_manager, source2_material)
        self.content_manager = content_manager
        self.logger = log_manager.get_logger(f'Shaders::{self.SHADER}')
        self.do_arrange = True

    @property
    def sky_texture(self):

        texture_path = self._material_resource.get_texture_property('g_tSkyTexture', None)
        if texture_path:
            texture_resource = self._material_resource.get_child_resource(texture_path, self.content_manager,
                                                                          CompiledTextureResource)
            (width, height) = texture_resource.get_resolution(0)
            faces = {}
            for i, k in enumerate("FBLRUD"):
                data, _ = texture_resource.get_cubemap_face(i, 0)
                side = data.reshape((width, height, 4))
                if k == 'B':
                    side = np.rot90(side, 2)
                if k == 'L':
                    side = np.rot90(side, 3)
                if k == 'R':
                    side = np.rot90(side, 1)
                faces[k] = side.T

            pixel_data = convert_to_eq(faces, "dict", 2048, 1024, 'default', 'bilinear').T
            pixel_data = np.rot90(pixel_data, 1)
            # pixel_data = np.flipud(pixel_data)
            name = path_stem(texture_path)
            image = bpy.data.images.new(
                name + '.tga',
                width=2048,
                height=1024,
                alpha=True
            )
            image.alpha_mode = 'CHANNEL_PACKED'
            if pixel_data.shape[0] == 0:
                return None

            pixel_format = texture_resource.get_texture_format()
            if pixel_format in (VTexFormat.RGBA16161616F, VTexFormat.BC6H):
                image.use_generated_float = True
                image.file_format = 'HDR'
                image.pixels.foreach_set(pixel_data.astype(np.float32).ravel())
            else:
                image.file_format = 'PNG'
                image.pixels.foreach_set(pixel_data.ravel())

            image.pack()
            return image
        return None

    def create_nodes(self, material:bpy.types.Material, extra_parameters: dict[ExtraMaterialParameters, Any]):
        self.logger.info(f'Creating material {repr(material.name)}')
        self.bpy_material = material

        if self.bpy_material is None:
            self.logger.error('Failed to get or create material')
            return 'UNKNOWN'

        if self.bpy_material.get('source_loaded'):
            return 'LOADED'

        self.bpy_material.use_nodes = True
        self.clean_nodes()
        self.bpy_material['source_loaded'] = True

        material_output = self.create_node(Nodes.ShaderNodeOutputWorld)
        shader = self.create_node(Nodes.ShaderNodeBackground, self.SHADER)
        self.connect_nodes(shader.outputs['Background'], material_output.inputs['Surface'])

        texture = self.create_node(Nodes.ShaderNodeTexEnvironment)
        texture.image = self.sky_texture
        self.connect_nodes(texture.outputs['Color'], shader.inputs['Color'])
