import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_api_add_item_to_order_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/orders/add-item",
        json={"order_id": 1, "nomenclature_id": 1, "quantity": 1}
    )
    assert response.status_code in [200, 201]
    assert response.json()["quantity"] >= 1

@pytest.mark.asyncio
async def test_api_order_not_found_error(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/orders/add-item",
        json={"order_id": 999, "nomenclature_id": 1, "quantity": 1}
    )
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"].lower()
