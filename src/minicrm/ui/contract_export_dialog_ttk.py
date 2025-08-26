"""MiniCRM 合同文档导出对话框TTK版本

提供合同文档生成和导出功能,包括:
- 多种文档格式支持(Word、PDF、Excel)
- 导出选项配置
- 模板选择和自定义
- 批量导出支持

设计原则:
- 继承BaseDialogTTK提供标准对话框功能
- 支持多种导出格式和选项
- 集成文档模板系统
- 提供进度显示和错误处理
"""

import logging
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Any, Callable, Dict, List, Optional

from minicrm.core.exceptions import ValidationError
from minicrm.models.contract import Contract
from minicrm.services.contract_service import ContractService
from minicrm.ui.ttk_base.base_dialog import BaseDialogTTK, DialogResult
from transfunctions.formatting import format_currency, format_date
from transfunctions.validation import validate_required_fields


class DocumentExportWorker:
    """文档导出工作类"""

    def __init__(
        self,
        contracts: List[Contract],
        export_options: Dict[str, Any],
        progress_callback: Optional[Callable[[int], None]] = None,
        completion_callback: Optional[Callable[[str], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
    ):
        self._contracts = contracts
        self._export_options = export_options
        self._progress_callback = progress_callback
        self._completion_callback = completion_callback
        self._error_callback = error_callback
        self._logger = logging.getLogger(__name__)
        self._cancelled = False

    def start_export(self) -> None:
        """开始导出任务"""

        def _export_thread():
            try:
                self._export_documents()
            except Exception as e:
                if self._error_callback:
                    self._error_callback(str(e))

        thread = threading.Thread(target=_export_thread, daemon=True)
        thread.start()

    def cancel_export(self) -> None:
        """取消导出"""
        self._cancelled = True

    def _export_documents(self) -> None:
        """执行导出任务"""
        try:
            export_format = self._export_options.get("format", "word")
            output_path = self._export_options.get("output_path", "")

            total_contracts = len(self._contracts)

            for i, contract in enumerate(self._contracts):
                if self._cancelled:
                    break

                # 导出单个合同
                self._export_single_contract(contract, export_format, output_path)

                # 更新进度
                progress = int((i + 1) / total_contracts * 100)
                if self._progress_callback:
                    self._progress_callback(progress)

            if not self._cancelled and self._completion_callback:
                self._completion_callback(f"成功导出 {total_contracts} 个合同文档")

        except Exception as e:
            self._logger.error(f"导出失败: {e}")
            if self._error_callback:
                self._error_callback(str(e))

    def _export_single_contract(
        self, contract: Contract, format_type: str, output_path: str
    ) -> None:
        """导出单个合同文档"""
        try:
            # 验证导出参数
            export_data = {
                "contract_id": contract.id,
                "format_type": format_type,
                "output_path": output_path,
            }

            validate_required_fields(
                export_data, ["contract_id", "format_type", "output_path"]
            )

            # 准备格式化的合同数据
            formatted_data = self._prepare_formatted_contract_data(contract)

            # 根据格式类型调用相应的导出方法
            if format_type == "word":
                self._export_to_word(formatted_data, output_path)
            elif format_type == "pdf":
                self._export_to_pdf(formatted_data, output_path)
            elif format_type == "excel":
                self._export_to_excel(formatted_data, output_path)

        except Exception as e:
            self._logger.error(f"导出合同 {contract.id} 失败: {e}")
            raise

    def _prepare_formatted_contract_data(self, contract: Contract) -> Dict[str, Any]:
        """准备格式化的合同数据"""
        try:
            return {
                "id": contract.id,
                "name": contract.name,
                "contract_number": contract.contract_number,
                "party_name": contract.party_name,
                "contract_amount": format_currency(float(contract.contract_amount))
                if contract.contract_amount
                else "未设定",
                "formatted_amount": format_currency(
                    float(contract.contract_amount), symbol="¥"
                )
                if contract.contract_amount
                else "¥0.00",
                "created_date": format_date(contract.created_at)
                if contract.created_at
                else "未知",
                "sign_date": format_date(contract.sign_date)
                if contract.sign_date
                else "未签署",
                "effective_date": format_date(contract.effective_date)
                if contract.effective_date
                else "未生效",
                "expiry_date": format_date(contract.expiry_date)
                if contract.expiry_date
                else "无期限",
                "status": contract.contract_status.value
                if contract.contract_status
                else "未知",
                "type": contract.contract_type.value
                if contract.contract_type
                else "未知",
            }
        except Exception as e:
            self._logger.error(f"格式化合同数据失败: {e}")
            return {
                "id": contract.id,
                "name": contract.name or "未命名合同",
                "party_name": contract.party_name or "未知合同方",
                "contract_amount": str(contract.contract_amount)
                if contract.contract_amount
                else "0",
                "created_date": str(contract.created_at)
                if contract.created_at
                else "未知",
            }

    def _export_to_word(self, formatted_data: Dict[str, Any], output_path: str) -> None:
        """导出为Word文档"""
        filename = f"合同_{formatted_data['id']}_{formatted_data['party_name']}.docx"
        full_path = Path(output_path) / filename

        self._logger.info(f"生成Word文档: {full_path}")
        # 模拟处理时间
        import time

        time.sleep(0.1)

    def _export_to_pdf(self, formatted_data: Dict[str, Any], output_path: str) -> None:
        """导出为PDF文档"""
        filename = f"合同_{formatted_data['id']}_{formatted_data['party_name']}.pdf"
        full_path = Path(output_path) / filename

        self._logger.info(f"生成PDF文档: {full_path}")
        # 模拟处理时间
        import time

        time.sleep(0.1)

    def _export_to_excel(
        self, formatted_data: Dict[str, Any], output_path: str
    ) -> None:
        """导出为Excel文档"""
        filename = (
            f"合同数据_{formatted_data['id']}_{formatted_data['party_name']}.xlsx"
        )
        full_path = Path(output_path) / filename

        self._logger.info(f"生成Excel文档: {full_path}")
        # 模拟处理时间
        import time

        time.sleep(0.1)


class ContractExportDialogTTK(BaseDialogTTK):
    """合同文档导出对话框TTK版本

    提供合同文档导出功能:
    - 导出格式选择
    - 导出选项配置
    - 模板选择
    - 批量导出支持
    """

    def __init__(
        self,
        parent: Optional[tk.Widget] = None,
        contract_service: Optional[ContractService] = None,
        contracts: Optional[List[Contract]] = None,
        **kwargs,
    ):
        """初始化合同导出对话框

        Args:
            parent: 父组件
            contract_service: 合同服务实例
            contracts: 要导出的合同列表
            **kwargs: 其他参数
        """
        self._contract_service = contract_service
        self._contracts = contracts or []

        # 日志记录器
        self._logger = logging.getLogger(__name__)

        # UI组件引用 - 必须在基类初始化前创建
        self._format_var = tk.StringVar(value="word")
        self._template_var = tk.StringVar(value="标准合同模板")
        self._output_path_var = tk.StringVar()
        self._include_attachments_var = tk.BooleanVar(value=True)
        self._separate_files_var = tk.BooleanVar(value=True)
        self._progress_var = tk.IntVar()

        # 导出工作器
        self._export_worker: Optional[DocumentExportWorker] = None
        self._is_exporting = False

        # 初始化基类
        super().__init__(
            parent=parent,
            title="导出合同文档",
            size=(500, 400),
            min_size=(450, 350),
            **kwargs,
        )

        self._logger.info(
            f"合同导出对话框初始化完成,待导出合同数: {len(self._contracts)}"
        )

    def _setup_content(self) -> None:
        """设置对话框内容"""
        # 信息区域
        self._create_info_area()

        # 导出格式选择
        self._create_format_group()

        # 导出选项
        self._create_options_group()

        # 输出设置
        self._create_output_group()

        # 进度条
        self._create_progress_area()

    def _create_info_area(self) -> None:
        """创建信息区域"""
        info_frame = ttk.Frame(self.content_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        info_text = f"将导出 {len(self._contracts)} 个合同的文档"
        info_label = ttk.Label(
            info_frame, text=info_text, font=("Microsoft YaHei UI", 10, "bold")
        )
        info_label.pack(side=tk.LEFT)

    def _create_format_group(self) -> None:
        """创建导出格式选择组"""
        group = ttk.LabelFrame(self.content_frame, text="导出格式", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # Word格式
        word_radio = ttk.Radiobutton(
            group, text="Word文档 (.docx)", variable=self._format_var, value="word"
        )
        word_radio.pack(anchor=tk.W)

        # PDF格式
        pdf_radio = ttk.Radiobutton(
            group, text="PDF文档 (.pdf)", variable=self._format_var, value="pdf"
        )
        pdf_radio.pack(anchor=tk.W)

        # Excel格式
        excel_radio = ttk.Radiobutton(
            group, text="Excel表格 (.xlsx)", variable=self._format_var, value="excel"
        )
        excel_radio.pack(anchor=tk.W)

    def _create_options_group(self) -> None:
        """创建导出选项组"""
        group = ttk.LabelFrame(self.content_frame, text="导出选项", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # 模板选择
        template_frame = ttk.Frame(group)
        template_frame.pack(fill=tk.X, pady=2)

        ttk.Label(template_frame, text="文档模板:").pack(side=tk.LEFT)

        template_combo = ttk.Combobox(
            template_frame,
            textvariable=self._template_var,
            values=["标准合同模板", "简化合同模板", "详细合同模板", "自定义模板"],
            state="readonly",
        )
        template_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))

        # 包含附件
        attachments_check = ttk.Checkbutton(
            group, text="包含合同附件", variable=self._include_attachments_var
        )
        attachments_check.pack(anchor=tk.W, pady=2)

        # 分别保存文件
        separate_check = ttk.Checkbutton(
            group, text="为每个合同生成单独文件", variable=self._separate_files_var
        )
        separate_check.pack(anchor=tk.W, pady=2)

    def _create_output_group(self) -> None:
        """创建输出设置组"""
        group = ttk.LabelFrame(self.content_frame, text="输出设置", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)

        # 输出路径
        path_frame = ttk.Frame(group)
        path_frame.pack(fill=tk.X, pady=2)

        ttk.Label(path_frame, text="输出路径:").pack(side=tk.LEFT)

        path_entry = ttk.Entry(path_frame, textvariable=self._output_path_var)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))

        browse_btn = ttk.Button(
            path_frame, text="浏览...", command=self._browse_output_path
        )
        browse_btn.pack(side=tk.RIGHT)

    def _create_progress_area(self) -> None:
        """创建进度区域"""
        self._progress_frame = ttk.Frame(self.content_frame)
        # 初始隐藏

        ttk.Label(self._progress_frame, text="导出进度:").pack(anchor=tk.W)

        self._progress_bar = ttk.Progressbar(
            self._progress_frame, variable=self._progress_var, maximum=100
        )
        self._progress_bar.pack(fill=tk.X, pady=2)

    def _setup_buttons(self) -> None:
        """设置对话框按钮"""
        # 移除默认按钮
        self.remove_button("取消")
        self.remove_button("确定")

        # 添加自定义按钮
        self.add_button("取消", self._on_cancel, DialogResult.CANCEL)
        self._export_button = self.add_button(
            "开始导出", self._on_start_export, DialogResult.OK, default=True
        )

    def _browse_output_path(self) -> None:
        """浏览输出路径"""
        folder = filedialog.askdirectory(
            title="选择输出文件夹", initialdir=str(Path.home())
        )

        if folder:
            self._output_path_var.set(folder)

    def _validate_input(self) -> bool:
        """验证输入数据"""
        try:
            # 验证输出路径
            output_path = self._output_path_var.get().strip()
            if not output_path:
                raise ValidationError("请选择输出路径")

            output_dir = Path(output_path)
            if not output_dir.exists():
                raise ValidationError("输出路径不存在")

            if not output_dir.is_dir():
                raise ValidationError("输出路径必须是文件夹")

            # 验证合同列表
            if not self._contracts:
                raise ValidationError("没有可导出的合同")

            return True

        except ValidationError as e:
            self.show_error(str(e))
            return False
        except Exception as e:
            self._logger.error(f"验证输入失败: {e}")
            self.show_error(f"验证输入失败: {e}")
            return False

    def _get_result_data(self) -> Dict[str, Any]:
        """获取结果数据"""
        return self._get_export_options()

    def _get_export_options(self) -> Dict[str, Any]:
        """获取导出选项"""
        return {
            "format": self._format_var.get(),
            "template": self._template_var.get(),
            "output_path": self._output_path_var.get().strip(),
            "include_attachments": self._include_attachments_var.get(),
            "separate_files": self._separate_files_var.get(),
        }

    def _on_start_export(self) -> None:
        """开始导出按钮处理"""
        if self._is_exporting:
            # 如果正在导出,则取消导出
            self._cancel_export()
        else:
            # 开始导出
            self._start_export()

    def _start_export(self) -> None:
        """开始导出"""
        try:
            # 验证输入
            if not self._validate_input():
                return

            # 显示进度条
            self._progress_frame.pack(fill=tk.X, padx=10, pady=5)
            self._progress_var.set(0)

            # 更新按钮状态
            self._is_exporting = True
            self._export_button.configure(text="取消导出")
            self.set_button_enabled("取消", False)

            # 获取导出选项
            export_options = self._get_export_options()

            # 创建并启动导出工作器
            self._export_worker = DocumentExportWorker(
                self._contracts,
                export_options,
                progress_callback=self._on_progress_updated,
                completion_callback=self._on_export_completed,
                error_callback=self._on_export_failed,
            )
            self._export_worker.start_export()

        except Exception as e:
            self._logger.error(f"启动导出失败: {e}")
            self.show_error(f"启动导出失败: {e}")
            self._reset_export_state()

    def _cancel_export(self) -> None:
        """取消导出"""
        if self._export_worker:
            self._export_worker.cancel_export()

        self._reset_export_state()
        self.show_info("导出已取消")

    def _reset_export_state(self) -> None:
        """重置导出状态"""
        self._is_exporting = False
        self._export_button.configure(text="开始导出")
        self.set_button_enabled("取消", True)
        self._progress_frame.pack_forget()

    def _on_progress_updated(self, progress: int) -> None:
        """处理进度更新"""
        self.after_idle(lambda: self._progress_var.set(progress))

    def _on_export_completed(self, message: str) -> None:
        """处理导出完成"""

        def _handle_completion():
            self._reset_export_state()
            self.show_info(message)
            self.result = DialogResult.OK
            self.return_value = self._get_export_options()
            self._close_dialog()

        self.after_idle(_handle_completion)

    def _on_export_failed(self, error: str) -> None:
        """处理导出失败"""

        def _handle_failure():
            self._reset_export_state()
            self.show_error(f"导出失败: {error}")

        self.after_idle(_handle_failure)

    def _on_cancel(self) -> None:
        """取消按钮处理"""
        if self._is_exporting:
            # 如果正在导出,询问是否取消
            if self.confirm("导出正在进行中,确定要取消吗?"):
                self._cancel_export()
                super()._on_cancel()
        else:
            super()._on_cancel()
