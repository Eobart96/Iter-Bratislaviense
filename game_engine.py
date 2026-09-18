"""
Игровой движок.

Содержит класс GameEngine для управления основным циклом игры,
обработкой ввода и сохранением состояния.
"""

import json
from typing import Dict, List, Optional, Any

from player import Player
from location import Location, create_bratislava_locations
from quest import QuestManager, Quest, QuestType
from word_database import WordDatabase, WordEntry
from utils import (
    print_header, print_location, print_dialogue, print_quest,
    print_success, print_error, print_warning, print_info,
    print_separator, clear_screen, colorize, Colors
)


class GameEngine:
    """
    Основной игровой движок.
    
    Управляет игровым циклом, обработкой ввода,
    навигацией между локациями, системой заданий и сохранением.
    
    Attributes:
        player: Объект игрока.
        locations: Словарь всех локаций.
        quest_manager: Менеджер заданий.
        word_db: База данных слов.
        save_path: Путь к файлу сохранения.
        running: Флаг работы игрового цикла.
    """
    
    SAVE_FILE = "save.json"
    
    def __init__(self) -> None:
        """Инициализировать игровой движок."""
        self.player: Optional[Player] = None
        self.locations: Dict[str, Location] = {}
        self.quest_manager = QuestManager()
        self.word_db = WordDatabase()
        self.save_path = self.SAVE_FILE
        self.running = False
        self.current_quest: Optional[Quest] = None
    
    def new_game(self, player_name: str) -> None:
        """
        Начать новую игру.
        
        Args:
            player_name: Имя нового игрока.
        """
        self.player = Player(name=player_name)
        self.locations = create_bratislava_locations()
        self.quest_manager = QuestManager()
        self.running = True
        
        # Установить стартовую локацию
        if "start" in self.locations:
            self.player.set_location("start")
            self.locations["start"].mark_visited()
    
    def load_game(self) -> bool:
        """
        Загрузить сохранённую игру.
        
        Returns:
            True если загрузка успешна.
        """
        player = Player.load(self.save_path)
        if not player:
            return False
        
        self.player = player
        self.locations = create_bratislava_locations()
        self.quest_manager = QuestManager()
        
        # Загрузить состояние квестов
        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "quests" in data:
                    self.quest_manager.from_dict(data["quests"])
        except (json.JSONDecodeError, IOError):
            pass
        
        # Отметить посещённые локации
        current_loc_id = self.player.current_location_id
        if current_loc_id in self.locations:
            self.locations[current_loc_id].mark_visited()
        
        self.running = True
        return True
    
    def save_game(self) -> bool:
        """
        Сохранить текущую игру.
        
        Returns:
            True если сохранение успешно.
        """
        if not self.player:
            return False
        
        try:
            # Сохранить данные игрока
            save_data = self.player.to_dict()
            save_data["quests"] = self.quest_manager.to_dict()
            
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except IOError as e:
            print_error(f"Ошибка сохранения: {e}")
            return False
    
    def get_current_location(self) -> Optional[Location]:
        """Получить текущую локацию."""
        if not self.player:
            return None
        return self.locations.get(self.player.current_location_id)
    
    def move_player(self, direction: str) -> bool:
        """
        Переместить игрока в направлении.
        
        Args:
            direction: Направление движения.
        
        Returns:
            True если перемещение успешно.
        """
        location = self.get_current_location()
        if not location:
            return False
        
        if not location.can_go(direction):
            print_warning(f"Нельзя идти на {direction}.")
            return False
        
        dest_id = location.get_destination(direction)
        if dest_id and dest_id in self.locations:
            self.player.set_location(dest_id)
            self.locations[dest_id].mark_visited()
            return True
        
        return False
    
    def talk_to_npc(self, npc_name: str) -> Optional[Quest]:
        """
        Поговорить с NPC.
        
        Args:
            npc_name: Имя персонажа.
        
        Returns:
            Quest если есть доступное задание.
        """
        location = self.get_current_location()
        if not location:
            return None
        
        npc = location.get_npc(npc_name)
        if not npc:
            print_warning(f"Здесь нет персонажа '{npc_name}'.")
            return None
        
        # Показать диалог
        print_dialogue(npc.name, npc.get_random_dialogue())
        
        # Проверить наличие задания
        if npc.quest_id:
            quest = self.quest_manager.get_quest(npc.quest_id)
            if quest and not quest.completed:
                print_quest(quest.title, quest.description)
                self.current_quest = quest
                return quest
            elif quest and quest.completed:
                print_info(f"{npc.name}: 'Вы уже помогли мне, спасибо!'")
        
        return None
    
    def start_quest(self, quest: Quest) -> None:
        """
        Начать выполнение задания.
        
        Args:
            quest: Задание для выполнения.
        """
        self.current_quest = quest
        print_quest(quest.title, quest.description)
        print(colorize(quest.get_question_with_hint(), Colors.YELLOW))
    
    def submit_quest_answer(self, answer: str) -> bool:
        """
        Отправить ответ на задание.
        
        Args:
            answer: Ответ игрока.
        
        Returns:
            True если ответ правильный.
        """
        if not self.current_quest or not self.player:
            return False
        
        quest = self.current_quest
        
        if quest.check_answer(answer):
            # Правильный ответ
            self._complete_quest(quest)
            return True
        else:
            # Неправильный ответ
            print_error("Неправильно! Попробуйте ещё раз.")
            self.player.lose_energy(5)
            print_warning(f"Вы потеряли 5 энергии. Осталось: {self.player.energy}")
            return False
    
    def _complete_quest(self, quest: Quest) -> None:
        """
        Завершить задание и выдать награду.
        
        Args:
            quest: Выполненное задание.
        """
        if not self.player:
            return
        
        quest.completed = True
        self.quest_manager.mark_completed(quest.id)
        self.player.complete_quest(quest.id)
        
        # Выдать награду
        reward = quest.reward
        levels_gained = self.player.add_xp(reward.xp)
        self.player.restore_energy(reward.energy)
        
        # Добавить слово в инвентарь
        if reward.word:
            for slovak, russian in reward.word.items():
                self.player.learn_word(slovak, russian)
                # Также добавить в базу данных если нет
                if not self.word_db.get_word(russian):
                    self.word_db.add_word(WordEntry(russian, slovak, "", "learned"))
        
        print_success(f"Задание '{quest.title}' выполнено!")
        print_info(f"+{reward.xp} XP, +{reward.energy} энергии")
        
        if levels_gained > 0:
            print(colorize(f"🎉 Уровень повышен! Теперь вы уровень {self.player.level}", 
                          Colors.BRIGHT_GREEN, bold=True))
        
        if reward.word:
            for slovak, russian in reward.word.items():
                print_info(f"📚 Выучено слово: {slovak} = {russian}")
        
        self.current_quest = None
    
    def search_location(self) -> None:
        """Поискать предметы в текущей локации."""
        location = self.get_current_location()
        if not location or not self.player:
            return
        
        # Поиск скрытых предметов
        found_items = []
        for item in location.hidden_items:
            if not item.found:
                # Шанс найти предмет или требование знать слово
                if item.required_word is None or self.player.knows_word(item.required_word):
                    item.found = True
                    found_items.append(item)
        
        if found_items:
            print_success("Вы нашли скрытые предметы:")
            for item in found_items:
                print_info(f"  🎁 {item.name}: {item.description}")
                # Дать немного XP за находку
                self.player.add_xp(5)
        else:
            print_info("Здесь ничего особенного не найдено.")
    
    def show_inventory(self) -> None:
        """Показать инвентарь игрока."""
        if not self.player:
            return
        
        print_separator()
        print(colorize("📦 ИНВЕНТАРЬ (выученные слова):", Colors.BRIGHT_CYAN, bold=True))
        
        if not self.player.learned_words:
            print("Пока пусто. Выполняйте задания чтобы учить слова!")
        else:
            for word in self.player.learned_words:
                entry = self.word_db.get_word_by_slovak(word) if hasattr(self.word_db, 'get_word_by_slovak') else None
                if entry:
                    print(f"  📖 {word} - {entry.russian}")
                else:
                    # Найти в базе по словацкому слову
                    found = False
                    for rus, slov_entry in self.word_db.words.items():
                        if slov_entry.slovak == word:
                            print(f"  📖 {word} - {rus}")
                            found = True
                            break
                    if not found:
                        print(f"  📖 {word}")
        
        print_separator()
    
    def show_status(self) -> None:
        """Показать статус игрока."""
        if not self.player:
            return
        
        print_separator()
        print(colorize("👤 СОСТОЯНИЕ ИГРОКА:", Colors.BRIGHT_BLUE, bold=True))
        print(f"  Имя: {self.player.name}")
        print(f"  Уровень: {self.player.level}")
        print(f"  XP: {self.player.xp}")
        print(f"  Энергия: {self.player.energy}/{self.player.max_energy}")
        print(f"  Слов выучено: {self.player.words_count}")
        print(f"  Заданий выполнено: {len(self.player.completed_quests)}")
        print(f"  Локация: {self.get_current_location().name if self.get_current_location() else '???'}")
        print_separator()
    
    def show_help(self) -> None:
        """Показать справку по командам."""
        print_separator()
        print(colorize("📖 СПРАВКА ПО КОМАНДАМ:", Colors.BRIGHT_YELLOW, bold=True))
        print("""
  Движение:
    север, юг, восток, запад - идти в направлении
    осмотр - описание локации
    
  Взаимодействие:
    говорить [имя] - поговорить с NPC
    ответить [текст] - ответить на вопрос задания
    искать - поискать предметы
    
  Задания:
    задания - список доступных заданий
    начать [номер] - начать задание
    
  Инвентарь и статус:
    инвентарь - показать выученные слова
    статус - показать характеристики
    
  Система:
    сохранить - сохранить игру
    загрузить - загрузить игру
    помощь - эта справка
    выход - выйти из игры
        """)
        print_separator()
    
    def list_quests(self) -> None:
        """Показать список доступных заданий."""
        if not self.player:
            return
        
        location = self.get_current_location()
        loc_id = location.id if location else None
        
        available = self.quest_manager.get_available_quests(loc_id or "")
        
        print_separator()
        print(colorize("📜 ДОСТУПНЫЕ ЗАДАНИЯ:", Colors.BRIGHT_GREEN, bold=True))
        
        if not available:
            print("Нет доступных заданий в этой локации.")
            print("Попробуйте поговорить с NPC или перейти в другое место.")
        else:
            for i, quest in enumerate(available, 1):
                status = "✓" if quest.completed else "○"
                print(f"  {i}. [{status}] {quest.title}")
                print(f"     {quest.description[:50]}...")
        
        print_separator()
    
    def handle_input(self, command: str) -> bool:
        """
        Обработать команду игрока.
        
        Args:
            command: Введённая команда.
        
        Returns:
            False если игра должна завершиться.
        """
        if not self.player:
            return False
        
        parts = command.strip().lower().split(maxsplit=1)
        cmd = parts[0] if parts else ""
        arg = parts[1] if len(parts) > 1 else ""
        
        # Команды движения
        directions = ["север", "юг", "восток", "запад", "вход", "выход"]
        if cmd in directions:
            if self.move_player(cmd):
                self.display_location()
            return True
        
        # Осмотр локации
        if cmd == "осмотр":
            self.display_location()
            return True
        
        # Говорить с NPC
        if cmd == "говорить":
            if arg:
                self.talk_to_npc(arg)
            else:
                # Показать доступных NPC
                location = self.get_current_location()
                if location and location.npcs:
                    print("Здесь можно поговорить с:")
                    for npc in location.npcs:
                        print(f"  - {npc.name}")
                else:
                    print("Здесь не с кем поговорить.")
            return True
        
        # Ответ на задание
        if cmd == "ответить":
            if self.current_quest:
                self.submit_quest_answer(arg)
            else:
                print_warning("Сейчас нет активного задания.")
            return True
        
        # Поиск
        if cmd == "искать":
            self.search_location()
            return True
        
        # Задания
        if cmd == "задания":
            self.list_quests()
            return True
        
        if cmd == "начать" and arg.isdigit():
            idx = int(arg) - 1
            location = self.get_current_location()
            loc_id = location.id if location else ""
            available = self.quest_manager.get_available_quests(loc_id)
            if 0 <= idx < len(available):
                self.start_quest(available[idx])
            else:
                print_warning("Неверный номер задания.")
            return True
        
        # Инвентарь
        if cmd == "инвентарь":
            self.show_inventory()
            return True
        
        # Статус
        if cmd == "статус":
            self.show_status()
            return True
        
        # Помощь
        if cmd == "помощь" or cmd == "help":
            self.show_help()
            return True
        
        # Сохранить
        if cmd == "сохранить":
            if self.save_game():
                print_success("Игра сохранена!")
            return True
        
        # Загрузить
        if cmd == "загрузить":
            if self.load_game():
                print_success("Игра загружена!")
                self.display_location()
            else:
                print_error("Нет файла сохранения.")
            return True
        
        # Выход
        if cmd == "выход" or cmd == "quit":
            print_info("Сохранение перед выходом...")
            self.save_game()
            print("Спасибо за игру! До свидания! / Dovidenia!")
            return False
        
        # Неизвестная команда
        print_warning(f"Неизвестная команда: {cmd}")
        print("Введите 'помощь' для списка команд.")
        return True
    
    def display_location(self) -> None:
        """Отобразить текущую локацию."""
        location = self.get_current_location()
        if not location:
            return
        
        print_location(location.name, location.get_description())
        
        # Показать доступные направления
        directions = location.get_available_directions()
        if directions:
            dir_str = ", ".join(directions)
            print(colorize(f"→ Доступные направления: {dir_str}", Colors.CYAN))
        
        # Показать NPC
        if location.npcs:
            npc_names = ", ".join(npc.name for npc in location.npcs)
            print(colorize(f"💬 Здесь находятся: {npc_names}", Colors.MAGENTA))
    
    def run(self) -> None:
        """Запустить основной игровой цикл."""
        print_header("ITER BRATISLAVIENSE", "Путешествие по Братиславе с изучением словацкого языка")
        
        # Проверка сохранения
        import os
        if os.path.exists(self.save_path):
            print_info("Найдено сохранение.")
            choice = input("Загрузить последнюю игру? (да/нет): ").strip().lower()
            if choice in ["да", "д", "yes", "y"]:
                if self.load_game():
                    print_success(f"Добро пожаловать обратно, {self.player.name}!")
                    self.display_location()
                else:
                    self._start_new_game()
            else:
                self._start_new_game()
        else:
            self._start_new_game()
        
        # Игровой цикл
        while self.running and self.player and self.player.is_alive():
            try:
                command = input("\n> ").strip()
                if not command:
                    continue
                
                self.running = self.handle_input(command)
                
            except KeyboardInterrupt:
                print("\n")
                print_warning("Игра прервана. Сохранение...")
                self.save_game()
                break
            except EOFError:
                break
        
        # Конец игры
        if self.player and not self.player.is_alive():
            print_error("Ваша энергия иссякла! Игра окончена.")
            print_info("Но вы продолжили изучение словацкого языка!")
        
        print("\nĎakujem za hru! Спасибо за игру!")
    
    def _start_new_game(self) -> None:
        """Запросить имя и начать новую игру."""
        print("\nДобро пожаловать в Iter Bratislaviense!")
        print("Вы отправляетесь в виртуальное путешествие по Братиславе,")
        print("изучая словацкий язык через квесты и общение с местными.")
        print_separator()
        
        name = input("Введите ваше имя: ").strip() or "Путешественник"
        self.new_game(name)
        
        print_success(f"Добро пожаловать, {self.player.name}!")
        print_info("Ваше путешествие начинается у входа в Старый город.")
        print_separator()
        print("Подсказка: введите 'помощь' для списка команд.")
        print_separator()
        
        self.display_location()
        
        # Показать первое задание
        location = self.get_current_location()
        if location and location.npcs:
            print_info("\nКажется, здесь кто-то хочет с вами поговорить...")
            print("Попробуйте 'говорить [имя персонажа]'")
