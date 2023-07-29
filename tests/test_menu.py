from httpx import AsyncClient


async def test_create_menu(ac: AsyncClient):

    data = {
        "title": "Test Menu",
        "description": "Test Menu Description"
    }

    response = await ac.post('/api/v1/menus', json=data)
    assert response.status_code == 201, f'Expected status code 201, but got "{response.status_code}"'
    assert response.headers["Content-Type"] == "application/json", "Content-Type header is not application/json"

    response_data = response.json()
    assert "title" in response_data, '"title" field is missing in the response'
    assert "description" in response_data, '"description" field is missing in the response'
    assert "id" in response_data, '"id" field is missing in the response'
    assert "submenus_count" in response_data, '"submenus_count" field is missing in the response'
    assert "dishes_count" in response_data, '"dishes_count" field is missing in the response'


async def test_get_list_menu(ac: AsyncClient):
    
    response = await ac.get('/api/v1/menus')
    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers["Content-Type"] == "application/json", "Content-Type header is not application/json"

    response_data = response.json()
    assert isinstance(response_data, list)
    if response_data:
        menu = response_data[0]
        assert "title" in menu, '"title" field is missing in the response'
        assert "description" in menu, '"description" field is missing in the response'
        assert "id" in menu, '"id" field is missing in the response'
        assert "submenus_count" in menu, '"submenus_count" field is missing in the response'
        assert "dishes_count" in menu, '"dishes count" field is missing in the response'


async def test_get_specific_menu(ac: AsyncClient, menu_id: str):

    response = await ac.get(f'/api/v1/menus/{menu_id}')
    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers["Content-Type"] == "application/json", "Content-Type header is not application/json"

    response_data = response.json()
    assert "title" in response_data, '"title" field is missing in the response'
    assert "description" in response_data, '"description" field is missing in the response'
    assert "id" in response_data, '"id" field is missing in the response'
    assert "submenus_count" in response_data, '"submenus" count field is missing in the response'
    assert "dishes_count" in response_data, '"dishes" count field is missing in the response'


async def test_update_menu(ac: AsyncClient, menu_id: str):

    new_data_for_menu = {
        "title": "Updated Menu",
        "description": "Updated Menu Description"
    }

    updated_menu_response = await ac.patch(f'/api/v1/menus/{menu_id}', json=new_data_for_menu)
    assert updated_menu_response.status_code == 200, f'Expected status code 200, but got "{updated_menu_response.status_code}"'
    assert updated_menu_response.headers["Content-Type"] == "application/json", "Content-Type header is not application/json"

    updated_menu = updated_menu_response.json()
    assert "title" in updated_menu, '"title" field is missing in the response'
    assert "description" in updated_menu, '"description" field is missing in the response'
    assert updated_menu['title'] == new_data_for_menu['title']
    assert updated_menu['description'] == new_data_for_menu['description']


async def test_delete_menu(ac: AsyncClient, menu_id: str):

    response = await ac.delete(f'/api/v1/menus/{menu_id}')
    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers["Content-Type"] == "application/json", "Content-Type header is not application/json"