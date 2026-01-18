#  Copyright (c) 2025-2026 Half_nothing
#  SPDX-License-Identifier: MIT

from typing import Optional, Type, TypeVar, cast, overload

from PySide6.QtWidgets import QLineEdit, QWidget


def show_error(widget: QWidget) -> None:
    widget.setStyleSheet("background-color: #ef9a9a;color: white")


def clear_error(widget: QWidget) -> None:
    widget.setStyleSheet("")


def get_line_edit_str(line: QLineEdit) -> Optional[str]:
    data = line.text()
    if data:
        clear_error(line)
        return data
    show_error(line)
    return None


def get_line_edit_int(line: QLineEdit) -> Optional[int]:
    data = line.text()
    if not data:
        show_error(line)
        return None
    try:
        data = int(data)
        clear_error(line)
        return data
    except ValueError:
        show_error(line)
        return None


T = TypeVar("T", bound=type)

_handlers = {
    str: get_line_edit_str,
    int: get_line_edit_int,
}


@overload
def get_line_edit_data(line: QLineEdit, data_type: Type[str]) -> Optional[str]: ...


@overload
def get_line_edit_data(line: QLineEdit, data_type: Type[int]) -> Optional[int]: ...


def get_line_edit_data(line: QLineEdit, data_type: Type[T]) -> Optional[T]:
    handler = _handlers.get(data_type)
    if handler is not None:
        result = handler(line)
        return cast(Optional[T], result)
    return None
