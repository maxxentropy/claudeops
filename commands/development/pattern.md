# /pattern - Code Pattern Implementation

Embody this expert persona:
<!-- INCLUDE: ../system/personas.md#SOFTWARE_ARCHITECT -->

Load relevant patterns based on request:

## Available Patterns:

### Error Handling
<!-- INCLUDE: ../system/principles.md#ERROR_PATTERN -->

### MAUI/Prism
<!-- INCLUDE: ../system/principles.md#MAUI_PRISM -->

### Additional Patterns:

1. **Repository Pattern**:
```csharp
public interface IRepository<T>
{
    Task<T> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();
    Task<T> AddAsync(T entity);
    Task UpdateAsync(T entity);
    Task DeleteAsync(int id);
}
```

2. **Service Layer**:
```csharp
public interface IUserService
{
    Task<Result<UserDto>> GetUserAsync(int id);
    Task<Result<IEnumerable<UserDto>>> GetAllUsersAsync();
    Task<Result<UserDto>> CreateUserAsync(CreateUserDto dto);
}
```

3. **Logging Pattern**:
```csharp
_logger.LogInformation("Processing {EntityType} with ID {EntityId}", 
    nameof(User), userId);
```

4. **Validation Pattern**:
```csharp
public class UserValidator : AbstractValidator<User>
{
    public UserValidator()
    {
        RuleFor(x => x.Email).NotEmpty().EmailAddress();
        RuleFor(x => x.Age).GreaterThan(0).LessThan(150);
    }
}
```

5. **API Response Pattern**:
```csharp
return Ok(new ApiResponse<T> 
{ 
    Success = true, 
    Data = result, 
    Message = "Operation successful" 
});
```

## Implementation Steps:
1. Identify which pattern is needed
2. Apply pattern with project-specific naming
3. Follow language standards:
<!-- INCLUDE: ../system/principles.md#LANG_STANDARDS -->
4. Include appropriate error handling
5. Add tests for the pattern implementation

Example usage: `/pattern error-handling` or `/pattern repository for User entity`