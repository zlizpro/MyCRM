"""
MiniCRM 表单面板核心组件

整合使用模块化组件的简化表单面板，符合200行代码限制。
使用FormFieldFactory、FormValidator和FormDataBinder提供完整的表单功能。
"""

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from minicrm.ui.components.base_widget import BaseWidget
from minicrm.ui.components.form_data_binder import FormDataBinder
from minicrm.ui.components.form_field_factory import FormFieldFactory
from minicrm.ui.components.form_validator import FormValidator


class FormPanelCore(BaseWidget):
    """
    表单面板核心组件

    使用模块化设计的简化表单面板：
    - 使用FormFieldFactory创建字段
    - 使用FormValidator进行验证
    - 使用FormDataBinder管理数据绑定
    - 保持在200行代码限制内

    Signals:
        form_submitted: 表单提交信号 (data: dict[str, Any])
        form_reset: 表单重置信号
        field_changed: 字段变化信号 (field_key: str, value: Any)
    """

    # Qt信号定义
    form_submitted = Signal(dict)
    form_reset = Signal()
    field_changed = Signal(str, object)

    def __init__(
        self,
        fields: list[dict[str, Any]],
        layout_type: str = "form",
        parent: QWidget = None,
    ):
        """
        初始化表单面板

        Args:
            fields: 字段配置列表
            layout_type: 布局类型 ("form", "grid", "vertical")
            parent: 父组件
        """
        # 配置
        self._fields = fields
        self._layout_type = layout_type

        # 模块化组件
        self._field_factory = FormFieldFactory()
        self._validator = FormValidator()
        self._data_binder = FormDataBinder()

        # UI组件
        self._field_widgets: dict[str, QWidget] = {}
        self._field_labels: dict[str, QWidget] = {}
        self._button_frame: QFrame | None = None

        # 调用父类初始化
        super().__init__(parent)

        # 设置验证规则
        self._setup_validation_rules()

        self._logger.debug(f"表单面板初始化完成: {len(fields)}个字段")

    def setup_ui(self) -> None:
        """设置用户界面"""
        try:
            # 主布局
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 10, 10, 10)
            layout.setSpacing(15)

            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            # 创建表单容器
            form_widget = QWidget()
            self._create_form_layout(form_widget)
            scroll_area.setWidget(form_widget)

            layout.addWidget(scroll_area)

            # 创建操作按钮
            self._create_buttons(layout)

        except Exception as e:
            self._logger.error(f"表单UI设置失败: {e}")
            raise

    def _create_form_layout(self, parent_widget: QWidget) -> None:
        """创建表单布局"""
        if self._layout_type == "form":
            layout = QFormLayout(parent_widget)
            self._create_form_fields(layout)
        elif self._layout_type == "grid":
            grid_layout = QGridLayout(parent_widget)
            self._create_grid_fields(grid_layout)
        else:  # vertical
            vertical_layout = QVBoxLayout(parent_widget)
            self._create_vertical_fields(vertical_layout)

    def _create_form_fields(self, layout: QFormLayout) -> None:
        """创建表单字段（QFormLayout）"""
        for field in self._fields:
            field_widget, label_widget = self._field_factory.create_field_widget(field)

            if field_widget and label_widget:
                field_key = field.get("key", "")

                # 存储组件引用
                self._field_widgets[field_key] = field_widget
                self._field_labels[field_key] = label_widget

                # 注册到数据绑定器
                self._data_binder.register_field(field_key, field_widget, field)

                # 创建错误标签
                error_label = self._field_factory.create_error_label(field_key)
                self._validator.set_error_label(field_key, error_label)

                # 创建容器
                container_widget = QWidget()
                container_layout = QVBoxLayout(container_widget)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.addWidget(field_widget)
                container_layout.addWidget(error_label)

                layout.addRow(label_widget, container_widget)

    def _create_grid_fields(self, layout: QGridLayout) -> None:
        """创建网格字段（QGridLayout）"""
        row = 0
        col = 0
        max_cols = 2

        for field in self._fields:
            field_widget, label_widget = self._field_factory.create_field_widget(field)

            if field_widget and label_widget:
                field_key = field.get("key", "")

                self._field_widgets[field_key] = field_widget
                self._field_labels[field_key] = label_widget
                self._data_binder.register_field(field_key, field_widget, field)

                error_label = self._field_factory.create_error_label(field_key)
                self._validator.set_error_label(field_key, error_label)

                # 添加到网格
                layout.addWidget(label_widget, row, col * 2)
                layout.addWidget(field_widget, row, col * 2 + 1)
                layout.addWidget(error_label, row + 1, col * 2 + 1)

                col += 1
                if col >= max_cols:
                    col = 0
                    row += 2

    def _create_vertical_fields(self, layout: QVBoxLayout) -> None:
        """创建垂直字段（QVBoxLayout）"""
        for field in self._fields:
            field_widget, label_widget = self._field_factory.create_field_widget(field)

            if field_widget and label_widget:
                field_key = field.get("key", "")

                self._field_widgets[field_key] = field_widget
                self._field_labels[field_key] = label_widget
                self._data_binder.register_field(field_key, field_widget, field)

                error_label = self._field_factory.create_error_label(field_key)
                self._validator.set_error_label(field_key, error_label)

                # 创建分组
                group_box = QGroupBox(field.get("label", field_key))
                group_layout = QVBoxLayout(group_box)
                group_layout.addWidget(field_widget)
                group_layout.addWidget(error_label)

                layout.addWidget(group_box)

    def _create_buttons(self, layout: QVBoxLayout) -> None:
        """创建操作按钮"""
        self._button_frame = QFrame()
        button_layout = QHBoxLayout(self._button_frame)
        button_layout.addStretch()

        # 提交按钮
        submit_btn = QPushButton("提交")
        submit_btn.clicked.connect(self.submit_form)
        button_layout.addWidget(submit_btn)

        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self.reset_form)
        button_layout.addWidget(reset_btn)

        layout.addWidget(self._button_frame)

    def _setup_validation_rules(self) -> None:
        """设置验证规则"""
        for field in self._fields:
            field_key = field.get("key", "")

            # 必填验证
            if field.get("required", False):
                rule = self._validator.create_required_rule()
                self._validator.add_validation_rule(field_key, rule)

            # 其他验证规则可以在这里添加

    def setup_connections(self) -> None:
        """设置信号连接"""
        # 字段变化监听在子类中实现
        pass

    def apply_styles(self) -> None:
        """应用样式"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ced4da;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

    # 公共接口方法
    def set_data(self, data: dict[str, Any]) -> None:
        """设置表单数据"""
        self._data_binder.set_data(data)

    def get_data(self) -> dict[str, Any]:
        """获取表单数据"""
        return self._data_binder.get_data()

    def validate_form(self) -> bool:
        """验证表单"""
        form_data = self.get_data()
        return self._validator.validate_form(form_data)

    def submit_form(self) -> None:
        """提交表单"""
        try:
            if self.validate_form():
                data = self.get_data()
                self.form_submitted.emit(data)
                self._logger.debug("表单提交成功")
            else:
                self._logger.warning("表单验证失败")

        except Exception as e:
            self._logger.error(f"表单提交失败: {e}")

    def reset_form(self) -> None:
        """重置表单"""
        try:
            self._data_binder.reset_to_original()
            self._validator.clear_errors()
            self.form_reset.emit()
            self._logger.debug("表单已重置")

        except Exception as e:
            self._logger.error(f"表单重置失败: {e}")

    def clear_form(self) -> None:
        """清空表单"""
        try:
            self._data_binder.clear_data()
            self._validator.clear_errors()
            self._logger.debug("表单已清空")

        except Exception as e:
            self._logger.error(f"表单清空失败: {e}")

    def is_modified(self) -> bool:
        """检查表单是否已修改"""
        return self._data_binder.is_modified()

    def cleanup_resources(self) -> None:
        """清理资源"""
        try:
            # 清理组件引用
            self._field_widgets.clear()
            self._field_labels.clear()

            self._logger.debug("表单面板资源清理完成")

        except Exception as e:
            self._logger.error(f"表单面板资源清理失败: {e}")

    def __str__(self) -> str:
        """返回表单的字符串表示"""
        return f"FormPanelCore(fields={len(self._fields)}, layout={self._layout_type})"
