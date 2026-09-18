"""
Модуль заданий (квестов).

Содержит класс Quest для логики заданий на перевод слов
и выбор правильных грамматических окончаний.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class QuestType(Enum):
    """Типы заданий."""
    TRANSLATION = "translation"  # Перевод слова
    GRAMMAR = "grammar"  # Выбор окончания
    FIND_WORD = "find_word"  # Найти слово в локации


@dataclass
class QuestReward:
    """
    Награда за выполнение задания.
    
    Attributes:
        xp: Очки опыта.
        energy: Восстановление энергии.
        word: Новое слово для изучения (словарь {slovak: russian}).
    """
    xp: int = 0
    energy: int = 0
    word: Optional[Dict[str, str]] = None


@dataclass
class Quest:
    """
    Класс задания.
    
    Содержит всю информацию о задании: условие, проверку, награду.
    
    Attributes:
        id: Уникальный идентификатор задания.
        title: Название задания.
        description: Описание условия.
        quest_type: Тип задания.
        question: Вопрос игроку.
        correct_answer: Правильный ответ (или список вариантов).
        hint: Подсказка.
        reward: Награда за выполнение.
        completed: Выполнено ли задание.
        location_id: ID локации где доступно.
    """
    id: str
    title: str
    description: str
    quest_type: QuestType = QuestType.TRANSLATION
    question: str = ""
    correct_answer: str = ""
    hint: str = ""
    reward: QuestReward = field(default_factory=QuestReward)
    completed: bool = False
    location_id: Optional[str] = None
    
    def check_answer(self, player_answer: str) -> bool:
        """
        Проверить ответ игрока.
        
        Args:
            player_answer: Ответ игрока.
        
        Returns:
            True если ответ правильный.
        """
        if not player_answer:
            return False
        
        # Нормализация ответа
        player_answer = player_answer.strip().lower()
        correct = self.correct_answer.lower()
        
        # Для заданий с несколькими вариантами
        if isinstance(self.correct_answer, list):
            return player_answer in [a.lower() for a in self.correct_answer]
        
        return player_answer == correct
    
    def get_question_with_hint(self) -> str:
        """Получить вопрос с подсказкой."""
        if self.hint:
            return f"{self.question}\n💡 Подсказка: {self.hint}"
        return self.question


class QuestManager:
    """
    Менеджер заданий.
    
    Управляет созданием, хранением и проверкой квестов.
    """
    
    def __init__(self) -> None:
        """Инициализировать менеджер заданий."""
        self.quests: Dict[str, Quest] = {}
        self._create_default_quests()
    
    def _create_default_quests(self) -> None:
        """Создать стандартные задания для игры."""
        
        # Задание от продавца сувениров
        self.quests["souvenir_quest"] = Quest(
            id="souvenir_quest",
            title="Первое слово",
            description="Продавец сувениров просит перевести простое приветствие.",
            quest_type=QuestType.TRANSLATION,
            question="Как будет 'привет' по-словацки?",
            correct_answer="ahoj",
            hint="Начинается на 'a'",
            reward=QuestReward(xp=10, energy=5, word={"ahoj": "привет"}),
            location_id="start"
        )
        
        # Задание от стражника замка
        self.quests["castle_history_quest"] = Quest(
            id="castle_history_quest",
            title="Название замка",
            description="Стражник спрашивает название замка на словацком.",
            quest_type=QuestType.TRANSLATION,
            question="Как будет 'замок' по-словацки?",
            correct_answer="hrad",
            hint="Четыре буквы, заканчивается на 'd'",
            reward=QuestReward(xp=15, energy=5, word={"hrad": "замок"}),
            location_id="castle_hill"
        )
        
        # Задание от гида на площади
        self.quests["square_translation_quest"] = Quest(
            id="square_translation_quest",
            title="Площадь",
            description="Гид просит перевести слово 'площадь'.",
            quest_type=QuestType.TRANSLATION,
            question="Как будет 'площадь' по-словацки?",
            correct_answer="námestie",
            hint="Длинное слово с диакритикой",
            reward=QuestReward(xp=20, energy=5, word={"námestie": "площадь"}),
            location_id="old_town_square"
        )
        
        # Задание от рыбака
        self.quests["river_quest"] = Quest(
            id="river_quest",
            title="Река",
            description="Рыбак хочет проверить знание слова 'река'.",
            quest_type=QuestType.TRANSLATION,
            question="Как будет 'река' по-словацки?",
            correct_answer="rieka",
            hint="Похоже на русское слово",
            reward=QuestReward(xp=15, energy=5, word={"rieka": "река"}),
            location_id="embankment"
        )
        
        # Задание от туриста на мосту
        self.quests["bridge_quest"] = Quest(
            id="bridge_quest",
            title="Мост",
            description="Турист интересуется, знаете ли вы слово 'мост'.",
            quest_type=QuestType.TRANSLATION,
            question="Как будет 'мост' по-словацки?",
            correct_answer="most",
            hint="Короткое слово из 4 букв",
            reward=QuestReward(xp=15, energy=5, word={"most": "мост"}),
            location_id="snp_bridge"
        )
        
        # Грамматическое задание - окончания
        self.quests["grammar_adjective_quest"] = Quest(
            id="grammar_adjective_quest",
            title="Прилагательные",
            description="Выберите правильное окончание прилагательного.",
            quest_type=QuestType.GRAMMAR,
            question="Какое окончание у прилагательного 'pekn...' (красивый)?",
            correct_answer="ý",
            hint="Мужской род, единственное число",
            reward=QuestReward(xp=25, energy=10),
            location_id="old_town_square"
        )
        
        # Задание на поиск слова
        self.quests["find_water_quest"] = Quest(
            id="find_water_quest",
            title="Вода",
            description="Найдите в инвентаре слово 'вода' на словацком.",
            quest_type=QuestType.FIND_WORD,
            question="Какой предмет означает 'вода'?",
            correct_answer="voda",
            hint="Простое слово, похоже на русское",
            reward=QuestReward(xp=10, energy=5),
            location_id="embankment"
        )
        
        # Дополнительные задания
        self.quests["thank_you_quest"] = Quest(
            id="thank_you_quest",
            title="Благодарность",
            description="Научитесь благодарить по-словацки.",
            quest_type=QuestType.TRANSLATION,
            question="Как будет 'спасибо' по-словацки?",
            correct_answer="ďakujem",
            hint="Начинается с 'ď'",
            reward=QuestReward(xp=15, energy=5, word={"ďakujem": "спасибо"}),
            location_id="start"
        )
        
        self.quests["good_day_quest"] = Quest(
            id="good_day_quest",
            title="Формальное приветствие",
            description="Выучите формальное приветствие.",
            quest_type=QuestType.TRANSLATION,
            question="Как сказать 'здравствуйте' (букв. 'хороший день')?",
            correct_answer="dobrý deň",
            hint="Два слова, первое заканчивается на 'ý'",
            reward=QuestReward(xp=20, energy=5, word={"dobrý deň": "здравствуйте"}),
            location_id="castle_hill"
        )
        
        self.quests["friend_quest"] = Quest(
            id="friend_quest",
            title="Друг",
            description="Как будет 'друг' по-словацки?",
            quest_type=QuestType.TRANSLATION,
            question="Переведите слово 'друг'",
            correct_answer="priateľ",
            hint="Звучит похоже на польское 'przyjaciel'",
            reward=QuestReward(xp=15, energy=5, word={"priateľ": "друг"}),
            location_id="old_town_square"
        )
        
        self.quests["wine_quest"] = Quest(
            id="wine_quest",
            title="Словацкое вино",
            description="Словакия известна винами. Выучите слово!",
            quest_type=QuestType.TRANSLATION,
            question="Как будет 'вино' по-словацки?",
            correct_answer="víno",
            hint="С диакритикой на первой букве",
            reward=QuestReward(xp=15, energy=5, word={"víno": "вино"}),
            location_id="castle_hill"
        )
        
        self.quests["go_quest"] = Quest(
            id="go_quest",
            title="Движение",
            description="Глагол движения.",
            quest_type=QuestType.TRANSLATION,
            question="Как будет 'идти' по-словацки?",
            correct_answer="ísť",
            hint="Инфинитив с диакритикой",
            reward=QuestReward(xp=20, energy=5, word={"ísť": "идти"}),
            location_id="snp_bridge"
        )
        
        self.quests["beautiful_quest"] = Quest(
            id="beautiful_quest",
            title="Красивый город",
            description="Опишите Братиславу.",
            quest_type=QuestType.TRANSLATION,
            question="Как сказать 'красивый' (о мужчине/объекте)?",
            correct_answer="pekný",
            hint="Заканчивается на 'ý'",
            reward=QuestReward(xp=20, energy=5, word={"pekný": "красивый"}),
            location_id="old_town_square"
        )
        
        self.quests["yes_no_quest"] = Quest(
            id="yes_no_quest",
            title="Утверждение и отрицание",
            description="Базовые слова.",
            quest_type=QuestType.GRAMMAR,
            question="Какое слово означает 'да'?",
            correct_answer="áno",
            hint="Три буквы с диакритикой",
            reward=QuestReward(xp=10, energy=5, word={"áno": "да"}),
            location_id="start"
        )
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """
        Получить задание по ID.
        
        Args:
            quest_id: Идентификатор задания.
        
        Returns:
            Quest если найден, иначе None.
        """
        return self.quests.get(quest_id)
    
    def get_available_quests(self, location_id: str) -> List[Quest]:
        """
        Получить доступные задания для локации.
        
        Args:
            location_id: ID текущей локации.
        
        Returns:
            Список незавершённых заданий локации.
        """
        available = []
        for quest in self.quests.values():
            if not quest.completed:
                if quest.location_id is None or quest.location_id == location_id:
                    available.append(quest)
        return available
    
    def get_all_quests(self) -> List[Quest]:
        """Получить все задания."""
        return list(self.quests.values())
    
    def mark_completed(self, quest_id: str) -> None:
        """
        Отметить задание как выполненное.
        
        Args:
            quest_id: ID задания.
        """
        if quest_id in self.quests:
            self.quests[quest_id].completed = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для сохранения."""
        return {
            qid: {
                "completed": quest.completed
            }
            for qid, quest in self.quests.items()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Загрузить состояние из словаря.
        
        Args:
            data: Словарь с состоянием заданий.
        """
        for quest_id, state in data.items():
            if quest_id in self.quests:
                self.quests[quest_id].completed = state.get("completed", False)
