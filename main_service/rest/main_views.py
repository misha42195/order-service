from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from starlette.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/products/admin", name="products:create-view")  # Добавьте / в конце
async def get_page(request: Request):
    return templates.TemplateResponse(
        "admin.html", {"request": request, "products": []}
    )


@router.post("/products/admin/", name="products:create")  # Тот же путь, но POST
async def create_product(request: Request):
    # Логика обработки формы
    return RedirectResponse(
        url=request.url_for("products:create-view"), status_code=303
    )
