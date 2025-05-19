import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Optional

MAX_SCORE: Final = 20


class BonusType(Enum):
    RACIAL = "racial"
    FEAT = "feat"
    LEVEL = "level"


class Ability(Enum):
    STRENGTH = ("Força", "strength")
    DEXTERITY = ("Destreza", "dexterity")
    CONSTITUTION = ("Constituição", "constitution")
    INTELLIGENCE = ("Inteligência", "intelligence")
    WISDOM = ("Sabedora", "wisdom")
    CHARISMA = ("Carisma", "charisma")

    def __init__(self, short_name: str, field_name: str):
        self.short_name = short_name
        self.field_name = field_name


@dataclass
class AbilitySet:
    """A set of ability scores with validation."""

    strength: int = 0
    dexterity: int = 0
    constitution: int = 0
    wisdom: int = 0
    intelligence: int = 0
    charisma: int = 0

    def __post_init__(self):
        """Validate that all ability scores are integers"""
        for ability in Ability:
            value = getattr(self, ability.field_name)
            if not isinstance(value, int):
                raise ValueError(f"{ability.name} must be an integer")
            if value < 0 and not isinstance(self, BaseAbilities):
                raise ValueError(f"{ability.name} cannot be negative for bonuses")


@dataclass
class BaseAbilities(AbilitySet):
    """Base ability scores for a character, requiring non-negative values."""

    def __post_init__(self):
        super().__post_init__()
        for ability in Ability:
            if getattr(self, ability.field_name) < 0:
                raise ValueError(f"Base {ability.name} must be non-negative")


@dataclass
class AbilityBonus(AbilitySet):
    """Bonus applied to ability scores (e.g., racial, feat, or level)."""

    bonus_type: BonusType = BonusType.RACIAL

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.bonus_type, BonusType):
            raise ValueError("Bonus type must be a BonusType enum value")


type RacialBonus = AbilityBonus
type FeatBonus = AbilityBonus
type LevelBonus = AbilityBonus


class CharacterStats:
    def __init__(
        self,
        base: BaseAbilities,
        racial: Optional[RacialBonus] = None,
        feat: Optional[FeatBonus] = None,
        level: Optional[LevelBonus] = None,
    ) -> None:
        self._base_abilities = base
        self._racial_bonus = racial or AbilityBonus(bonus_type=BonusType.RACIAL)
        self._feat_bonus = feat or AbilityBonus(bonus_type=BonusType.FEAT)
        self._level_bonus = level or AbilityBonus(bonus_type=BonusType.LEVEL)

        if self._racial_bonus.bonus_type != BonusType.RACIAL:
            raise ValueError("Racial bonus must have bonus_type=BonusType.RACIAL")
        if self._feat_bonus.bonus_type != BonusType.FEAT:
            raise ValueError("Feat bonus must have bonus_type=BonusType.FEAT")
        if self._level_bonus.bonus_type != BonusType.LEVEL:
            raise ValueError("Level bonus must have bonus_type=BonusType.LEVEL")

        self._score_components = [
            self._base_abilities,
            self._racial_bonus,
            self._feat_bonus,
            self._level_bonus,
        ]

    @property
    def base_abilities(self) -> BaseAbilities:
        return self._base_abilities

    @property
    def racial_bonus(self) -> RacialBonus:
        return self._racial_bonus

    @property
    def feat_bonus(self) -> FeatBonus:
        return self._feat_bonus

    @property
    def level_bonus(self) -> LevelBonus:
        return self._level_bonus

    def total_score(self, ability: Ability) -> int:
        """Calculate the total score for a given ability."""
        return sum(getattr(c, ability.field_name) for c in self._score_components)

    def modifier(self, ability: Ability) -> int:
        """Calculate the modifier for a given ability."""
        return math.floor((self.total_score(ability) - 10) / 2)

    def add_bonus(self, bonus_type: BonusType, increments: dict[Ability, int]) -> None:
        """Add bonuses to ability scores for a specific bonus type."""
        bonus_map: dict[BonusType, AbilityBonus] = {
            BonusType.RACIAL: self._racial_bonus,
            BonusType.FEAT: self._feat_bonus,
            BonusType.LEVEL: self._level_bonus,
        }
        if bonus_type not in bonus_map:
            raise ValueError(f"Invalid bonus type: {bonus_type}")

        target = bonus_map[bonus_type]

        # Validate increments
        for ability, amount in increments.items():
            if not isinstance(amount, int) or amount <= 0:
                raise ValueError(f"Bonus for {ability.name} must be a positive integer")
            new_total = self.total_score(ability) + amount
            if new_total > MAX_SCORE:
                raise ValueError(
                    f"Bonus would cause {ability.name} ({new_total}) to exceed {MAX_SCORE}"
                )

        # Apply increments
        for ability, amount in increments.items():
            current_value = getattr(target, ability.field_name)
            setattr(target, ability.field_name, current_value + amount)
