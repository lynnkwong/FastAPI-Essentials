from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    price: float


class ProductCreate(ProductBase):
    pid: int


class ProductUpdate(BaseModel):
    name: str | None
    price: float | None


class ProductDb(ProductBase):
    pid: int


class ProductResponse(ProductBase):
    pid: int


products: dict[int, ProductDb] = {}


async def verify_pid(pid: int):
    if not products.get(pid):
        raise HTTPException(
            status_code=404, detail=f"Product with id {pid} doesn't exists."
        )


# Create an instance of APIRouter rather than FastAPI.
router = APIRouter()


# Use the router instance rather than app.
# Create. Change the default status code from 200 to 201.
@router.post("/products", status_code=202)
async def create_product(product: ProductCreate) -> int:
    if product.pid not in products:
        products[product.pid] = product
        return product.pid

    raise HTTPException(
        status_code=409,
        detail=f"Product with id {product.pid} already exists.",
    )


# Read. Add an additional response for OpenAPI docs.
@router.get(
    "/products/{pid: int}",
    responses={404: {"description": "Product not found."}},
    dependencies=[Depends(verify_pid)],
)
async def read_product(pid: int) -> ProductResponse:
    return products[pid]


# Update (Put)
@router.put("/products/{pid: int}")
async def update_product(pid: int, product: ProductBase):
    products[pid] = product


# Patch (Patch)
@router.patch(
    "/products/{pid: int}",
    responses={404: {"description": "Product not found."}},
    dependencies=[Depends(verify_pid)],
)
async def patch_product(pid: int, product_update: ProductUpdate):
    existing_product = products[pid]
    patched_product = existing_product.copy(
        update=product_update.dict(exclude_unset=True)
    )
    existing_product[pid] = patched_product


# Delete
@router.delete(
    "/products/{pid: int}",
    responses={404: {"description": "Product not found."}},
    dependencies=[Depends(verify_pid)],
)
async def read_product(pid: int):
    products.pop(pid)
