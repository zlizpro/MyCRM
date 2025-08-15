"""
MiniCRM 图标生成器

程序化生成应用程序图标和其他UI图标
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QFont, QIcon, QPainter, QPen, QPixmap


def create_app_icon(size: int = 64) -> QIcon:
    """
    创建MiniCRM应用程序图标

    生成一个简单的CRM图标，包含：
    - 圆形背景
    - "CRM"文字
    - 现代化的设计风格

    Args:
        size: 图标大小（像素）

    Returns:
        QIcon: 生成的图标对象
    """
    # 创建像素图
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    # 创建画笔
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 设置背景圆形
    background_brush = QBrush(Qt.GlobalColor.blue)
    painter.setBrush(background_brush)
    painter.setPen(QPen(Qt.GlobalColor.darkBlue, 2))

    # 绘制圆形背景
    margin = 4
    painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)

    # 设置文字
    painter.setPen(QPen(Qt.GlobalColor.white))
    font = QFont("Arial", max(8, size // 8), QFont.Weight.Bold)
    painter.setFont(font)

    # 绘制"CRM"文字
    text_rect = pixmap.rect()
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "CRM")

    painter.end()

    return QIcon(pixmap)


def save_app_icon(file_path: str, size: int = 64) -> bool:
    """
    保存应用程序图标到文件

    Args:
        file_path: 保存路径
        size: 图标大小

    Returns:
        bool: 保存是否成功
    """
    try:
        icon = create_app_icon(size)
        pixmap = icon.pixmap(size, size)
        return pixmap.save(file_path, "PNG")
    except Exception:
        return False


def create_menu_icon(icon_type: str, size: int = 16) -> QIcon:
    """
    创建菜单图标

    Args:
        icon_type: 图标类型 ("new", "save", "open", "settings", etc.)
        size: 图标大小

    Returns:
        QIcon: 生成的图标
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 根据类型绘制不同的图标
    if icon_type == "new":
        # 绘制"+"号
        painter.setPen(QPen(Qt.GlobalColor.darkGreen, 2))
        center = size // 2
        painter.drawLine(center, 2, center, size - 2)
        painter.drawLine(2, center, size - 2, center)

    elif icon_type == "save":
        # 绘制磁盘图标
        painter.setBrush(QBrush(Qt.GlobalColor.blue))
        painter.setPen(QPen(Qt.GlobalColor.darkBlue, 1))
        painter.drawRect(2, 2, size - 4, size - 4)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.drawRect(4, 4, size - 8, size - 8)

    elif icon_type == "settings":
        # 绘制齿轮图标（简化版）
        painter.setBrush(QBrush(Qt.GlobalColor.gray))
        painter.setPen(QPen(Qt.GlobalColor.darkGray, 1))
        center = size // 2
        painter.drawEllipse(center - 4, center - 4, 8, 8)
        painter.drawEllipse(center - 2, center - 2, 4, 4)

    painter.end()
    return QIcon(pixmap)
