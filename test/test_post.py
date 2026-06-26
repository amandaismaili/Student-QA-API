import pytest
from httpx import AsyncClient

from test.conftest import auth_header, create_test_user, login_user

@pytest.mark.anyio
async def test_get_posts_empty(client: AsyncClient):
    response = await client.get("/section")

    assert response.status_code == 200

    data = response.json()
    assert data == []


@pytest.mark.anyio
async def test_get_notfound(client: AsyncClient):
    response = await client.get("/section/search/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found."


@pytest.mark.anyio
async def test_create_post(client: AsyncClient):
    user = await create_test_user(client)
    token = await login_user(client)
    headers = auth_header(token)

    response = await client.post(
        "/section/questions",
        json = {"title": "New post here here", "content": "word word word"},
        headers= headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New post here here"
    assert data["content"] == "word word word"
    assert data["user_id"] == user["id"]
    assert "id" in data
    assert "date_posted" in data
    assert data["author"]["username"] == "user"


@pytest.mark.anyio
async def test_create_post_notauth(client: AsyncClient):
    response = await client.post(
        "/section/questions", 
        json={"title": "New post here", "content": "hello"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_update_post(client: AsyncClient):
    await create_test_user(client, username="updateuser", email="update@test.com")
    token = await login_user(client, email="update@test.com")
    headers = auth_header(token)

    repsonse = await client.post(
        "/section/questions",
        json = {"title": "original post here", "content": "original cntnt"},
        headers=headers
    )

    post_id = repsonse.json()["id"]

    repsonse = await client.patch(
        f"/section/search/{post_id}",
        json = {"title": "updated post here"},
        headers=headers
    )

    assert repsonse.status_code == 200
    data = repsonse.json()
    assert data["title"] == "updated post here"
    assert data["content"] == "original cntnt" 


@pytest.mark.anyio
async def test_update_post_wronguser(client: AsyncClient):
    await create_test_user(client, username="us1", email="us1@gmail.com")
    token1 = await login_user(client, email="us1@gmail.com")

    response = await client.post(
        "/section/questions",
        json = {"title": "new post here here", "content": "dont touch unless authorized"},
        headers = auth_header(token1)
    )

    post_id = response.json()["id"]

    await create_test_user(client, username="us2", email="us2@gmail.com")
    token2 = await login_user(client, email="us2@gmail.com")

    response = await client.patch(
        f"/section/search/{post_id}",
        json= {"title": "changed title"},
        headers = auth_header(token2)
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Cannot update this post."

