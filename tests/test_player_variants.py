from renardo.lib.Player.player_variants import split_variant_kwargs


def test_no_variant_kwargs_is_a_noop():
    degree, kwargs = [0, 2, 4, 5], {"dur": .25, "oct": 5}
    base_degree, base_kwargs, variants = split_variant_kwargs(degree, kwargs)

    assert base_degree is degree
    assert base_kwargs is kwargs
    assert variants == {}


def test_single_param_single_variant():
    base_degree, base_kwargs, variants = split_variant_kwargs(
        [0, 2, 4, 5], {"dur": .25, "oct": 5, "oct_2": 6}
    )

    assert base_kwargs == {"dur": .25, "oct": 5}
    assert variants == {2: (None, {"oct": 6})}


def test_several_params_grouped_on_the_same_variant():
    base_degree, base_kwargs, variants = split_variant_kwargs(
        [0, 2, 4, 5], {"dur": .25, "oct": 5, "oct_2": 6, "dur_2": .125}
    )

    assert base_kwargs == {"dur": .25, "oct": 5}
    assert variants == {2: (None, {"oct": 6, "dur": .125})}


def test_several_distinct_variants():
    base_degree, base_kwargs, variants = split_variant_kwargs(
        [0, 2, 4, 5], {"dur": .25, "oct": 5, "oct_2": 6, "oct_3": 7}
    )

    assert base_kwargs == {"dur": .25, "oct": 5}
    assert variants == {2: (None, {"oct": 6}), 3: (None, {"oct": 7})}


def test_degree_n_overrides_the_note_pattern_not_a_kwarg():
    base_degree, base_kwargs, variants = split_variant_kwargs(
        [0, 2, 4, 5], {"dur": .25, "degree_2": [0, 1, 2, 3]}
    )

    assert base_degree == [0, 2, 4, 5]
    assert base_kwargs == {"dur": .25}
    assert variants == {2: ([0, 1, 2, 3], {})}


def test_degree_n_can_be_combined_with_other_overrides_on_same_variant():
    base_degree, base_kwargs, variants = split_variant_kwargs(
        [0, 2, 4, 5], {"dur": .25, "oct": 5, "degree_2": [0, 1, 2, 3], "oct_2": 6}
    )

    assert variants == {2: ([0, 1, 2, 3], {"oct": 6})}


def test_out_of_range_suffixes_are_left_as_literal_kwargs():
    base_degree, base_kwargs, variants = split_variant_kwargs(
        [0, 2, 4, 5],
        {"oct": 5, "oct_1": 99, "oct_0": 99, "oct_10": 99, "oct_99": 99},
    )

    assert variants == {}
    assert base_kwargs == {
        "oct": 5, "oct_1": 99, "oct_0": 99, "oct_10": 99, "oct_99": 99,
    }


def test_real_glued_digit_params_are_not_mistaken_for_variants():
    # room2/mix2/damp2 etc. are real, distinct effect params in Renardo
    # (see python_defined_effect_synthdefs.py) -- no underscore, so they
    # must never be split into a variant.
    base_degree, base_kwargs, variants = split_variant_kwargs(
        [0, 2, 4, 5], {"room": .3, "room2": .5, "mix2": .2}
    )

    assert variants == {}
    assert base_kwargs == {"room": .3, "room2": .5, "mix2": .2}


def test_sample_players_use_the_same_convention():
    base_degree, base_kwargs, variants = split_variant_kwargs(
        0, {"sample": 2, "room_2": .5, "sample_2": 4}
    )

    assert base_kwargs == {"sample": 2}
    assert variants == {2: (None, {"room": .5, "sample": 4})}
