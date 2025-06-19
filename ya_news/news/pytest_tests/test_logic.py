from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


def test_user_can_create_comment(author_client, author, form_data, news):
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == comments_count + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_note(client, form_data, news):
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count


def test_user_cant_use_bad_words(author_client, news, form_data):
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] = f'{BAD_WORDS[0]} текст'
    response = author_client.post(url, data=form_data)
    assertFormError(
        response.context['form'], 'text',
        errors=WARNING)
    assert Comment.objects.count() == comments_count


def test_author_can_delete_comment(author_client, news, comment):
    comments_count = Comment.objects.count()
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count - 1


def test_author_can_edit_comment(author_client, news, form_data, comment):
    comments_count = Comment.objects.count()
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count


def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    comments_count = Comment.objects.count()
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count


def test_user_cant_edit_comment_of_another_user(
        reader_client,
        form_data,
        comment
):
    url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
