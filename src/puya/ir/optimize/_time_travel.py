"""Time travel: dt-algorand's tt_seek op moves a program's reads to a past round.

After a seek, every box, global and local state read, `global Round` and `global
LatestTimestamp` return what they were at the round sought, until the program seeks again, and
the rounds that `block` and `txn FirstValidTime` may read move with it: a read that succeeded
before a seek may fail after it. So a read can't move across a seek, nor reuse the result of a
read made before it. Only dt-algorand's POST /v2/query runs tt_seek; a program without it
compiles as it always has.
"""

from collections.abc import Mapping

from puya.ir import models
from puya.ir.avm_ops import AVMOp


def program_seeks(program: models.Program) -> bool:
    """Whether any subroutine of the program runs tt_seek."""
    return any(
        is_seek(op)
        for subroutine in program.all_subroutines
        for block in subroutine.body
        for op in block.ops
    )


def is_seek(op: models.Op) -> bool:
    return isinstance(op, models.Intrinsic) and op.op == AVMOp.tt_seek


def may_seek(op: models.Op) -> bool:
    """Whether op runs tt_seek, or calls a subroutine that may."""
    match op:
        case (
            models.InvokeSubroutine(target=target)
            | models.Assignment(source=models.InvokeSubroutine(target=target))
        ):
            return not target.pure
        case _:
            return is_seek(op)


def unsought_box_reads(
    subroutine: models.Subroutine,
) -> Mapping[int, tuple[object, frozenset[models.Register]]]:
    """The box reads that no seek may have come after, at each op of subroutine and at the value
    each assignment assigns, by id and beside the op or value: those earlier in the op's block
    with no seek, nor call that may seek, between them and it. Combining a box read with an op
    reads the box at that op, so only these may be combined with it."""
    unsought = dict[int, tuple[object, frozenset[models.Register]]]()
    for block in subroutine.body:
        reads = set[models.Register]()
        for op in block.ops:
            before = frozenset(reads)
            unsought[id(op)] = (op, before)
            if isinstance(op, models.Assignment):
                unsought[id(op.source)] = (op.source, before)
            match op:
                case models.Assignment(targets=[target], source=models.BoxRead()):
                    reads.add(target)
                case _ if may_seek(op):
                    reads.clear()
    return unsought
