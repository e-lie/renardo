import strawberry
from typing import Optional


@strawberry.type
class ExecuteCodeResult:
    success: bool
    message: str
    output: Optional[str] = None


@strawberry.type
class Mutation:
    @strawberry.field
    def execute_code(self, code: str) -> ExecuteCodeResult:
        """Execute Python code in the Renardo runtime"""
        try:
            # Import the execute function from renardo runtime
            from ..runtime import execute

            # Execute the code
            result = execute(code, verbose=True)

            return ExecuteCodeResult(
                success=True,
                message="Code executed successfully",
                output=str(result) if result else None,
            )
        except Exception as e:
            return ExecuteCodeResult(
                success=False, message=f"Error executing code: {str(e)}", output=None
            )


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        """Simple query for GraphQL health check"""
        return "Hello from Renardo!"


schema = strawberry.Schema(query=Query, mutation=Mutation)
