import lzma
from dataclasses import dataclass, field
from typing import Optional, Type, Union

from SourceIO.library.shared.app_id import SteamAppId
from SourceIO.library.utils.file_utils import Buffer, MemoryBuffer
from SourceIO.library.utils.math_utilities import sizeof_fmt



@dataclass(slots=True)
class LumpTag:
    lump_id: int
    lump_name: str
    lump_version: Optional[int] = field(default=None)
    bsp_version: Optional[Union[int, tuple[int, int]]] = field(default=None)
    steam_id: Optional[SteamAppId] = field(default=None)


def lump_tag(lump_id, lump_name,
             lump_version: Optional[int] = None,
             bsp_version: Optional[Union[int, tuple[int, int]]] = None,
             steam_id: Optional[SteamAppId] = None):
    def loader(klass: Type[Lump]) -> Type[Lump]:
        if not klass.tags:
            klass.tags = []
        if bsp_version is not None and isinstance(bsp_version, int):
            bsp_version_ = (bsp_version,0)
        else:
            bsp_version_ = bsp_version
        klass.tags.append(LumpTag(lump_id, lump_name, lump_version, bsp_version_, steam_id))
        return klass

    return loader


@dataclass(slots=True)
class AbstractLump:
    id: int
    offset: int
    size: int
    version: int

    @property
    def compressed(self):
        return False

    def __repr__(self):
        return f"<Lump{self.id}({self.id:04x}) o: {self.offset} s: {sizeof_fmt(self.size)}({self.size})>"


@dataclass(slots=True)
class RavenLumpInfo(AbstractLump):

    @classmethod
    def from_buffer(cls, buffer: Buffer, lump_type: int, is_l4d2: bool = False):
        return RavenLumpInfo(lump_type, buffer.read_int32(), buffer.read_int32(), 0)


@dataclass(slots=True)
class LumpInfo(AbstractLump):
    decompressed_size: int

    @property
    def compressed(self):
        return self.decompressed_size != 0

    @classmethod
    def from_buffer(cls, buffer: Buffer, lump_type: int, is_l4d2: bool = False):
        if is_l4d2:
            version = buffer.read_int32()
            offset = buffer.read_int32()
            size = buffer.read_int32()
            decompressed_size = buffer.read_uint32()
        else:
            offset = buffer.read_int32()
            size = buffer.read_int32()
            version = buffer.read_int32()
            decompressed_size = buffer.read_uint32()
        return cls(lump_type, offset, size, version, decompressed_size)


class Lump:
    tags: list[LumpTag]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.tags = []

    @property
    def version(self):
        return self._info.version

    @classmethod
    def all_subclasses(cls):
        return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in c.all_subclasses()])

    def __init__(self, lump_info: LumpInfo):
        self._info = lump_info

    # def parse(self, buffer: Buffer, bsp: 'BSPFile'):
    #     return self

    # noinspection PyUnresolvedReferences,PyProtectedMember
    @staticmethod
    def decompress_lump(buffer: Buffer) -> Buffer:
        magic = buffer.read_fourcc()
        assert magic == 'LZMA', f'Invalid LZMA compressed header: {magic}'

        decompressed_size = buffer.read_uint32()
        compressed_size = buffer.read_uint32()
        filter_properties = lzma._decode_filter_properties(lzma.FILTER_LZMA1, buffer.read(5))

        compressed_buffer = buffer.read(compressed_size)
        chunks: list[bytes] = []

        while True:
            decompressor = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=(filter_properties,))
            try:
                result = decompressor.decompress(compressed_buffer)
            except lzma.LZMAError:
                if not chunks:
                    raise  # Error on the first iteration; bail out.
                break  # Leftover data is not a valid LZMA/XZ stream; ignore it.
            chunks.append(result)
            compressed_buffer = decompressor.unused_data
            if not compressed_buffer:
                break
            assert decompressor.eof, 'Compressed data ended before the end-of-stream marker was reached'

        decompressed_buffer = b"".join(chunks)[:decompressed_size]
        assert decompressed_size == len(decompressed_buffer), 'Decompressed data does not match the expected size'
        return MemoryBuffer(decompressed_buffer)
