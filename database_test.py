import pytest

from database import Database

"""
Tests all function that alter or add data in the database
Function that return data and establish/end connections are not explicitly tested, as they are
included in the other functions

Tests only work on an empty database! Don't forget to reset the values for Auto Increment!
"""


@pytest.fixture
def fxt_db():
    fxt_db = Database()
    return fxt_db


def test_add_player(fxt_db):
    test_db = fxt_db
    test_db.add_player('test@gmx.de', 'hallo123', 'maxMustermann')
    private_data = test_db.fetch_full_userdata(1)
    assert private_data == [(1, 'test@gmx.de', 'hallo123', 'maxMustermann', 0, 0, 0, 1000, None)]
    public_data = test_db.fetch_public_userdata(1)
    assert public_data == [('maxMustermann', 0, 0, 0, 1000)]


def test_add_game(fxt_db):
    test_db = fxt_db
    test_db.add_game(1, 2, 1)
    private_data = test_db.fetch_full_gamedata(1)
    assert private_data == [(1, 1, 2, 1)]
    public_data = test_db.fetch_public_gamedata(1)
    assert public_data == [(1, 2, 1)]


def test_add_save(fxt_db):
    test_db = fxt_db
    test_db.add_save('MaxM_Save')
    data = test_db.fetch_full_savedata(1)
    assert data == [(1, 'MaxM_Save')]


def test_add_win(fxt_db):
    test_db = fxt_db
    test_db.add_win(1)
    data = test_db.fetch_public_userdata(1)
    assert data == [('maxMustermann', 1, 0, 0, 1000)]


def test_add_loss(fxt_db):
    test_db = fxt_db
    test_db.add_loss(1)
    data = test_db.fetch_public_userdata(1)
    assert data == [('maxMustermann', 1, 1, 0, 1000)]


def test_add_remis(fxt_db):
    test_db = fxt_db
    test_db.add_remis(1)
    data = test_db.fetch_public_userdata(1)
    assert data == [('maxMustermann', 1, 1, 1, 1000)]


def test_change_elo(fxt_db):
    test_db = fxt_db
    test_db.change_elo(1, 500)
    data = test_db.fetch_public_userdata(1)
    assert data == [('maxMustermann', 1, 1, 1, 500)]


def test_change_saveid(fxt_db):
    test_db = fxt_db
    test_db.change_saveid(1, 'MaxM_Save')
    data = test_db.fetch_full_userdata(1)
    assert data == [(1, 'test@gmx.de', 'hallo123', 'maxMustermann', 1, 1, 1, 500, 1)]
