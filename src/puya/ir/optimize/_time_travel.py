"""Time travel: dt-algorand's tt_seek op moves a program's reads to a past round.

After a seek, every ledger read (box, global and local state, balances, holdings, account,
asset and app params), `global Round` and `global LatestTimestamp` return what they were at the
round sought, until the program seeks again; the group's txns read the round after it as their
FirstValid and LastValid and its timestamp as FirstValidTime, and the rounds `block` may read
move with it: a read that succeeded before a seek may fail after it. So a read can't move
across a seek, nor reuse the result of a read made before it. Only dt-algorand's POST
/v2/query runs tt_seek; a program without it compiles as it always has.

The optimizer keeps reads on their side of a seek as follows:
- the passes that track state op by op within a block (repeated loads, box exists asserts)
  forget what they know at a tt_seek, as at any impure call;
- the passes that reuse or combine reads across ops by other means (repeated expressions,
  box extract/replace combining) do so in a subroutine that may seek, one that runs tt_seek or
  calls one that may, only where no seek can come between the ops (see `seeking_subroutines`
  and `may_seek`).
"""

from collections.abc import Set

from puya.ir import models
from puya.ir.avm_ops import AVMOp


def seeking_subroutines(program: models.Program) -> frozenset[str]:
    """The ids of the subroutines of program that may seek: those that run tt_seek, or call one
    that may."""
    callers = dict[str, set[str]]()
    seeking = set[str]()
    for subroutine in program.all_subroutines:
        for block in subroutine.body:
            for op in block.ops:
                if is_seek(op):
                    seeking.add(subroutine.id)
                elif (callee := _callee(op)) is not None:
                    callers.setdefault(callee.id, set()).add(subroutine.id)
    pending = list(seeking)
    while pending:
        for caller in callers.get(pending.pop(), ()):
            if caller not in seeking:
                seeking.add(caller)
                pending.append(caller)
    return frozenset(seeking)


def is_seek(op: models.Op | models.ValueProvider) -> bool:
    return isinstance(op, models.Intrinsic) and op.op == AVMOp.tt_seek


def may_seek(op: models.Op | models.ValueProvider, seeking: Set[str]) -> bool:
    """Whether op runs tt_seek, or calls a subroutine of seeking."""
    callee = _callee(op)
    if callee is not None:
        return callee.id in seeking
    return is_seek(op)


def _callee(op: models.Op | models.ValueProvider) -> models.Subroutine | None:
    match op:
        case (
            models.InvokeSubroutine(target=target)
            | models.Assignment(source=models.InvokeSubroutine(target=target))
        ):
            return target
        case _:
            return None
