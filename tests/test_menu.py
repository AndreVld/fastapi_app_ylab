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
    assert "submenus_count" in response_data, '"submenus" count field is missing in the response'
    assert "dishes_count" in response_data, '"dishes" count field is missing in the response'


async def test_get_list_menu(ac: AsyncClient):
    
    response = await ac.get('/api/v1/menus')

    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers["Content-Type"] == "application/json", "Content-Type header is not application/json"

    response_data = response.json()
    assert isinstance(response_data, list)  




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

    updated_menu_data = {
        "title": "Updated Menu",
        "description": "Updated Menu Description"
    }

    update_response = await ac.patch(f'/api/v1/menus/{menu_id}', json=updated_menu_data)
    assert update_response.status_code == 200, f'Expected status code 200, but got "{update_response.status_code}"'

    updated_menu_response = await ac.get(f'/api/v1/menus/{menu_id}')
    assert updated_menu_response.status_code == 200
    assert updated_menu_response.headers["Content-Type"] == "application/json", "Content-Type header is not application/json"

    updated_menu = updated_menu_response.json()
    assert updated_menu['title'] == updated_menu_data['title']
    assert updated_menu['description'] == updated_menu_data['description']


async def test_delete_menu(ac: AsyncClient, menu_id: str):

    response = await ac.delete(f'/api/v1/menus/{menu_id}')

    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'