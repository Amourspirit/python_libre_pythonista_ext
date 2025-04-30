from __future__ import annotations
from typing import TypeVar, Union, Generic, Iterator, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import TypeIs
else:
    TypeIs = Union

T = TypeVar("T")
E = TypeVar("E", bound=Union[BaseException, None])
T_Success = TypeVar("T_Success")
E_Failure = TypeVar("E_Failure", bound=Union[BaseException, None])


class Result(Generic[T, E]):
    """
    A generic Result type that can represent either a successful operation with data
    or a failure with an error.

    Type Parameters:
        T: The type of the success value
        E: The type of the error value, must be BaseException or None

    Examples:
        >>> result = Result.success(10)
        >>> if Result.is_success(result):
        >>>     print(result.data)  # Outputs: 10
        >>> else:
        >>>     print(result.error)

        >>> result = Result.failure(ValueError("Invalid input"))
        >>> data, error = result.unpack()
        >>> print(error)  # Outputs: Invalid input
    """

    def __init__(self, data: T, error: E) -> None:
        """
        Initialize a Result instance.

        Args:
            data: The success value
            error: The error value
        """
        self.data: T = data
        self.error: E = error

    def __eq__(self, value: object) -> bool:
        """
        Check if two Result instances are equal.

        Args:
            value: The other Result instance to compare with

        Returns:
            True if the two instances are equal, False otherwise
        """
        if isinstance(value, Result):
            return self.data == value.data and self.error == value.error
        return False

    def __bool__(self) -> bool:
        """
        Check if the Result represents success.

        Returns:
            True if the Result represents success, False otherwise
        """
        return self.error is None

    def __repr__(self) -> str:
        """
        Get the string representation of the Result instance.

        Returns:
            A string representation of the Result instance
        """
        return f"Result(data={repr(self.data)}, error={repr(self.error)})"

    def __iter__(self) -> Iterator[Union[T, E]]:
        """
        Make Result instance iterable.

        Returns:
            Iterator yielding data and error values
        """
        return iter((self.data, self.error))

    def unpack(self) -> Tuple[T, E]:
        """
        Unpack the Result into a tuple of (data, error).

        Returns:
            A tuple containing the data and error values
        """
        return (self.data, self.error)

    @staticmethod
    def success(data: T_Success) -> "Result[T_Success, None]":
        """
        Create a successful Result with the given data.

        Args:
            data: The success value

        Returns:
            A Result instance representing success
        """
        return Result(data, None)

    @staticmethod
    def failure(error: E_Failure) -> "Result[None, E_Failure]":
        """
        Create a failure Result with the given error.

        Args:
            error: The error value

        Returns:
            A Result instance representing failure
        """
        return Result(None, error)

    @staticmethod
    def is_success(
        obj: Union["Result[T_Success, None]", "Result[None, E_Failure]"],
    ) -> TypeIs["Result[T_Success, None]"]:
        """
        Type guard to check if a Result instance represents success.

        Args:
            obj: The Result instance to check

        Returns:
            True if the Result represents success, False otherwise
        """
        return isinstance(obj, Result) and obj.error is None

    @staticmethod
    def is_failure(
        obj: Union["Result[T_Success, None]", "Result[None, E_Failure]"],
    ) -> TypeIs["Result[None, E_Failure]"]:
        """
        Type guard to check if a Result instance represents failure.

        Args:
            obj: The Result instance to check

        Returns:
            True if the Result represents failure, False otherwise
        """
        return isinstance(obj, Result) and obj.error is not None
