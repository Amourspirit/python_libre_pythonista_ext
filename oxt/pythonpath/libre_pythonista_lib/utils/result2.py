from typing import TypeVar, Union, Generic, Iterator, TypeGuard, Tuple, Optional

T = TypeVar("T")
E = TypeVar("E", bound=Union[BaseException, None])  # Can be None or BaseException
T_Success = TypeVar("T_Success")
E_Failure = TypeVar("E_Failure", bound=Union[BaseException, None])


# class Result(Generic[T, E]):
class Result2:
    class Success(Generic[T_Success]):
        def __init__(self, data: T_Success) -> None:
            self.data: T_Success = data
            self.error: None = None

        def __iter__(self) -> Iterator[Union[T_Success, None]]:
            return iter((self.data, self.error))

        def unpack(self) -> Tuple[T_Success, None]:
            return (self.data, self.error)

        def is_success(self) -> bool:
            return True

    class Failure(Generic[E_Failure]):
        def __init__(self, error: E_Failure) -> None:
            self.data: None = None
            self.error: E_Failure = error

        def __iter__(self) -> Iterator[Union[None, E_Failure]]:
            return iter((self.data, self.error))

        def unpack(self) -> Tuple[None, E_Failure]:
            return (self.data, self.error)

        def is_success(self) -> bool:
            return False

    @staticmethod
    def success(data: T_Success) -> "Result.Success[T_Success]":
        return Result.Success(data)

    @staticmethod
    def failure(error: E_Failure) -> "Result.Failure[E_Failure]":
        return Result.Failure(error)

    @staticmethod
    def is_success(
        obj: Union["Result.Success[T_Success]", "Result.Failure[E_Failure]"],
    ) -> TypeGuard["Result.Success[T_Success]"]:
        return isinstance(obj, Result.Success)
