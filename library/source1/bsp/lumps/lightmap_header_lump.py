from typing import List

from SourceIO.library.utils import IBuffer
from .. import Lump, lump_tag, LumpInfo
from ..bsp_file import BSPFile
from ..datatypes.lightmap_header import LightmapHeader


@lump_tag(0x53, 'LUMP_LIGHTMAP_HEADERS', bsp_version=29)
class LightmapHeadersLump(Lump):

    def __init__(self, lump_info: LumpInfo):
        super().__init__(lump_info)
        self.lightmap_headers: List[LightmapHeader] = []

    def parse(self, buffer: IBuffer, bsp: 'BSPFile'):
        while buffer:
            self.lightmap_headers.append(LightmapHeader(self).parse(buffer, bsp))
        return self
