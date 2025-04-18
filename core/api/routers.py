from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal, Optional, Sequence, Type

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import ORJSONResponse, Response
from pydantic import BaseModel, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from core.database import get_session
from core.database.models.user import User

if TYPE_CHECKING:
    from core.api.services import C, CRUDService, S, U

UserDependenciesMethodsType = (
    Literal["list"] | Literal["create"] | Literal["update"] | Literal["delete"] | Literal["retrieve"]
)
UserDependenciesMapType = Optional[dict[UserDependenciesMethodsType, Callable]]


class CRUDRouterConfig:
    def __init__(
        self,
        prefix: str,
        tags: list[str],
        create_schema: Type[C],
        update_schema: Type[U],
        response_schema: Type[S],
        crud_service: CRUDService,
        user_dependencies_map: UserDependenciesMapType = None,
        excluded_opts: Optional[Sequence[UserDependenciesMethodsType]] = None,
    ):
        self.prefix = prefix
        self.tags = tags
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        self.crud_service = crud_service
        self.user_dependencies_map = user_dependencies_map or {}
        self.excluded_opts = excluded_opts or tuple()


class CRUDRouter:
    def __init__(self, config: CRUDRouterConfig):
        self.config = config
        self.router = APIRouter(prefix=config.prefix, tags=config.tags)
        self._setup_routes()

    def _get_user_dependency(self, method: UserDependenciesMethodsType) -> Callable:
        return self.config.user_dependencies_map.get(method)

    async def _get_schema_validated_request_data(self, request: Request, schema_class: Type[BaseModel]) -> BaseModel:  # noqa
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")

        adapter = TypeAdapter(schema_class)
        return adapter.validate_python(data)

    def get_query_params(self, request: Request) -> dict:  # noqa
        return dict(request.query_params)

    def _setup_routes(self):
        list_user_dependency = self._get_user_dependency("list")
        retrieve_user_dependency = self._get_user_dependency("retrieve")
        create_user_dependency = self._get_user_dependency("create")
        update_user_dependency = self._get_user_dependency("update")
        delete_user_dependency = self._get_user_dependency("delete")

        create_schema_class = self.config.create_schema
        update_schema_class = self.config.update_schema
        response_schema_class = self.config.response_schema

        if "list" not in self.config.excluded_opts:

            @self.router.get("/", response_model=list[response_schema_class])
            async def get_entities(
                session: AsyncSession = Depends(get_session),
                user: User = Depends(list_user_dependency),
                query: dict = Depends(self.get_query_params),
            ) -> ORJSONResponse:
                entities = await self.config.crud_service.get_entities_list(session, query, user)
                return ORJSONResponse(entities)

        if "retrieve" not in self.config.excluded_opts:

            @self.router.get("/{id}", response_model=list[response_schema_class])
            async def retrieve_entity(
                id: int,  # noqa
                session: AsyncSession = Depends(get_session),
                user: User = Depends(retrieve_user_dependency),
            ) -> ORJSONResponse:
                entity = await self.config.crud_service.retrieve_entity(id, session, user)
                return ORJSONResponse(entity)

        if "create" not in self.config.excluded_opts:

            @self.router.post("/", response_model=response_schema_class)
            async def create_entity(
                request: Request,
                session: AsyncSession = Depends(get_session),
                user: User = Depends(create_user_dependency),
            ) -> ORJSONResponse:
                create_schema = await self._get_schema_validated_request_data(request, create_schema_class)
                entity = await self.config.crud_service.create_entity(create_schema, session, user)
                return ORJSONResponse(entity, status_code=status.HTTP_201_CREATED)

        if "update" not in self.config.excluded_opts:

            @self.router.patch(
                "/{id}",
                response_model=response_schema_class,
            )
            async def update_entity(
                request: Request,
                id: int,  # noqa
                session: AsyncSession = Depends(get_session),
                user: User = Depends(update_user_dependency),
            ) -> ORJSONResponse:
                update_schema = await self._get_schema_validated_request_data(request, update_schema_class)
                entity = await self.config.crud_service.update_entity(id, update_schema, session, user)
                return ORJSONResponse(entity)

        if "delete" not in self.config.excluded_opts:

            @self.router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
            async def delete_entity(
                id: int,  # noqa
                session: AsyncSession = Depends(get_session),
                user: User = Depends(delete_user_dependency),
            ) -> Response:
                await self.config.crud_service.remove_entity(id, session, user)
                return Response(status_code=status.HTTP_204_NO_CONTENT)
