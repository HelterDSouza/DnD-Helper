import math
from enum import Enum
from typing import Final

MAX_TOTAL: Final = 20


class ComponentScore(Enum):
    RACIAL_BONUS = "racial_bonus"
    FEAT_BONUS = "feat_bonus"
    LEVEL_BONUS = "level_bonus"


class Ability(Enum):
    STRENGTH = ("Força", "strength")
    DEXTERITY = ("Destreza", "dexterity")
    CONSTITUTION = ("Constituição", "constitution")
    INTELLIGENCE = ("Inteligência", "intelligence")
    WISDOM = ("Sabedora", "wisdom")
    CHARISMA = ("Carisma", "charisma")

    def __init__(self, short_name: str, attr_name: str):
        self.short_name = short_name
        self.attr_name = attr_name  # e.g., "strength"


class CharacterAbility:
    def __init__(
        self,
        strength: int,
        dexterity: int,
        constitution: int,
        wisdom: int,
        intelligence: int,
        charisma: int,
    ):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.wisdom = wisdom
        self.intelligence = intelligence
        self.charisma = charisma


class ScoreBase(CharacterAbility):
    def __init__(
        self,
        strength: int,
        dexterity: int,
        constitution: int,
        wisdom: int,
        intelligence: int,
        charisma: int,
    ):
        if not all(
            isinstance(x, int) and x >= 0
            for x in [strength, dexterity, constitution, wisdom, intelligence, charisma]
        ):
            raise ValueError("All attributes must be non-negative integers")
        super().__init__(
            strength, dexterity, constitution, wisdom, intelligence, charisma
        )


class RacialBonus(CharacterAbility):
    def __init__(
        self,
        strength: int = 0,
        dexterity: int = 0,
        constitution: int = 0,
        wisdom: int = 0,
        intelligence: int = 0,
        charisma: int = 0,
    ):
        if not all(
            isinstance(x, int)
            for x in [strength, dexterity, constitution, wisdom, intelligence, charisma]
        ):
            raise ValueError("All racial bonuses must be integers")
        super().__init__(
            strength, dexterity, constitution, wisdom, intelligence, charisma
        )


class FeatBonus(CharacterAbility):
    def __init__(
        self,
        strength: int = 0,
        dexterity: int = 0,
        constitution: int = 0,
        wisdom: int = 0,
        intelligence: int = 0,
        charisma: int = 0,
    ):
        if not all(
            isinstance(x, int)
            for x in [strength, dexterity, constitution, wisdom, intelligence, charisma]
        ):
            raise ValueError("All feat bonuses must be integers")
        super().__init__(
            strength, dexterity, constitution, wisdom, intelligence, charisma
        )


class LevelBonus(CharacterAbility):
    def __init__(
        self,
        strength: int = 0,
        dexterity: int = 0,
        constitution: int = 0,
        wisdom: int = 0,
        intelligence: int = 0,
        charisma: int = 0,
    ):
        if not all(
            isinstance(x, int)
            for x in [strength, dexterity, constitution, wisdom, intelligence, charisma]
        ):
            raise ValueError("All level bonuses must be integers")
        super().__init__(
            strength, dexterity, constitution, wisdom, intelligence, charisma
        )


class AbilityScores:
    def __init__(
        self,
        base: ScoreBase,
        racial: RacialBonus | None = None,
        feat: FeatBonus | None = None,
        level: LevelBonus | None = None,
    ) -> None:
        self._score_base = base
        self._racial_bonus = racial or RacialBonus()
        self._feat_bonus = feat or FeatBonus()
        self._level_bonus = level or LevelBonus()

    @property
    def score_base(self):
        return self._score_base

    @property
    def racial_bonus(self):
        return self._racial_bonus

    @property
    def feat_bonus(self):
        return self._feat_bonus

    @property
    def level_bonus(self):
        return self._level_bonus

    def _sum_scores(self, attribute: Ability) -> int:
        """Sum the specified score across all components."""
        return sum(
            getattr(c, attribute.attr_name)
            for c in [
                self._score_base,
                self._racial_bonus,
                self._feat_bonus,
                self._level_bonus,
            ]
            if isinstance(c, CharacterAbility)
        )

    @property
    def strength_mod(self):
        value = self._sum_scores(Ability.STRENGTH)
        return math.floor((value - 10) / 2)

    @property
    def dexterity_mod(self):
        value = self._sum_scores(Ability.DEXTERITY)
        return math.floor((value - 10) / 2)

    @property
    def constitution_mod(self):
        value = self._sum_scores(Ability.CONSTITUTION)
        return math.floor((value - 10) / 2)

    @property
    def wisdom_mod(self):
        value = self._sum_scores(Ability.WISDOM)
        return math.floor((value - 10) / 2)

    @property
    def intelligence_mod(self):
        value = self._sum_scores(Ability.INTELLIGENCE)
        return math.floor((value - 10) / 2)

    @property
    def charisma_mod(self):
        value = self._sum_scores(Ability.CHARISMA)
        return math.floor((value - 10) / 2)

    def increment_attribute(
        self, component: ComponentScore, increments: dict[Ability, int]
    ):
        component_map = {
            ComponentScore.RACIAL_BONUS: self._racial_bonus,
            ComponentScore.FEAT_BONUS: self._feat_bonus,
            ComponentScore.LEVEL_BONUS: self._level_bonus,
        }
        if component not in component_map or not isinstance(component, ComponentScore):
            raise ValueError(
                f"Invalid component: {component}. Must be one of {list(component_map.keys())}"
            )

        target = component_map[component]

        for ability, amount in increments.items():
            if not isinstance(amount, int):
                raise ValueError(f"Increment for {ability.name} must be an integer")
            if amount <= 0:
                raise ValueError(f"Increment for {ability.name} must be positive")

        for ability, amount in increments.items():
            current_total = self._sum_scores(ability)
            new_total = current_total + amount
            if new_total > MAX_TOTAL:
                raise ValueError(
                    f"Increment would cause {ability.name} ({new_total}) to exceed MAX_ATTRIBUTE ({MAX_TOTAL})"
                )

        for ability, amount in increments.items():
            current_value = getattr(target, ability.attr_name)
            setattr(target, ability.attr_name, current_value + amount)


if __name__ == "__main__":
    base = ScoreBase(16, 13, 15, 12, 8, 10)
    # Add racial bonus (Strength +2, Dexterity +1)
    racial = RacialBonus(strength=2, dexterity=1)
    scores = AbilityScores(base, racial)

    # Print initial state
    print(
        f"Strength total: {scores._sum_scores(Ability.STRENGTH)} (mod: {scores.strength_mod})"
    )
    print(
        f"Dexterity total: {scores._sum_scores(Ability.DEXTERITY)} (mod: {scores.dexterity_mod})"
    )
    print(
        f"Wisdom total: {scores._sum_scores(Ability.WISDOM)} (mod: {scores.wisdom_mod})"
    )

    # Increment racial attribute
    print("\nIncrementing racial: Wisdom +3")
    scores.increment_attribute(
        component=ComponentScore.RACIAL_BONUS, increments={Ability.WISDOM: 3}
    )
    print(
        f"New wisdom total: {scores._sum_scores(Ability.WISDOM)} (mod: {scores.wisdom_mod})"
    )

    # Try to exceed MAX_ATTRIBUTE
    print("\nAttempting to increment feat: Strength +14 (should fail)")
    scores.increment_attribute(
        component=ComponentScore.FEAT_BONUS, increments={Ability.STRENGTH: 2}
    )
