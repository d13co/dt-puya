"""dt-algorand's time-travel ops, which only its POST /v2/query runs.

The methods that read before a seek and use the value after it check that the optimizer keeps
reads on the side of the seek they were written on.
"""

from algopy import (
    Account,
    Application,
    ARC4Contract,
    Asset,
    Box,
    Bytes,
    Global,
    GlobalState,
    UInt64,
    arc4,
    gtxn,
    op,
    subroutine,
)


class Point(arc4.Struct):
    a: arc4.UInt64
    b: arc4.UInt64


class TimeTravel(ARC4Contract, avm_version=13):
    def __init__(self) -> None:
        self.counter = GlobalState(UInt64(0))
        self.data = Box(Bytes, key=b"data")
        self.items = Box(arc4.DynamicArray[arc4.UInt64], key=b"items")
        self.point = Box(Point, key=b"pt")

    @arc4.abimethod
    def round_at(self, rnd: UInt64) -> UInt64:
        op.TimeTravel.seek(rnd)
        return Global.round

    @arc4.abimethod
    def round_before(self, rnd: UInt64) -> UInt64:
        before = Global.round
        op.TimeTravel.seek(rnd)
        return before

    @arc4.abimethod
    def counter_then_and_now(self, rnd: UInt64) -> tuple[UInt64, UInt64]:
        home = Global.round - 1  # seeking to the round before the program's goes back to it
        now = self.counter.value
        op.TimeTravel.seek(rnd)
        then = self.counter.value
        op.TimeTravel.seek(home)
        return then, now

    @arc4.abimethod
    def data_changed(self, rnd: UInt64) -> bool:
        now = self.data.value
        op.TimeTravel.seek(rnd)
        then = self.data.value
        return now[:8] != then[:8]

    @arc4.abimethod
    def first_item_changed(self, rnd: UInt64) -> bool:
        now = self.items.value.copy()
        go_back(rnd)
        then = self.items.value.copy()
        return now[0] != then[0]

    @arc4.abimethod
    def first_item_now(self, rnd: UInt64) -> arc4.UInt64:
        first = self.items.value[0]
        op.TimeTravel.seek(rnd)
        return first

    @arc4.abimethod
    def append_then_write_back(self, rnd: UInt64, x: arc4.UInt64) -> None:
        items = self.items.value.copy()
        items.append(x)
        op.TimeTravel.seek(rnd)
        self.items.value = items.copy()

    @arc4.abimethod
    def set_then_write_back(self, rnd: UInt64, x: arc4.UInt64) -> None:
        point = self.point.value.copy()
        point.a = x
        op.TimeTravel.seek(rnd)
        self.point.value = point.copy()

    @arc4.abimethod
    def timestamps(self, rnd: UInt64, of: UInt64) -> UInt64:
        now = op.Block.blk_timestamp(of)
        op.TimeTravel.seek(rnd)
        then = op.Block.blk_timestamp(of)
        return now + then

    @arc4.abimethod
    def data_existed(self, rnd: UInt64) -> Bytes:
        existed = bool(self.data)
        op.TimeTravel.seek(rnd)
        then = self.data.value
        assert existed
        return then

    @arc4.abimethod
    def data_existed_before_call(self, rnd: UInt64) -> Bytes:
        existed = bool(self.data)
        go_back_not_inlined(rnd)
        then = self.data.value
        assert existed
        return then

    @arc4.abimethod
    def data_existed_before_delete(self) -> Bytes:
        existed = bool(self.data)
        del self.data.value
        assert existed
        return self.data.value  # keeps its exists assert: the box is gone

    @arc4.abimethod
    def first_item_if(self, first: bool) -> arc4.UInt64:
        # doesn't seek, so the box read is still combined with the read of its first item
        items = self.items.value.copy()
        if first:
            return items[0]
        return items[1]

    @arc4.abimethod
    def first_valid_then_and_now(self, i: UInt64, rnd: UInt64) -> UInt64:
        now = gtxn.Transaction(i).first_valid
        op.TimeTravel.seek(rnd)
        then = gtxn.Transaction(i).first_valid
        return now + then

    @arc4.abimethod
    def data_exists_then(self, rnd: UInt64) -> bool:
        assert self.data.length
        op.TimeTravel.seek(rnd)
        return bool(self.data)

    @arc4.abimethod
    def changes(
        self, acct: Account, asset: Asset, app: Application, from_: UInt64, to: UInt64
    ) -> UInt64:
        total = UInt64(0)
        rnd, status = op.TimeTravel.acct_change(acct, from_, to)
        total += rnd + status
        rnd, status = op.TimeTravel.holding_change(acct, asset, from_, to)
        total += rnd + status
        rnd, status = op.TimeTravel.local_change(acct, app, from_, to)
        total += rnd + status
        rnd, status = op.TimeTravel.asset_change(asset, from_, to)
        total += rnd + status
        rnd, status = op.TimeTravel.app_change(app, from_, to)
        total += rnd + status
        rnd, status = op.TimeTravel.box_change(app, b"data", from_, to)
        total += rnd + status
        rnd, status, value = op.TimeTravel.global_key_change_uint64(app, b"counter", from_, to)
        total += rnd + status + value
        rnd, status, name = op.TimeTravel.global_key_change_bytes(app, b"name", from_, to)
        total += rnd + status
        # the value is uint64 0 unless the key was created or changed
        if status in (UInt64(1), UInt64(2)):
            total += name.length
        rnd, status, value = op.TimeTravel.local_key_change_uint64(acct, app, b"n", from_, to)
        total += rnd + status + value
        rnd, status, name = op.TimeTravel.local_key_change_bytes(acct, app, b"s", from_, to)
        total += rnd + status
        # the value is uint64 0 unless the key was created or changed
        if status in (UInt64(1), UInt64(2)):
            total += name.length
        rnd, status, name = op.TimeTravel.box_prefix_change(app, b"it", from_, to)
        total += rnd + status + name.length
        return total


@subroutine
def go_back(rnd: UInt64) -> None:
    op.TimeTravel.seek(rnd)


@subroutine(inline=False)
def go_back_not_inlined(rnd: UInt64) -> None:
    op.TimeTravel.seek(rnd)
