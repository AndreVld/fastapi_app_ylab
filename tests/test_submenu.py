from httpx import AsyncClient


async def test_create_submenu(ac: AsyncClient, menu_id: str):

    data = {
        'title': 'Test Submenu',
        'description': 'Test Submenu Description'
    }

    response = await ac.post(f'/api/v1/menus/{menu_id}/submenus', json=data)
    assert response.status_code == 201, f'Expected status code 201, but got "{response.status_code}"'
    assert response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'

    response_data = response.json()
    assert 'title' in response_data, '"title" field is missing in the response'
    assert 'description' in response_data, '"description" field is missing in the response'
    assert 'id' in response_data, '"id" field is missing in the response'
    assert 'menu_id' in response_data, '"menu_id" field is missing in the response'
    assert 'dishes_count' in response_data, '"dishes count" field is missing in the response'


async def test_get_list_submenu(ac: AsyncClient, menu_id: str):

    response = await ac.get(f'/api/v1/menus/{menu_id}/submenus')

    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'

    response_data = response.json()
    assert isinstance(response_data, list)
    if response_data:
        submenu = response_data[0]
        assert 'title' in submenu, '"title" field is missing in the response'
        assert 'description' in submenu, '"description" field is missing in the response'
        assert 'id' in submenu, '"id" field is missing in the response'
        assert 'menu_id' in submenu, '"menu_id" field is missing in the response'
        assert 'dishes_count' in submenu, '"dishes count" field is missing in the response'


async def test_get_specific_submenu(ac: AsyncClient, menu_id: str, submenu_id: str):

    response = await ac.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'

    assert response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'
    response_data = response.json()
    assert 'title' in response_data, '"title" field is missing in the response'
    assert 'description' in response_data, '"description" field is missing in the response'
    assert 'id' in response_data, '"id" field is missing in the response'
    assert 'menu_id' in response_data, '"menu_id" field is missing in the response'
    assert 'dishes_count' in response_data, '"dish count" field is missing in the response'


async def test_update_submenu(ac: AsyncClient, menu_id: str, submenu_id: str):

    new_data_for_submenu = {
        'title': 'Updated Submenu',
        'description': 'Updated Submenu Description'
    }

    updated_submenu_response = await ac.patch(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}', json=new_data_for_submenu)
    assert updated_submenu_response.status_code == 200, f'Expected status code 200, but got "{updated_submenu_response.status_code}"'
    assert updated_submenu_response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'
    updated_submenu = updated_submenu_response.json()
    assert 'title' in updated_submenu, '"title" field is missing in the response'
    assert 'description' in updated_submenu, '"description" field is missing in the response'
    assert updated_submenu['title'] == new_data_for_submenu['title']
    assert updated_submenu['description'] == new_data_for_submenu['description']


async def test_delete_submenu(ac: AsyncClient, menu_id: str, submenu_id: str):

    response = await ac.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'
