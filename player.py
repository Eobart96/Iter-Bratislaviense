"""
Модуль игрока.

Содержит класс Player для хранения состояния игрока:
инвентарь, уровень знания языка (XP), энергия, местоположение.
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class Player:
    """
    Класс игрока.
    
    Хранит все характеристики игрока: имя, опыт, энергию,
    инвентарь с выученными словами и текущее местоположение.
    
    Attributes:
        name: Имя игрока.
        xp: Очки опыта (уровень знания языка).
        level: Уровень игрока (вычисляется из XP).
        energy: Текущая энергия (здоровье).
        max_energy: Максимальная энергия.
        inventory: Список выученных слов (словарь).
        current_location_id: ID текущей локации.
        completed_quests: Список завершённых заданий.
    """
    
    def __init__(self, name: str = "Путешественник") -> None:
        """
        Инициализировать нового игрока.
        
        Args:
            name: Имя игрока.
        """
        self.name: str = name
        self.xp: int = 0
        self.energy: int = 100
        self.max_energy: int = 100
        self.inventory: Dict[str, bool] = {}  # слово -> выучено ли
        self.current_location_id: str = "start"
        self.completed_quests: List[str] = []
        self.learned_words: List[str] = []  # Список выученных словацких слов
    
    @property
    def level(self) -> int:
        """
        Вычислить уровень игрока на основе XP.
        
        Returns:
            Уровень игрока (каждые 100 XP = новый уровень).
        """
        return (self.xp // 100) + 1
    
    @property
    def words_count(self) -> int:
        """Количество выученных слов."""
        return len(self.learned_words)
    
    def add_xp(self, amount: int) -> int:
        """
        Добавить опыт игроку.
        
        Args:
            amount: Количество опыта для добавления.
        
        Returns:
            Новый уровень если произошло повышение, иначе 0.
        """
        old_level = self.level
        self.xp += amount
        
        # Проверка на повышение уровня
        if self.level > old_level:
            # Восстановить немного энергии при повышении уровня
            self.energy = min(self.max_energy, self.energy + 20)
            return self.level - old_level
        
        return 0
    
    def lose_energy(self, amount: int) -> None:
        """
        Потерять энергию.
        
        Args:
            amount: Количество энергии для потери.
        """
        self.energy = max(0, self.energy - amount)
    
    def restore_energy(self, amount: int) -> None:
        """
        Восстановить энергию.
        
        Args:
            amount: Количество энергии для восстановления.
        """
        self.energy = min(self.max_energy, self.energy + amount)
    
    def is_alive(self) -> bool:
        """
        Проверить, жив ли игрок (есть ли энергия).
        
        Returns:
            True если энергия > 0.
        """
        return self.energy > 0
    
    def learn_word(self, slovak_word: str, russian_word: str) -> bool:
        """
        Выучить новое слово.
        
        Args:
            slovak_word: Слово на словацком.
            russian_word: Перевод на русский.
        
        Returns:
            True если слово было новым, False если уже известно.
        """
        key = f"{slovak_word}:{russian_word}"
        if key not in self.inventory:
            self.inventory[key] = True
            self.learned_words.append(slovak_word)
            return True
        return False
    
    def knows_word(self, slovak_word: str) -> bool:
        """
        Проверить, знает ли игрок слово.
        
        Args:
            slovak_word: Слово на словацком.
        
        Returns:
            True если слово известно.
        """
        return slovak_word in self.learned_words
    
    def complete_quest(self, quest_id: str) -> bool:
        """
        Отметить задание как выполненное.
        
        Args:
            quest_id: ID задания.
        
        Returns:
            True если задание было новым, False если уже выполнено.
        """
        if quest_id not in self.completed_quests:
            self.completed_quests.append(quest_id)
            return True
        return False
    
    def set_location(self, location_id: str) -> None:
        """
        Установить текущее местоположение.
        
        Args:
            location_id: ID новой локации.
        """
        self.current_location_id = location_id
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать состояние игрока в словарь.
        
        Returns:
            Словарь с данными игрока.
        """
        return {
            "name": self.name,
            "xp": self.xp,
            "energy": self.energy,
            "max_energy": self.max_energy,
            "inventory": self.inventory,
            "learned_words": self.learned_words,
            "current_location_id": self.current_location_id,
            "completed_quests": self.completed_quests
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Player":
        """
        Создать игрока из словаря.
        
        Args:
            data: Словарь с данными игрока.
        
        Returns:
            Новый экземпляр Player.
        """
        player = cls(name=data.get("name", "Путешественник"))
        player.xp = data.get("xp", 0)
        player.energy = data.get("energy", 100)
        player.max_energy = data.get("max_energy", 100)
        player.inventory = data.get("inventory", {})
        player.learned_words = data.get("learned_words", [])
        player.current_location_id = data.get("current_location_id", "start")
        player.completed_quests = data.get("completed_quests", [])
        return player
    
    def save(self, filepath: str) -> None:
        """
        Сохранить состояние игрока в JSON файл.
        
        Args:
            filepath: Путь к файлу сохранения.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> Optional["Player"]:
        """
        Загрузить игрока из JSON файла.
        
        Args:
            filepath: Путь к файлу сохранения.
        
        Returns:
            Player если загрузка успешна, иначе None.
        """
        path = Path(filepath)
        if not path.exists():
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except (json.JSONDecodeError, IOError):
            return None
    
    def __str__(self) -> str:
        """Строковое представление игрока."""
        return (f"Игрок: {self.name} | Уровень: {self.level} | "
                f"XP: {self.xp} | Энергия: {self.energy}/{self.max_energy} | "
                f"Слов: {self.words_count}")
