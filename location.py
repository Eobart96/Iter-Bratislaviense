"""
Модуль локаций.

Содержит класс Location для описания мест в игре,
а также фабрики для создания стандартных локаций Братиславы.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class NPC:
    """
    Неигровой персонаж.
    
    Attributes:
        name: Имя персонажа.
        description: Описание внешности.
        dialogue: Список реплик.
        quest_id: ID связанного задания (если есть).
    """
    name: str
    description: str
    dialogue: List[str] = field(default_factory=list)
    quest_id: Optional[str] = None
    
    def get_random_dialogue(self) -> str:
        """Получить случайную реплику."""
        import random
        if not self.dialogue:
            return "..."
        return random.choice(self.dialogue)


@dataclass
class HiddenItem:
    """
    Скрытый предмет в локации.
    
    Attributes:
        name: Название предмета.
        description: Описание предмета.
        found: Найден ли предмет.
        required_word: Слово для получения предмета.
    """
    name: str
    description: str
    found: bool = False
    required_word: Optional[str] = None


class Location:
    """
    Класс локации.
    
    Содержит описание места, доступные направления,
    скрытые предметы и NPC.
    
    Attributes:
        id: Уникальный идентификатор локации.
        name: Название локации.
        description: Полное описание.
        short_description: Краткое описание.
        connections: Словарь направлений -> ID соседних локаций.
        npcs: Список NPC в локации.
        hidden_items: Список скрытых предметов.
        visited: Посещена ли локация ранее.
    """
    
    def __init__(
        self,
        loc_id: str,
        name: str,
        description: str,
        short_description: str = "",
        connections: Optional[Dict[str, str]] = None,
        npcs: Optional[List[NPC]] = None,
        hidden_items: Optional[List[HiddenItem]] = None
    ) -> None:
        """
        Инициализировать локацию.
        
        Args:
            loc_id: Уникальный идентификатор.
            name: Название локации.
            description: Полное описание.
            short_description: Краткое описание (для повторных посещений).
            connections: Словарь направлений.
            npcs: Список NPC.
            hidden_items: Список скрытых предметов.
        """
        self.id = loc_id
        self.name = name
        self.description = description
        self.short_description = short_description or description
        self.connections = connections or {}
        self.npcs = npcs or []
        self.hidden_items = hidden_items or []
        self.visited = False
    
    def mark_visited(self) -> None:
        """Отметить локацию как посещённую."""
        self.visited = True
    
    def get_description(self) -> str:
        """
        Получить описание локации.
        
        Returns:
            Краткое описание если посещена, иначе полное.
        """
        return self.short_description if self.visited else self.description
    
    def can_go(self, direction: str) -> bool:
        """
        Проверить возможность движения в направлении.
        
        Args:
            direction: Направление (север, юг, восток, запад и т.д.).
        
        Returns:
            True если движение возможно.
        """
        return direction.lower() in self.connections
    
    def get_destination(self, direction: str) -> Optional[str]:
        """
        Получить ID локации назначения.
        
        Args:
            direction: Направление движения.
        
        Returns:
            ID целевой локации или None.
        """
        return self.connections.get(direction.lower())
    
    def get_available_directions(self) -> List[str]:
        """
        Получить список доступных направлений.
        
        Returns:
            Список названий направлений.
        """
        return list(self.connections.keys())
    
    def get_npc(self, name: str) -> Optional[NPC]:
        """
        Найти NPC по имени.
        
        Args:
            name: Имя персонажа.
        
        Returns:
            NPC если найден, иначе None.
        """
        for npc in self.npcs:
            if npc.name.lower() == name.lower():
                return npc
        return None
    
    def find_hidden_item(self, search_word: Optional[str] = None) -> Optional[HiddenItem]:
        """
        Найти скрытый предмет.
        
        Args:
            search_word: Слово-ключ для поиска (опционально).
        
        Returns:
            HiddenItem если найден, иначе None.
        """
        for item in self.hidden_items:
            if not item.found:
                if search_word is None or item.required_word == search_word:
                    return item
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать локацию в словарь для сохранения."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "short_description": self.short_description,
            "connections": self.connections,
            "visited": self.visited,
            "hidden_items": [
                {"name": i.name, "found": i.found} 
                for i in self.hidden_items
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Location":
        """Создать локацию из словаря."""
        loc = cls(
            loc_id=data["id"],
            name=data["name"],
            description=data["description"],
            short_description=data.get("short_description", ""),
            connections=data.get("connections", {})
        )
        loc.visited = data.get("visited", False)
        return loc


def create_bratislava_locations() -> Dict[str, Location]:
    """
    Создать все локации Братиславы.
    
    Returns:
        Словарь всех локаций по ID.
    """
    locations = {}
    
    # Стартовая локация - Вход в город
    locations["start"] = Location(
        loc_id="start",
        name="Вход в Старый город",
        description=(
            "Вы стоите у входа в исторический центр Братиславы. "
            "Вокруг снуют туристы, слышна разноязычная речь. "
            "Перед вами расходятся улицы в разные стороны.\n"
            "На севере виднеется подъём к замку, на востоке - площадь, "
            "на западе - спуск к реке, а на юге - мост через Дунай."
        ),
        short_description="Перекрёсток у входа в Старый город.",
        connections={
            "север": "castle_hill",
            "восток": "old_town_square",
            "запад": "embankment",
            "юг": "snp_bridge"
        },
        npcs=[
            NPC(
                name="Продавец сувениров",
                description="Пожилой мужчина с тележкой, полной магнитов и открыток.",
                dialogue=[
                    "Vitajte! Добро пожаловать в Братиславу!",
                    "Хотите купить магнитик? Только 2 евро!",
                    "Вы изучаете словацкий? Это прекрасный язык!"
                ],
                quest_id="souvenir_quest"
            )
        ]
    )
    
    # Братиславский Град
    locations["castle_hill"] = Location(
        loc_id="castle_hill",
        name="Братиславский Град",
        description=(
            "Вы на холме перед величественным Братиславским Градом. "
            "Красные крыши замка выделяются на фоне неба. "
            "Отсюда открывается потрясающий вид на город и Дунай.\n"
            "Замок выглядит как перевёрнутая кровать - его уникальная форма "
            "известна далеко за пределами Словакии."
        ),
        short_description="Двор Братиславского Града.",
        connections={
            "юг": "start",
            "вход": "castle_interior"
        },
        npcs=[
            NPC(
                name="Стражник",
                description="Мужчина в историческом костюме у ворот замка.",
                dialogue=[
                    "Dobrý deň! Добро пожаловать в Град.",
                    "Замок хранит много тайн словацкой истории.",
                    "Знаете ли вы, что здесь короновали Марию Терезию?"
                ],
                quest_id="castle_history_quest"
            )
        ],
        hidden_items=[
            HiddenItem(
                name="Старинная монета",
                description="Монета времён Австро-Венгрии.",
                required_word="hrad"
            )
        ]
    )
    
    # Внутри замка
    locations["castle_interior"] = Location(
        loc_id="castle_interior",
        name="Внутри Братиславского Града",
        description=(
            "Вы внутри замка. Каменные стены помнят многие века. "
            "Сейчас здесь расположен музей словацкой истории."
        ),
        short_description="Внутренний двор замка.",
        connections={
            "выход": "castle_hill"
        }
    )
    
    # Старый город (площадь)
    locations["old_town_square"] = Location(
        loc_id="old_town_square",
        name="Главная площадь Старого города",
        description=(
            "Вы на главной площади (Hlavné námestie). "
            "В центре возвышается фонтан Максимилиана. "
            "Вокруг красивые старинные здания с аркадами.\n"
            "Здесь всегда много людей: туристы фотографируются, "
            "уличные музыканты играют, кафе заполнены посетителями."
        ),
        short_description="Главная площадь с фонтаном.",
        connections={
            "запад": "start",
            "север": "st_martin_cathedral",
            "восток": "primatial_palace"
        },
        npcs=[
            NPC(
                name="Гид",
                description="Энергичная женщина с флагом тургруппы.",
                dialogue=[
                    "Ahoj! Хотите узнать историю этой площади?",
                    "Этот фонтан был построен в 1572 году.",
                    "Попробуйте перевести 'námestie' - это площадь!"
                ],
                quest_id="square_translation_quest"
            )
        ]
    )
    
    # Собор Святого Мартина
    locations["st_martin_cathedral"] = Location(
        loc_id="st_martin_cathedral",
        name="Собор Святого Мартина",
        description=(
            "Готический собор XIII века, где короновали 11 венгерских королей. "
            "Высокая башня с золотой короной видна из многих точек города."
        ),
        short_description="Готический собор с высокой башней.",
        connections={
            "юг": "old_town_square"
        }
    )
    
    # Примациальный дворец
    locations["primatial_palace"] = Location(
        loc_id="primatial_palace",
        name="Примациальный дворец",
        description=(
            "Классицистический дворец XVIII века. "
            "Здесь был подписан Пресбургский мир в 1805 году."
        ),
        short_description="Дворец с зеркальным залом.",
        connections={
            "запад": "old_town_square"
        }
    )
    
    # Дунайская набережная
    locations["embankment"] = Location(
        loc_id="embankment",
        name="Дунайская набережная",
        description=(
            "Вы на берегу Дуная. Река спокойно течёт, разделяя город на две части. "
            "На другом берегу виден современный район Петржалка.\n"
            "Недалеко стоит знаменитая статуя 'Чумил' - водопроводчик, "
            "выглядывающий из люка."
        ),
        short_description="Набережная Дуная.",
        connections={
            "восток": "start",
            "юг": "uroborec"
        },
        npcs=[
            NPC(
                name="Рыбак",
                description="Мужчина с удочкой у воды.",
                dialogue=[
                    "Ticho... Рыба клюёт только в тишине.",
                    "Дунай - прекрасная река, знает много историй.",
                    "Слово 'rieka' означает река. Запомните!"
                ],
                quest_id="river_quest"
            )
        ]
    )
    
    # Статуя Чумила
    locations["uroborec"] = Location(
        loc_id="uroborec",
        name="Статуя Чумила",
        description=(
            "Знаменитая бронзовая статуя водопроводчика, "
            "выглядывающего из канализационного люка. "
            "Одна из самых фотографируемых достопримечательностей."
        ),
        short_description="Бронзовый водопроводчик в люке.",
        connections={
            "север": "embankment"
        }
    )
    
    # Мост SNP
    locations["snp_bridge"] = Location(
        loc_id="snp_bridge",
        name="Мост SNP (Новый мост)",
        description=(
            "Стальной мост через Дунай с уникальной башней-рестораном 'UFO'. "
            "С вершины башни (80 метров) открывается панорамный вид.\n"
            "SNP расшифровывается как Slovenské národné povstanie - "
            "Словацкое национальное восстание."
        ),
        short_description="Мост с башней UFO.",
        connections={
            "север": "start",
            "юг": "petrzalka"
        },
        npcs=[
            NPC(
                name="Турист",
                description="Человек с камерой и картой.",
                dialogue=[
                    "Wow! Этот мост невероятный!",
                    "Вы были в ресторане наверху? Виды потрясающие!",
                    "Как будет 'мост' по-словацки? Подсказка: most!"
                ],
                quest_id="bridge_quest"
            )
        ]
    )
    
    # Петржалка
    locations["petrzalka"] = Location(
        loc_id="petrzalka",
        name="Петржалка",
        description=(
            "Современный жилой район на правом берегу Дуная. "
            "Много панельных домов, парков и торговых центров."
        ),
        short_description="Современный район за Дунаем.",
        connections={
            "север": "snp_bridge"
        }
    )
    
    return locations
