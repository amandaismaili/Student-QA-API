import pytest
from httpx import AsyncClient
from test.conftest import auth_header, create_test_user, login_user


@pytest.mark.anyio
async def test_create_user_validation_error(client: AsyncClient):
    response = await client.post(
        "/account/register",
        json = {"username": "user"}
    )

    assert response.status_code == 422
    assert "email" in response.text
    assert "password" in response.text


@pytest.mark.anyio
async def test_duplicate_email(client: AsyncClient):
    await create_test_user(client, username="dupuser", email="dup@test.com")

    response = await client.post(
        "/account/register",
        json={"username": "new_user", "email": "dup@test.com", "password": "fakepw234"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists."


@pytest.mark.anyio
async def test_create_user(client: AsyncClient):
    response = await client.post(
        "/account/register",
        json = {
            "username": "user_acc",
            "email": "useremail@gmail.com",
            "password": "newpass3456"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "user_acc"
    assert data["email"] == "useremail@gmail.com"
    assert "id" in data
    assert "image_path" in data
    assert "password" not in data
    assert "password_hash" not in data