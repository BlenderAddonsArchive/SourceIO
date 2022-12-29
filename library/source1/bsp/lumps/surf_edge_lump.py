import numpy as np

from SourceIO.library.utils import IBuffer
from .. import Lump, lump_tag, LumpInfo
from ..bsp_file import BSPFile


@lump_tag(13, 'LUMP_SURFEDGES')
class SurfEdgeLump(Lump):
    def __init__(self, lump_info: LumpInfo):
        super().__init__(lump_info)
        self.surf_edges = np.array([])

    def parse(self, buffer: IBuffer, bsp: 'BSPFile'):
        self.surf_edges = np.frombuffer(buffer.read(), np.int32)
        return self
