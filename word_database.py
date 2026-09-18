"""
База данных слов словацкого языка.

Модуль содержит класс WordDatabase для хранения и управления
словами словацкого языка с переводами и подсказками.
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class WordEntry:
    """
    Структура данных для хранения слова.
    
    Attributes:
        russian: Слово на русском языке.
        slovak: Слово на словацком языке.
        hint: Подсказка к слову.
        category: Категория слова (существительное, глагол и т.д.).
    """
    
    def __init__(self, russian: str, slovak: str, hint: str = "", category: str = "general") -> None:
        self.russian = russian
        self.slovak = slovak
        self.hint = hint
        self.category = category
    
    def to_dict(self) -> Dict[str, str]:
        """Преобразовать запись в словарь."""
        return {
            "russian": self.russian,
            "slovak": self.slovak,
            "hint": self.hint,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "WordEntry":
        """Создать запись из словаря."""
        return cls(
            russian=data.get("russian", ""),
            slovak=data.get("slovak", ""),
            hint=data.get("hint", ""),
            category=data.get("category", "general")
        )


class WordDatabase:
    """
    База данных слов словацкого языка.
    
    Хранит слова с переводами, подсказками и категориями.
    Поддерживает загрузку/сохранение в JSON и поиск слов.
    
    Attributes:
        words: Словарь слов, где ключ - русское слово.
    """
    
    DEFAULT_WORDS: List[Dict[str, str]] = [
        # Приветствия и базовые фразы
        {"russian": "привет", "slovak": "ahoj", "hint": "Неформальное приветствие", "category": "greetings"},
        {"russian": "здравствуйте", "slovak": "dobrý deň", "hint": "Формальное приветствие", "category": "greetings"},
        {"russian": "спасибо", "slovak": "ďakujem", "hint": "Благодарность", "category": "greetings"},
        {"russian": "пожалуйста", "slovak": "prosím", "hint": "Вежливая просьба или ответ на спасибо", "category": "greetings"},
        {"russian": "до свидания", "slovak": "dovidenia", "hint": "Прощание", "category": "greetings"},
        {"russian": "да", "slovak": "áno", "hint": "Утверждение", "category": "basic"},
        {"russian": "нет", "slovak": "nie", "hint": "Отрицание", "category": "basic"},
        
        # Локации
        {"russian": "замок", "slovak": "hrad", "hint": "Братиславский Град", "category": "locations"},
        {"russian": "город", "slovak": "mesto", "hint": "Населённый пункт", "category": "locations"},
        {"russian": "мост", "slovak": "most", "hint": "Переправа через реку", "category": "locations"},
        {"russian": "река", "slovak": "rieka", "hint": "Водный поток", "category": "locations"},
        {"russian": "улица", "slovak": "ulica", "hint": "Дорога в городе", "category": "locations"},
        {"russian": "площадь", "slovak": "námestie", "hint": "Открытое пространство в городе", "category": "locations"},
        
        # Существительные
        {"russian": "друг", "slovak": "priateľ", "hint": "Товарищ", "category": "nouns"},
        {"russian": "вода", "slovak": "voda", "hint": "Жидкость", "category": "nouns"},
        {"russian": "хлеб", "slovak": "chlieb", "hint": "Продукт питания", "category": "nouns"},
        {"russian": "вино", "slovak": "víno", "hint": "Алкогольный напиток", "category": "nouns"},
        {"russian": "день", "slovak": "deň", "hint": "Период суток", "category": "nouns"},
        {"russian": "ночь", "slovak": "noc", "hint": "Тёмное время суток", "category": "nouns"},
        {"russian": "человек", "slovak": "človek", "hint": "Индивид", "category": "nouns"},
        {"russian": "женщина", "slovak": "žena", "hint": "Взрослая особа женского пола", "category": "nouns"},
        {"russian": "мужчина", "slovak": "muž", "hint": "Взрослая особа мужского пола", "category": "nouns"},
        
        # Глаголы
        {"russian": "говорить", "slovak": "hovoriť", "hint": "Произносить слова", "category": "verbs"},
        {"russian": "понимать", "slovak": "rozumieť", "hint": "Осознавать смысл", "category": "verbs"},
        {"russian": "знать", "slovak": "vedieť", "hint": "Иметь информацию", "category": "verbs"},
        {"russian": "хотеть", "slovak": "chcieť", "hint": "Иметь желание", "category": "verbs"},
        {"russian": "идти", "slovak": "ísť", "hint": "Перемещаться пешком", "category": "verbs"},
        {"russian": "видеть", "slovak": "vidieť", "hint": "Воспринимать глазами", "category": "verbs"},
        {"russian": "любить", "slovak": "ľúbiť", "hint": "Испытывать любовь", "category": "verbs"},
        
        # Прилагательные
        {"russian": "красивый", "slovak": "pekný", "hint": "Приятный на вид", "category": "adjectives"},
        {"russian": "большой", "slovak": "veľký", "hint": "Крупного размера", "category": "adjectives"},
        {"russian": "маленький", "slovak": "malý", "hint": "Небольшого размера", "category": "adjectives"},
        {"russian": "старый", "slovak": "starý", "hint": "Давний, не новый", "category": "adjectives"},
        {"russian": "новый", "slovak": "nový", "hint": "Недавно созданный", "category": "adjectives"},
        {"russian": "хороший", "slovak": "dobrý", "hint": "Качественный", "category": "adjectives"},
        {"russian": "плохой", "slovak": "zlý", "hint": "Некачественный", "category": "adjectives"},
    ]
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        """
        Инициализировать базу данных слов.
        
        Args:
            db_path: Путь к файлу JSON с дополнительными словами (опционально).
        """
        self.words: Dict[str, WordEntry] = {}
        self.db_path = Path(db_path) if db_path else None
        
        # Загрузить слова по умолчанию
        for word_data in self.DEFAULT_WORDS:
            entry = WordEntry.from_dict(word_data)
            self.words[entry.russian.lower()] = entry
        
        # Загрузить дополнительные слова из файла
        if self.db_path and self.db_path.exists():
            self._load_from_file()
    
    def _load_from_file(self) -> None:
        """Загрузить слова из JSON файла."""
        if not self.db_path or not self.db_path.exists():
            return
        
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for word_data in data.get("words", []):
                    entry = WordEntry.from_dict(word_data)
                    self.words[entry.russian.lower()] = entry
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load word database: {e}")
    
    def save_to_file(self, path: str) -> None:
        """
        Сохранить все слова в JSON файл.
        
        Args:
            path: Путь к файлу для сохранения.
        """
        data = {
            "words": [entry.to_dict() for entry in self.words.values()]
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_word(self, russian: str) -> Optional[WordEntry]:
        """
        Найти слово по русскому переводу.
        
        Args:
            russian: Русское слово для поиска.
        
        Returns:
            WordEntry если найдено, иначе None.
        """
        return self.words.get(russian.lower())
    
    def get_random_word(self, category: Optional[str] = None) -> Optional[WordEntry]:
        """
        Получить случайное слово из базы.
        
        Args:
            category: Фильтр по категории (опционально).
        
        Returns:
            Случайное слово или None если база пуста.
        """
        import random
        
        if category:
            filtered = [
                w for w in self.words.values() 
                if w.category == category
            ]
        else:
            filtered = list(self.words.values())
        
        if not filtered:
            return None
        
        return random.choice(filtered)
    
    def get_words_by_category(self, category: str) -> List[WordEntry]:
        """
        Получить все слова указанной категории.
        
        Args:
            category: Название категории.
        
        Returns:
            Список слов категории.
        """
        return [w for w in self.words.values() if w.category == category]
    
    def add_word(self, entry: WordEntry) -> None:
        """
        Добавить новое слово в базу.
        
        Args:
            entry: Запись слова для добавления.
        """
        self.words[entry.russian.lower()] = entry
    
    def get_all_categories(self) -> List[str]:
        """
        Получить список всех категорий.
        
        Returns:
            Список уникальных категорий.
        """
        categories = set(w.category for w in self.words.values())
        return sorted(categories)
