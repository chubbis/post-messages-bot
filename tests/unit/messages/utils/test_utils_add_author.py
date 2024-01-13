from bot_v3.handlers.messages.utils import add_author


def test_add_author_true():
    username = "test_author"
    message_text = f"There is @{username} in message"
    message_text_with_author = add_author(text=message_text, author_name=username)
    assert message_text_with_author == message_text


def test_add_author_true_with_no_eq_case_in_username():
    username = "Test_Author"
    message_text = f"There is @test_author in message"
    message_text_with_author = add_author(text=message_text, author_name=username)
    assert message_text_with_author == message_text


def test_add_author_true_with_no_eq_case_in_message_text():
    username = "test_author"
    in_message_username = "Test_Author"
    message_text = f"There is @{in_message_username} in message"
    message_text_with_author = add_author(text=message_text, author_name=username)
    assert message_text_with_author == message_text


def test_add_author_true_with_no_eq_case_in_message_text_2():
    username = "Test_Author"
    in_message_username = "test_author"
    message_text = f"There is @{in_message_username} in message"
    message_text_with_author = add_author(text=message_text, author_name=username)
    assert message_text_with_author == message_text


def test_add_author_true_with_no_eq_case_in_message_text_and_username():
    username = "Test_author"
    in_message_username = "test_Author"
    message_text = f"There is @{in_message_username} in message"
    message_text_with_author = add_author(text=message_text, author_name=username)
    assert message_text_with_author == message_text


def test_add_author_false():
    username = "test_author"
    message_text = f"There is no author_name in message"
    message_text_with_author = add_author(text=message_text, author_name=username)
    assert (
        message_text_with_author
        == f"{message_text}\n\n------------\nAuthor: @{username}"
    )
