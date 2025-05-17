import math
from enum import Enum
from typing import List, NamedTuple, Set

from ability_score import Ability, AbilityScores, ComponentScore, RacialBonus, ScoreBase


class CharacterClass(Enum):
    ARTIFICER = 0, 8  # d8
    BARBARIAN = 1, 12  # d12
    BARD = 2, 8  # d8
    CLERIC = 3, 8  # d8
    DRUID = 4, 8  # d8
    FIGHTER = 5, 10  # d10
    MONK = 6, 8  # d8
    PALADIN = 7, 10  # d10
    RANGER = 8, 10  # d10
    ROGUE = 9, 8  # d8
    SORCERER = 10, 6  # d6
    WARLOCK = 11, 8  # d8
    WIZARD = 12, 6  # d6

    @property
    def hit_dice(self) -> int:
        return self.value[1]


class SavingThrowProficiencies:
    def __init__(self):
        self._proficiencies = {
            CharacterClass.ARTIFICER: [Ability.CONSTITUTION, Ability.INTELLIGENCE],
            CharacterClass.BARBARIAN: [Ability.STRENGTH, Ability.CONSTITUTION],
            CharacterClass.BARD: [Ability.DEXTERITY, Ability.CHARISMA],
            CharacterClass.CLERIC: [Ability.WISDOM, Ability.CHARISMA],
            CharacterClass.DRUID: [Ability.INTELLIGENCE, Ability.WISDOM],
            CharacterClass.FIGHTER: [Ability.STRENGTH, Ability.CONSTITUTION],
            CharacterClass.MONK: [Ability.STRENGTH, Ability.DEXTERITY],
            CharacterClass.PALADIN: [Ability.WISDOM, Ability.CHARISMA],
            CharacterClass.RANGER: [Ability.STRENGTH, Ability.DEXTERITY],
            CharacterClass.ROGUE: [Ability.DEXTERITY, Ability.INTELLIGENCE],
            CharacterClass.SORCERER: [Ability.CONSTITUTION, Ability.CHARISMA],
            CharacterClass.WARLOCK: [Ability.WISDOM, Ability.INTELLIGENCE],
            CharacterClass.WIZARD: [Ability.INTELLIGENCE, Ability.WISDOM],
        }

    def get_proficiencies(self, character_class: CharacterClass) -> List[Ability]:
        return self._proficiencies.get(character_class, [])


class Skill(Enum):
    ACROBACIA = 0, "Acrobacia", Ability.DEXTERITY
    ADESTRAR_ANIMAIS = 1, "Adestrar Animais", Ability.WISDOM
    ARCANISMO = 2, "Arcanismo", Ability.INTELLIGENCE
    ATLETISMO = 3, "Atletismo", Ability.STRENGTH
    ENGANACAO = 4, "Enganação", Ability.CHARISMA
    HISTORIA = 5, "História", Ability.INTELLIGENCE
    INTUICAO = 6, "Intuição", Ability.WISDOM
    INTIMIDACAO = 7, "Intimidação", Ability.CHARISMA
    INVESTIGACAO = 8, "Investigação", Ability.INTELLIGENCE
    MEDICINA = 9, "Medicina", Ability.WISDOM
    NATUREZA = 10, "Natureza", Ability.INTELLIGENCE
    PERCEPCAO = 11, "Percepção", Ability.WISDOM
    ATUACAO = 12, "Atuação", Ability.CHARISMA
    PERSUASAO = 13, "Persuasão", Ability.CHARISMA
    RELIGIAO = 14, "Religião", Ability.INTELLIGENCE
    PRESTIDIGITACAO = 15, "Prestidigitação", Ability.DEXTERITY
    FURTIVIDADE = 16, "Furtividade", Ability.DEXTERITY
    SOBREVIVENCIA = 17, "Sobrevivência", Ability.WISDOM

    def __init__(self, id: int, name: str, ability: Ability):
        self._value_ = (id, name, ability)
        self._name = name
        self._ability = ability

    @property
    def name(self) -> str:
        return self._name

    @property
    def ability(self) -> Ability:
        return self._ability


class ClassWithLevel(NamedTuple):
    level: int
    class_: CharacterClass


class Character:
    def __init__(
        self,
        name: str,
        classes: List[ClassWithLevel],
        ability: AbilityScores,
        save_throws: List[Ability] = None,
        skills: List[Skill] = None,
        expertise_skills: Set[Skill] = None,
    ):
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        if not classes or not all(
            isinstance(cl, ClassWithLevel)
            and isinstance(cl.level, int)
            and cl.level > 0
            for cl in classes
        ):
            raise ValueError(
                "Classes must be a non-empty list of ClassLevel with positive levels"
            )
        if not isinstance(ability, AbilityScores):
            raise ValueError("Ability must be a CharacterAbility instance")

        if save_throws and not all(isinstance(s, Ability) for s in save_throws):
            raise ValueError("Save Throw must be a list of Ability instances")
        if skills and not all(isinstance(s, Skill) for s in skills):
            raise ValueError("Skills must be a list of Skill instances")
        if expertise_skills and not all(isinstance(s, Skill) for s in expertise_skills):
            raise ValueError("Expertise skills must be a set of Skill instances")
        if expertise_skills and not skills:
            raise ValueError("Cannot have expertise without proficient skills")
        if expertise_skills and not all(s in skills for s in expertise_skills):
            raise ValueError("Expertise skills must be a subset of proficient skills")

        total_level = sum(cl.level for cl in classes)
        if total_level > 20:
            raise ValueError("Total character level cannot exceed 20")

        self.name = name
        self.classes = classes
        self.ability = ability
        self.save_throws = save_throws or []  # Proficient skills
        self.skills = skills or []  # Proficient skills
        self.expertise_skills = expertise_skills or set()  # Expertise skills

    @property
    def total_level(self) -> int:
        return sum(cl.level for cl in self.classes)

    @property
    def proficiency(self) -> int:
        return math.ceil((self.total_level / 4) + 1)

    def _calc_hp(self, die: int, quantity: int, first_level: bool) -> float:
        die_value = die if first_level else (die / 2) + 1
        return (die_value + self.ability.constitution_mod) * quantity

    @property
    def total_hp(self) -> int:
        total = 0
        first_level = True
        for level, class_ in self.classes:
            total += self._calc_hp(class_.hit_dice, level, first_level)
            first_level = False

        return int(total)

    # FIX: Juntar dados da mesma categoria
    def get_hitdices(self) -> List[str]:
        dices = {}
        for cl in self.classes:
            dices[f"d{cl.class_.hit_dice}"] = (
                dices.get(f"d{cl.class_.hit_dice}", 0) + cl.level
            )
        return [f"{die_count}d{die_value}" for die_value, die_count in dices.items()]

    def get_save_throw_modifier(self, save_throw: Ability) -> int:
        ability_mod = {
            Ability.STRENGTH: self.ability.strength_mod,
            Ability.DEXTERITY: self.ability.dexterity_mod,
            Ability.CONSTITUTION: self.ability.constitution_mod,
            Ability.INTELLIGENCE: self.ability.intelligence_mod,
            Ability.WISDOM: self.ability.wisdom_mod,
            Ability.CHARISMA: self.ability.charisma_mod,
        }[save_throw]
        proficiency_bonus = self.proficiency * (
            1 if save_throw in self.save_throws else 0
        )
        return ability_mod + proficiency_bonus

    def get_skill_modifier(self, skill: Skill) -> int:
        ability_mod = {
            Ability.STRENGTH: self.ability.strength_mod,
            Ability.DEXTERITY: self.ability.dexterity_mod,
            Ability.CONSTITUTION: self.ability.constitution_mod,
            Ability.INTELLIGENCE: self.ability.intelligence_mod,
            Ability.WISDOM: self.ability.wisdom_mod,
            Ability.CHARISMA: self.ability.charisma_mod,
        }[skill.ability]
        proficiency_bonus = self.proficiency * (
            2 if skill in self.expertise_skills else 1 if skill in self.skills else 0
        )
        return ability_mod + proficiency_bonus

    def get_skill_emoji(self, ability: Ability) -> str:
        return {
            Ability.STRENGTH: "💪",
            Ability.DEXTERITY: "🖐",
            Ability.CONSTITUTION: "🛡",
            Ability.INTELLIGENCE: "🧠",
            Ability.WISDOM: "📚",
            Ability.CHARISMA: "🎭",
        }[ability]


class CharacterBuilder:
    def __init__(self):
        self._name: str | None = None
        self._classes: list[ClassWithLevel] = []
        self._ability: AbilityScores | None = None
        self.__first_class_level: bool = True
        self._save_throws: List[Ability] = []
        self._skills: List[Skill] = []
        self._expertise_skills: Set[Skill] = set()

    def with_name(self, name: str) -> "CharacterBuilder":
        if not name or not isinstance(name, str):
            raise ValueError("Name must be a non-empty string")
        self._name = name
        return self

    def add_class(self, level: int, class_: CharacterClass) -> "CharacterBuilder":
        if not isinstance(level, int) or level <= 0:
            raise ValueError("Level must be a positive integer")
        if not isinstance(class_, CharacterClass):
            raise ValueError("Class must be a CharacterClass instance")
        current_total_level = sum(cl.level for cl in self._classes) + level
        if current_total_level > 20:
            raise ValueError("Total character level cannot exceed 20")

        if self.__first_class_level:
            class_proficiencies = SavingThrowProficiencies()
            self._save_throws.extend(class_proficiencies.get_proficiencies(class_))
            self._classes.append(ClassWithLevel(level=1, class_=class_))
            level -= 1
            self.__first_class_level = False
            if level < 1:
                return self

        if level > 0:
            self._classes.append(ClassWithLevel(level=level, class_=class_))
        return self

    def with_ability(self, ability: AbilityScores) -> "CharacterBuilder":
        if not isinstance(ability, AbilityScores):
            raise ValueError("Ability must be a CharacterAbility instance")
        self._ability = ability
        return self

    def add_skill(self, skill: Skill) -> "CharacterBuilder":
        if not isinstance(skill, Skill):
            raise ValueError("Skill must be a Skill instance")
        if skill not in self._skills:
            self._skills.append(skill)
        return self

    def add_expertise(self, skill: Skill) -> "CharacterBuilder":
        if not isinstance(skill, Skill):
            raise ValueError("Skill must be a Skill instance")
        if skill not in self._skills:
            raise ValueError("Cannot add expertise to a non-proficient skill")
        self._expertise_skills.add(skill)
        return self

    def build(self) -> Character:
        if self._name is None:
            raise ValueError("Name must be set")
        if not self._classes:
            raise ValueError("At least one class must be set")
        if self._ability is None:
            raise ValueError("Ability must be set")
        return Character(
            self._name,
            self._classes,
            self._ability,
            self._save_throws,
            self._skills,
            self._expertise_skills,
        )


if __name__ == "__main__":
    base = ScoreBase(16, 13, 15, 12, 8, 10)
    racial = RacialBonus(strength=2, dexterity=1)
    scores = AbilityScores(base, racial)

    builder = CharacterBuilder()

    char = (
        builder.with_name("Silacks Dramalak")
        .with_ability(scores)
        .add_class(4, CharacterClass.BARBARIAN)
        .add_skill(Skill.ATLETISMO)
        .add_skill(Skill.SOBREVIVENCIA)
        .add_skill(Skill.INTIMIDACAO)
        .add_skill(Skill.PERCEPCAO)
        .build()
    )

    char.ability.increment_attribute(
        ComponentScore.LEVEL_BONUS, {Ability.CONSTITUTION: 1, Ability.STRENGTH: 1}
    )

    print(char.name)
    print(char.total_level)
    print(char.proficiency)
    print(char.total_hp)

    for ability in Ability:
        print(char.ability._sum_scores(ability))
    print()
    print("Teste de Resistencia")
    print()
    for ability in Ability:
        emoji = char.get_skill_emoji(ability)
        prof = "*" if ability in char.save_throws else ""
        print(
            f"{emoji}{ability.attr_name}({char.get_save_throw_modifier(ability):+}) {prof}"
        )

    print()
    print("Pericias")
    print()
    for skill in Skill:
        emoji = char.get_skill_emoji(skill.ability)
        skill_mod = char.get_skill_modifier(skill)

        prof = (
            "**"
            if skill in char.expertise_skills
            else ("*" if skill in char.skills else "")
        )
        print(
            f"{emoji} {skill.name} {skill.ability.attr_name[:3]} {skill_mod:+} {prof}"
        )
