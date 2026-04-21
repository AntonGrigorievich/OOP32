import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from model import TripleModel, TripleState


class ValueRow:
    def __init__(self, title: str, min_value: int, max_value: int) -> None:
        self.title = title
        self.group = QGroupBox(title)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Введите число")

        self.spin = QSpinBox()
        self.spin.setRange(min_value, max_value)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_value, max_value)

        layout = QGridLayout(self.group)
        layout.addWidget(QLabel("TextBox"), 0, 0)
        layout.addWidget(self.line_edit, 0, 1)
        layout.addWidget(QLabel("NumericUpDown"), 1, 0)
        layout.addWidget(self.spin, 1, 1)
        layout.addWidget(QLabel("TrackBar"), 2, 0)
        layout.addWidget(self.slider, 2, 1)


class MainWindow(QMainWindow):
    def __init__(self, model: TripleModel) -> None:
        super().__init__()
        self.setWindowTitle("ЛР 3.2 MVC")
        self.resize(920, 460)

        self._model = model
        self._is_syncing = False
        self._ui_update_count = 0

        self._row_a = ValueRow("A", model.min_value, model.max_value)
        self._row_b = ValueRow("B", model.min_value, model.max_value)
        self._row_c = ValueRow("C", model.min_value, model.max_value)

        self._status = QLabel("Обновлений UI: 0 | Уведомлений модели: 0")

        root = QWidget()
        wrapper = QVBoxLayout(root)
        wrapper.setSpacing(10)

        wrapper.addWidget(self._row_a.group)
        wrapper.addWidget(self._row_b.group)
        wrapper.addWidget(self._row_c.group)

        footer = QHBoxLayout()
        footer.addWidget(self._status)
        footer.addStretch(1)
        wrapper.addLayout(footer)

        self.setCentralWidget(root)

        self._bind_view_events()
        self._model.add_listener(self._on_model_changed)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._model.persist()
        super().closeEvent(event)

    def _bind_view_events(self) -> None:
        self._row_a.spin.valueChanged.connect(self._on_a_from_spin)
        self._row_a.slider.valueChanged.connect(self._on_a_from_slider)
        self._row_a.line_edit.editingFinished.connect(self._on_a_from_text)

        self._row_b.spin.valueChanged.connect(self._on_b_from_spin)
        self._row_b.slider.valueChanged.connect(self._on_b_from_slider)
        self._row_b.line_edit.editingFinished.connect(self._on_b_from_text)

        self._row_c.spin.valueChanged.connect(self._on_c_from_spin)
        self._row_c.slider.valueChanged.connect(self._on_c_from_slider)
        self._row_c.line_edit.editingFinished.connect(self._on_c_from_text)

    def _on_a_from_spin(self, value: int) -> None:
        if self._is_syncing:
            return
        self._model.set_a(value)

    def _on_a_from_slider(self, value: int) -> None:
        if self._is_syncing:
            return
        self._model.set_a(value)

    def _on_a_from_text(self) -> None:
        if self._is_syncing:
            return
        parsed = self._model.parse_user_number(self._row_a.line_edit.text())
        if parsed is None:
            self._sync_from_state(self._model.state())
            return
        self._model.set_a(parsed)

    def _on_b_from_spin(self, value: int) -> None:
        if self._is_syncing:
            return
        self._model.set_b(value)

    def _on_b_from_slider(self, value: int) -> None:
        if self._is_syncing:
            return
        self._model.set_b(value)

    def _on_b_from_text(self) -> None:
        if self._is_syncing:
            return
        parsed = self._model.parse_user_number(self._row_b.line_edit.text())
        if parsed is None:
            self._sync_from_state(self._model.state())
            return
        self._model.set_b(parsed)

    def _on_c_from_spin(self, value: int) -> None:
        if self._is_syncing:
            return
        self._model.set_c(value)

    def _on_c_from_slider(self, value: int) -> None:
        if self._is_syncing:
            return
        self._model.set_c(value)

    def _on_c_from_text(self) -> None:
        if self._is_syncing:
            return
        parsed = self._model.parse_user_number(self._row_c.line_edit.text())
        if parsed is None:
            self._sync_from_state(self._model.state())
            return
        self._model.set_c(parsed)

    def _on_model_changed(self, state: TripleState) -> None:
        self._sync_from_state(state)

    def _sync_from_state(self, state: TripleState) -> None:
        self._is_syncing = True
        self._ui_update_count += 1

        self._set_row_value(self._row_a, state.a)
        self._set_row_value(self._row_b, state.b)
        self._set_row_value(self._row_c, state.c)

        self._status.setText(
            f"Обновлений UI: {self._ui_update_count} | Уведомлений модели: {self._model.notify_count} | "
            f"A={state.a}, B={state.b}, C={state.c}"
        )

        self._is_syncing = False

    def _set_row_value(self, row: ValueRow, value: int) -> None:
        row.spin.setValue(value)
        row.slider.setValue(value)
        row.line_edit.setText(str(value))


def main() -> None:
    app = QApplication(sys.argv)
    settings_path = Path(__file__).resolve().parent / "lab32_state.json"
    model = TripleModel(settings_path)
    window = MainWindow(model)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
