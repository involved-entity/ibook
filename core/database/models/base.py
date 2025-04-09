from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)

    def __str__(self):
        return f"{self.__name__}(id={self.id})"

    def __repr__(self):
        return str(self)

    @declared_attr.directive
    def __tablename__(self) -> str:
        return self.__name__.lower() + "s"
