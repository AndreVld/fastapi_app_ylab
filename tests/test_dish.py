from httpx import AsyncClient


async def test_create_dish(ac: AsyncClient, menu_id: str, submenu_id: str):

    data = {
        'title': 'Test Dish',
        'description': 'Test Dish description',
        'price': '231.53'
    }

    response = await ac.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=data)
    assert response.status_code == 201, f'Expected status code 201, but got "{response.status_code}"'
    assert response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'

    response_data = response.json()
    assert 'title' in response_data, '"title" field is missing in the response'
    assert 'description' in response_data, '"description" field is missing in the response'
    assert 'id' in response_data, '"id" field is missing in the response'
    assert 'price' in response_data, '"price" field is missing in the response'
    assert 'submenu_id' in response_data, '"submenu_id" field is missing in the response'


async def test_get_list_dishes(ac: AsyncClient, menu_id: str, submenu_id: str):

    response = await ac.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes')

    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'

    response_data = response.json()
    assert isinstance(response_data, list)
    if response_data:
        dish = response_data[0]
        assert 'title' in dish, '"title" field is missing in the response'
        assert 'description' in dish, '"description" field is missing in the response'
        assert 'id' in dish, '"id" field is missing in the response'
        assert 'price' in dish, '"price" field is missing in the response'
        assert 'submenu_id' in dish, '"submenu_id" field is missing in the response'


async def test_get_specific_dish(ac: AsyncClient, menu_id: str, submenu_id: str, dish_id: str):

    response = await ac.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'

    response_data = response.json()
    assert 'title' in response_data, '"title" field is missing in the response'
    assert 'description' in response_data, '"description" field is missing in the response'
    assert 'id' in response_data, '"id" field is missing in the response'
    assert 'price' in response_data, '"price" field is missing in the response'
    assert 'submenu_id' in response_data, '"submenu_id" field is missing in the response'


async def test_update_dish(ac: AsyncClient, menu_id: str, submenu_id: str, dish_id: str):

    new_data_for_dish = {
        'title': 'My updated dish 1',
        'description': 'My updated dish description 1',
        'price': '212.31'
    }

    updated_dish_response = await ac.patch(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', json=new_data_for_dish)
    assert updated_dish_response.status_code == 200, f'Expected status code 200, but got "{updated_dish_response.status_code}"'
    assert updated_dish_response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'

    updated_dish = updated_dish_response.json()
    assert 'id' in updated_dish, '"id" field is missing in the response'
    assert 'title' in updated_dish, '"title" field is missing in the response'
    assert 'description' in updated_dish, '"description" field is missing in the response'
    assert 'price' in updated_dish, '"price" field is missing in the response'
    assert 'submenu_id' in updated_dish, '"submenu_id" field is missing in the response'
    assert updated_dish['title'] == new_data_for_dish['title']
    assert updated_dish['description'] == new_data_for_dish['description']
    assert updated_dish['price'] == new_data_for_dish['price']


async def test_delete_dish(ac: AsyncClient, menu_id: str, submenu_id: str, dish_id: str):

    response = await ac.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
    assert response.status_code == 200, f'Expected status code 200, but got "{response.status_code}"'
    assert response.headers['Content-Type'] == 'application/json', 'Content-Type header is not application/json'
