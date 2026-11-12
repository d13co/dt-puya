from collections.abc import Mapping

import attrs

from puya.context import ArtifactCompileContext
from puya.ir import models
from puya.ir._puya_lib import PuyaLibIR


@attrs.define(kw_only=True)
class IROptimizationContext(ArtifactCompileContext):
    expand_all_bytes: bool

    inlineable_calls: set[tuple[str, str]] = attrs.field(factory=set)
    """src -> dst pairs that can/should be inlined"""
    constant_with_constant_args: dict[str, bool] = attrs.field(factory=dict)
    embedded_funcs: Mapping[PuyaLibIR, models.Subroutine]
    time_travel: bool = False
    """the program runs tt_seek, so its reads may move to a past round (see _time_travel.py)"""
