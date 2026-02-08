import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_add_item_to_order_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/orders/add-item",
        json={"order_id": 1, "nomenclature_id": 1, "quantity": 1}
    )
    """
    Test case for successfully adding a new item to an existing order.

    Verifies that the API returns a success status code (200 or 201) and that
    the quantity field is correctly updated in the response body.

    Args:
        client: An asynchronous HTTP test client fixture provided by pytest-asyncio/httpx.
    """
    assert response.status_code in [200, 201]
    assert response.json()["quantity"] >= 1

@pytest.mark.asyncio
async def test_api_order_not_found_error(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/orders/add-item",
        json={"order_id": 999, "nomenclature_id": 1, "quantity": 1}
    )
    """
    Test case for handling an error when an order ID does not exist.

    Verifies that the API correctly handles a non-existent order ID by returning
    a 404 Not Found status code and a descriptive error message.

    Args:
        client: An asynchronous HTTP test client fixture provided by pytest-asyncio/httpx.
    """
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"].lower()
