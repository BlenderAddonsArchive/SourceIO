from dataclasses import dataclass

from SourceIO.library.shared.types import Vector3
from SourceIO.library.utils import Buffer


@dataclass(slots=True)
class StudioBone:
    name: str
    parent: int
    flags: int
    bone_controllers: tuple[int, ...]
    pos: Vector3[float]
    rot: Vector3[float]
    pos_scale: Vector3[float]
    rot_scale: Vector3[float]

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return cls(buffer.read_ascii_string(32), buffer.read_int32(), buffer.read_int32(), buffer.read_fmt('6i'),
                   buffer.read_fmt('3f'), buffer.read_fmt('3f'), buffer.read_fmt('3f'), buffer.read_fmt('3f'))
