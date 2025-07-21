# Generate Complete CRUD API

🎯 **COMMAND**: /api-crud | 📋 **WORKFLOW**: Workflow | 👤 **PERSONAS**: Default

Create a full-featured REST API with all CRUD operations, following best practices.

## Steps:

1. Analyze the entity/model to create API for
2. Generate the controller with proper routing and attributes
3. Create request/response DTOs with validation
4. Implement service layer with business logic
5. Create repository interface and implementation
6. Add comprehensive error handling
7. Generate Swagger documentation
8. Create unit tests for controller and service
9. Add integration tests for API endpoints

## Template Structure:

### Controller:
```csharp
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class EntitiesController : ControllerBase
{
    // GET: api/entities
    [HttpGet]
    [ProducesResponseType(typeof(IEnumerable<EntityDto>), 200)]
    
    // GET: api/entities/5
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(EntityDto), 200)]
    [ProducesResponseType(404)]
    
    // POST: api/entities
    [HttpPost]
    [ProducesResponseType(typeof(EntityDto), 201)]
    [ProducesResponseType(typeof(ValidationProblemDetails), 400)]
    
    // PUT: api/entities/5
    [HttpPut("{id}")]
    [ProducesResponseType(204)]
    [ProducesResponseType(typeof(ValidationProblemDetails), 400)]
    [ProducesResponseType(404)]
    
    // DELETE: api/entities/5
    [HttpDelete("{id}")]
    [ProducesResponseType(204)]
    [ProducesResponseType(404)]
}
```

### Features to Include:
- Pagination support with query parameters
- Filtering and sorting capabilities
- Async/await throughout
- Proper HTTP status codes
- Global exception handling
- Request/response logging
- API versioning support
- HATEOAS links (if requested)
- Rate limiting headers
- Caching headers

### Validation:
- Use FluentValidation for complex rules
- Data annotations for simple validation
- Custom validation attributes as needed
- Validate query parameters

### Error Responses:
- Use ProblemDetails RFC 7807
- Consistent error format
- Meaningful error messages
- Include correlation IDs