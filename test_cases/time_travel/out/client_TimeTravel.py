# This file is auto-generated, do not modify
# flake8: noqa
# fmt: off
import typing

import algopy


class TimeTravel(algopy.arc4.ARC4Client, typing.Protocol):
    @algopy.arc4.abimethod
    def round_at(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.UIntN[typing.Literal[64]]: ...

    @algopy.arc4.abimethod
    def round_before(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.UIntN[typing.Literal[64]]: ...

    @algopy.arc4.abimethod
    def counter_then_and_now(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.Tuple[algopy.arc4.UIntN[typing.Literal[64]], algopy.arc4.UIntN[typing.Literal[64]]]: ...

    @algopy.arc4.abimethod
    def data_changed(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.Bool: ...

    @algopy.arc4.abimethod
    def first_item_changed(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.Bool: ...

    @algopy.arc4.abimethod
    def first_item_now(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.UIntN[typing.Literal[64]]: ...

    @algopy.arc4.abimethod
    def append_then_write_back(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
        x: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> None: ...

    @algopy.arc4.abimethod
    def set_then_write_back(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
        x: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> None: ...

    @algopy.arc4.abimethod
    def timestamps(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
        of: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.UIntN[typing.Literal[64]]: ...

    @algopy.arc4.abimethod
    def data_existed(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.DynamicBytes: ...

    @algopy.arc4.abimethod
    def data_exists_then(
        self,
        rnd: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.Bool: ...

    @algopy.arc4.abimethod
    def changes(
        self,
        acct: algopy.arc4.Address,
        asset: algopy.arc4.UIntN[typing.Literal[64]],
        app: algopy.arc4.UIntN[typing.Literal[64]],
        from_: algopy.arc4.UIntN[typing.Literal[64]],
        to: algopy.arc4.UIntN[typing.Literal[64]],
    ) -> algopy.arc4.UIntN[typing.Literal[64]]: ...
