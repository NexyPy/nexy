"""The interactive prompts: pick one option or type a line; both go back and cancel."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl

from nexy.modules.cli.tui import render
from nexy.modules.cli.tui.render import Option
from nexy.modules.cli.tui.terminal import terminal
from nexy.modules.cli.tui.theme import STYLE, Glyphs, glyphs_for
from nexy.modules.cli.tui.transcript import transcript


class _Back:
    """What a prompt answers when the user goes back instead of answering."""

    def __repr__(self) -> str:
        return "BACK"


BACK = _Back()


def _glyphs() -> Glyphs:
    output = terminal.output
    return glyphs_for(output.encoding() if output is not None else "utf-8")


def _cancel(event: KeyPressEvent) -> None:
    event.app.exit(exception=KeyboardInterrupt)


def _bind_common(bindings: KeyBindings, back: bool) -> None:
    """Ctrl+C cancels; Escape goes back when the prompt allows it."""
    bindings.add("c-c", eager=True)(_cancel)
    if back:
        bindings.add("escape", eager=True)(lambda event: event.app.exit(result=BACK))


def _bind_select(bindings: KeyBindings, count: int, cursor: list[int], values: list[Any]) -> None:
    def move(step: int) -> Callable[[KeyPressEvent], None]:
        def handler(_event: KeyPressEvent) -> None:
            cursor[0] = (cursor[0] + step) % count

        return handler

    for key in ("up", "k", "s-tab"):
        bindings.add(key)(move(-1))
    for key in ("down", "j", "tab"):
        bindings.add(key)(move(1))
    bindings.add("home")(lambda _event: cursor.__setitem__(0, 0))
    bindings.add("end")(lambda _event: cursor.__setitem__(0, count - 1))
    bindings.add("enter", eager=True)(lambda event: event.app.exit(result=values[cursor[0]]))
    for number in range(1, min(count, 9) + 1):
        bindings.add(str(number))(lambda _event, n=number: cursor.__setitem__(0, n - 1))


def _select_bindings(choices: Sequence[Option], cursor: list[int], back: bool) -> KeyBindings:
    bindings = KeyBindings()
    _bind_common(bindings, back)
    _bind_select(bindings, len(choices), cursor, [choice.value for choice in choices])
    if back:
        bindings.add("left", eager=True)(lambda event: event.app.exit(result=BACK))
    return bindings


def _application(layout: Layout, bindings: KeyBindings) -> Application[Any]:
    return Application(
        layout=layout,
        key_bindings=bindings,
        style=STYLE,
        erase_when_done=True,
        input=terminal.input,
        output=terminal.output,
    )


def _select_application(
    message: str, choices: Sequence[Option], start: int, back: bool, glyphs: Glyphs
) -> Application[Any]:
    cursor = [start]

    def draw() -> FormattedText:
        return FormattedText(
            [
                *render.question(message, glyphs),
                *render.options(choices, cursor[0], glyphs),
                *render.footer(glyphs, back=back),
            ]
        )

    control = FormattedTextControl(draw, show_cursor=False)
    layout = Layout(Window(control, wrap_lines=True))
    return _application(layout, _select_bindings(choices, cursor, back))


def select(
    message: str,
    choices: Sequence[Option],
    *,
    default: Any = None,
    back: bool = True,
) -> Any:
    """Ask the user to pick one of *choices*; the value of the pick, or BACK."""
    glyphs = _glyphs()
    values = [choice.value for choice in choices]
    start = values.index(default) if default in values else 0
    answer = _select_application(message, choices, start, back, glyphs).run()
    if answer is BACK:
        return BACK
    label = choices[values.index(answer)].label
    transcript.show(render.answered(message, label, glyphs))
    return answer


def confirm(
    message: str,
    *,
    yes: str = "Yes",
    no: str = "No",
    yes_hint: str = "",
    no_hint: str = "",
    default: bool = True,
    back: bool = True,
) -> Any:
    """A yes/no question with a description for each answer; a bool, or BACK."""
    choices = [Option(True, yes, yes_hint), Option(False, no, no_hint)]
    return select(message, choices, default=default, back=back)


def _text_bindings(
    buffer: Buffer, validate: Callable[[str], bool | str] | None, problem: list[str], back: bool
) -> KeyBindings:
    bindings = KeyBindings()
    _bind_common(bindings, back)

    def submit(event: KeyPressEvent) -> None:
        verdict = validate(buffer.text) if validate else True
        if verdict is True:
            event.app.exit(result=buffer.text)
        else:
            problem[0] = str(verdict)

    bindings.add("enter", eager=True)(submit)
    return bindings


def _text_footer(problem: list[str], glyphs: Glyphs, back: bool) -> FormattedText:
    if problem[0]:
        return FormattedText(
            [("class:gutter", f"{glyphs.gutter}  "), ("class:error", problem[0] + "\n")]
        )
    return FormattedText(render.footer(glyphs, back=back, move=False))


def _text_application(
    message: str,
    buffer: Buffer,
    validate: Callable[[str], bool | str] | None,
    back: bool,
    glyphs: Glyphs,
) -> Application[Any]:
    problem = [""]
    mark = FormattedTextControl([("class:gutter", f"{glyphs.gutter}  ")])
    field = Window(BufferControl(buffer), height=1, style="class:input")
    header = FormattedTextControl(lambda: FormattedText(render.question(message, glyphs)))
    footer = FormattedTextControl(lambda: _text_footer(problem, glyphs, back))
    layout = HSplit(
        [
            Window(header, height=1),
            VSplit([Window(mark, width=3, height=1), field]),
            Window(footer, height=1),
        ]
    )
    bindings = _text_bindings(buffer, validate, problem, back)
    return _application(Layout(layout, focused_element=field), bindings)


def text(
    message: str,
    *,
    default: str = "",
    validate: Callable[[str], bool | str] | None = None,
    back: bool = False,
) -> Any:
    """Ask for a line of text; what was typed, or BACK. *validate* returns True or a message."""
    glyphs = _glyphs()
    buffer = Buffer(document=None, multiline=False)
    buffer.text = default
    buffer.cursor_position = len(default)
    answer = _text_application(message, buffer, validate, back, glyphs).run()
    if answer is BACK:
        return BACK
    transcript.show(render.answered(message, answer or default, glyphs))
    return answer
