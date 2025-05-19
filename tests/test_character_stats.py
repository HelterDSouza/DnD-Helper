import pytest

from src.ability_score import (
    MAX_SCORE,
    Ability,
    AbilityBonus,
    BaseAbilities,
    BonusType,
    CharacterStats,
)


@pytest.fixture
def base_abilities():
    """Create a default BaseAbilities instance."""
    return BaseAbilities(
        strength=14,
        dexterity=12,
        constitution=10,
        wisdom=8,
        intelligence=16,
        charisma=10,
    )


@pytest.fixture
def racial_bonus():
    """Create a default AbilityBonus for racial type."""
    return AbilityBonus(bonus_type=BonusType.RACIAL, strength=2, intelligence=2)


def test_base_abilities_valid_initialization(base_abilities):
    """Test valid initialization of BaseAbilities."""
    assert base_abilities.strength == 14
    assert base_abilities.dexterity == 12
    assert base_abilities.constitution == 10
    assert base_abilities.wisdom == 8
    assert base_abilities.intelligence == 16
    assert base_abilities.charisma == 10


@pytest.mark.parametrize(
    "field, value",
    [
        ("strength", -1),
        ("dexterity", -5),
        ("constitution", "invalid"),
        ("intelligence", 3.5),
    ],
)
def test_base_abilities_invalid_initialization(field, value):
    """Test BaseAbilities raises ValueError for invalid inputs."""
    kwargs = {
        "strength": 10,
        "dexterity": 10,
        "constitution": 10,
        "wisdom": 10,
        "intelligence": 10,
        "charisma": 10,
        field: value,
    }
    with pytest.raises(ValueError):
        BaseAbilities(**kwargs)


def test_ability_bonus_valid_initialization(racial_bonus):
    """Test valid initialization of AbilityBonus."""
    assert racial_bonus.bonus_type == BonusType.RACIAL
    assert racial_bonus.strength == 2
    assert racial_bonus.intelligence == 2
    assert racial_bonus.dexterity == 0  # Default value


def test_ability_bonus_invalid_bonus_type():
    """Test AbilityBonus raises ValueError for invalid bonus_type."""
    with pytest.raises(ValueError):
        AbilityBonus(bonus_type="invalid")


@pytest.mark.parametrize(
    "field, value",
    [
        ("strength", -1),
        ("dexterity", "invalid"),
        ("wisdom", 2.5),
    ],
)
def test_ability_bonus_invalid_values(field, value):
    """Test AbilityBonus raises ValueError for invalid ability values."""
    kwargs = {field: value}
    with pytest.raises(ValueError):
        AbilityBonus(bonus_type=BonusType.RACIAL, **kwargs)


def test_character_stats_initialization(base_abilities, racial_bonus):
    """Test valid initialization of CharacterStats."""
    stats = CharacterStats(base=base_abilities, racial=racial_bonus)
    assert stats.base_abilities == base_abilities
    assert stats.racial_bonus.bonus_type == BonusType.RACIAL
    assert stats.feat_bonus.bonus_type == BonusType.FEAT
    assert stats.level_bonus.bonus_type == BonusType.LEVEL


def test_character_stats_invalid_bonus_type(base_abilities):
    """Test CharacterStats raises ValueError for incorrect bonus types."""
    invalid_racial = AbilityBonus(bonus_type=BonusType.FEAT)
    with pytest.raises(ValueError):
        CharacterStats(base=base_abilities, racial=invalid_racial)


@pytest.mark.parametrize(
    "ability, expected_score",
    [
        (Ability.STRENGTH, 16),  # 14 (base) + 2 (racial)
        (Ability.DEXTERITY, 12),  # 12 (base) + 0 (racial)
        (Ability.INTELLIGENCE, 18),  # 16 (base) + 2 (racial)
        (Ability.CHARISMA, 10),  # 10 (base) + 0 (racial)
    ],
)
def test_total_score(base_abilities, racial_bonus, ability, expected_score):
    """Test total_score calculation."""
    stats = CharacterStats(base=base_abilities, racial=racial_bonus)
    assert stats.total_score(ability) == expected_score


@pytest.mark.parametrize(
    "ability, score, expected_modifier",
    [
        (Ability.STRENGTH, 16, 3),  # (16 - 10) // 2 = 3
        (Ability.DEXTERITY, 12, 1),  # (12 - 10) // 2 = 1
        (Ability.CONSTITUTION, 10, 0),  # (10 - 10) // 2 = 0
        (Ability.WISDOM, 8, -1),  # (8 - 10) // 2 = -1
    ],
)
def test_modifier(base_abilities, ability, score, expected_modifier):
    """Test modifier calculation."""
    stats = CharacterStats(base=base_abilities)
    # Mock the total_score to return the test score
    stats.total_score = lambda x: score if x == ability else 0
    assert stats.modifier(ability) == expected_modifier


def test_add_bonus_valid(base_abilities):
    """Test adding a valid bonus."""
    stats = CharacterStats(base=base_abilities)
    stats.add_bonus(BonusType.FEAT, {Ability.DEXTERITY: 2})
    assert stats.feat_bonus.dexterity == 2
    assert stats.total_score(Ability.DEXTERITY) == 14  # 12 (base) + 2 (feat)


def test_add_bonus_exceeds_max_score(base_abilities):
    """Test add_bonus raises ValueError when exceeding MAX_SCORE."""
    stats = CharacterStats(base=base_abilities)
    with pytest.raises(ValueError):
        stats.add_bonus(BonusType.FEAT, {Ability.STRENGTH: MAX_SCORE})


@pytest.mark.parametrize(
    "increments, error_msg",
    [
        ({Ability.STRENGTH: 0}, "must be a positive integer"),
        ({Ability.STRENGTH: -1}, "must be a positive integer"),
        ({Ability.STRENGTH: "invalid"}, "must be a positive integer"),
    ],
)
def test_add_bonus_invalid_increments(base_abilities, increments, error_msg):
    """Test add_bonus raises ValueError for invalid increments."""
    stats = CharacterStats(base=base_abilities)
    with pytest.raises(ValueError, match=error_msg):
        stats.add_bonus(BonusType.FEAT, increments)


def test_add_bonus_invalid_bonus_type(base_abilities):
    """Test add_bonus raises ValueError for invalid bonus type."""
    stats = CharacterStats(base=base_abilities)
    with pytest.raises(ValueError):
        stats.add_bonus("invalid", {Ability.STRENGTH: 1})
