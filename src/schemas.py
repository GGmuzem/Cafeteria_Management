from pydantic import BaseModel, field_validator
from database.store import Storage

class StorageCreate(BaseModel):
    name: str
    count: int
    type_of_product: str

    @field_validator('name')
    def name_must_be_unique(cls, v):
        if Storage.query.filter_by(name=v).first():
            raise ValueError('Товар с таким названием уже существует')
        return v

    @field_validator('count')
    def count_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Количество не может быть отрицательным')
        return v
    @field_validator('type_of_product')
    def type_of_product_must_be_in_list(cls, v):
        if v not in ['блюдо', 'продукт']:
            raise ValueError('Тип продукта должен быть одним из: блюдо, продукт')
        return v

class StorageDelete(BaseModel):
    name: str

    @field_validator('name')
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Название не может быть пустым')
        return v
