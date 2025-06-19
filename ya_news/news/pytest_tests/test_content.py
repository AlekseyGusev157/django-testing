from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


def test_home_page(client, news_count_ten):
    urls = reverse('news:home')
    response = client.get(urls)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_count_ten):
    urls = reverse('news:home')
    response = client.get(urls)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_detail_page_contains_form(author_client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url, data=form_data)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_detail_page_contains_form_for_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


def test_comments_order(client, news, commets):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_date_created = [comment.created for comment in all_comments]
    sorted_date = sorted(all_date_created)
    assert all_date_created == sorted_date
