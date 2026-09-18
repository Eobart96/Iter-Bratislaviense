"""
Утилиты для консольного вывода с ANSI-цветами.

Модуль предоставляет функции для цветного вывода текста в консоли,
что улучшает атмосферу игры и визуальное восприятие информации.
"""

from typing import Optional


# ANSI-коды цветов
class Colors:
    """ANSI-коды для цветного вывода в консоли."""
    
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Цвета текста
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Яркие цвета
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    
    # Цвета фона
    BG_BLACK = "\033[40m"
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"


def colorize(text: str, color: str, bold: bool = False) -> str:
    """
    Окрасить текст в указанный цвет.
    
    Args:
        text: Текст для окрашивания.
        color: ANSI-код цвета из класса Colors.
        bold: Сделать текст жирным.
    
    Returns:
        Окрашенный текст с кодами сброса.
    """
    style = Colors.BOLD if bold else ""
    return f"{style}{color}{text}{Colors.RESET}"


def print_header(title: str, subtitle: Optional[str] = None) -> None:
    """
    Вывести заголовок игры.
    
    Args:
        title: Основной заголовок.
        subtitle: Подзаголовок (опционально).
    """
    border = "=" * 60
    print(colorize(border, Colors.BRIGHT_BLUE, bold=True))
    print(colorize(f"  {title}", Colors.BRIGHT_CYAN, bold=True))
    if subtitle:
        print(colorize(f"  {subtitle}", Colors.CYAN))
    print(colorize(border, Colors.BRIGHT_BLUE, bold=True))
    print()


def print_location(name: str, description: str) -> None:
    """
    Вывести информацию о локации.
    
    Args:
        name: Название локации.
        description: Описание локации.
    """
    print(colorize(f"\n📍 {name}", Colors.BRIGHT_YELLOW, bold=True))
    print(colorize(description, Colors.WHITE))
    print("-" * 40)


def print_dialogue(speaker: str, message: str) -> None:
    """
    Вывести диалог с NPC.
    
    Args:
        speaker: Имя говорящего.
        message: Текст сообщения.
    """
    print(colorize(f"\n💬 {speaker}:", Colors.BRIGHT_MAGENTA, bold=True))
    print(colorize(f"   \"{message}\"", Colors.MAGENTA))


def print_quest(title: str, description: str) -> None:
    """
    Вывести информацию о задании.
    
    Args:
        title: Название задания.
        description: Описание задания.
    """
    print(colorize(f"\n📜 ЗАДАНИЕ: {title}", Colors.BRIGHT_GREEN, bold=True))
    print(colorize(description, Colors.GREEN))


def print_success(message: str) -> None:
    """Вывести сообщение об успехе."""
    print(colorize(f"✓ {message}", Colors.BRIGHT_GREEN))


def print_error(message: str) -> None:
    """Вывести сообщение об ошибке."""
    print(colorize(f"✗ {message}", Colors.BRIGHT_RED))


def print_warning(message: str) -> None:
    """Вывести предупреждение."""
    print(colorize(f"⚠ {message}", Colors.BRIGHT_YELLOW))


def print_info(message: str) -> None:
    """Вывести информационное сообщение."""
    print(colorize(f"ℹ {message}", Colors.BRIGHT_CYAN))


def print_separator() -> None:
    """Вывести разделитель."""
    print(colorize("-" * 40, Colors.DIM))


def clear_screen() -> None:
    """Очистить экран консоли."""
    print("\033[2J\033[H", end="")
