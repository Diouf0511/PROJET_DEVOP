from data.loader import load_data


def test_data_not_empty():
    df = load_data()
    assert not df.empty


def test_columns_exist():
    df = load_data()
    assert 'age' in df.columns
    assert 'sex' in df.columns


def test_no_null_age():
    df = load_data()
    assert df['age'].isnull().sum() == 0

# (Appuie bien sur ENTRÉE ici pour laisser une ligne vide à la fin)