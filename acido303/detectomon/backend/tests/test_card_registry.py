from src.card_registry import CardRegistry


def test_generate_and_reuse():
    reg = CardRegistry()
    card1, reused1 = reg.generate("det-1", "cup", {"x1": 1, "y1": 2, "x2": 3, "y2": 4})
    assert reused1 is False
    assert card1.class_name == "cup"

    card2, reused2 = reg.generate("det-2", "cup", {"x1": 10, "y1": 20, "x2": 30, "y2": 40})
    assert reused2 is True
    assert card2.card_id == card1.card_id
