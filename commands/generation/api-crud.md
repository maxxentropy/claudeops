# Generate Complete CRUD API

🎯 **COMMAND**: /api-crud | 📋 **WORKFLOW**: Workflow | 👤 **PERSONAS**: Default

Create a full-featured REST API with all CRUD operations, following best practices.

## Path Resolution
API files will be created in appropriate repository-relative directories, automatically resolved from any working directory.

**Implementation Note:**
```python
# Import path resolution utilities
import sys
import os
sys.path.insert(0, os.path.expanduser('~/.claude'))
from system.utils import path_resolver

# Standard API structure
controller_dir = path_resolver.ensure_directory('lib')
service_dir = path_resolver.ensure_directory('lib')
dto_dir = path_resolver.ensure_directory('lib')
test_dir = path_resolver.ensure_directory('tests')

# Create subdirectories
(controller_dir / 'controllers').mkdir(exist_ok=True)
(service_dir / 'services').mkdir(exist_ok=True)
(dto_dir / 'dtos').mkdir(exist_ok=True)
(test_dir / 'api').mkdir(exist_ok=True)

# Define file paths
controller_path = controller_dir / 'controllers' / f'{entity_name}Controller.cs'
service_path = service_dir / 'services' / f'{entity_name}Service.cs'
dto_path = dto_dir / 'dtos' / f'{entity_name}Dto.cs'
test_path = test_dir / 'api' / f'{entity_name}ControllerTests.cs'

# After creating files, format output
output_paths = {
    "Controller created": controller_path,
    "Service created": service_path,
    "DTOs created": dto_path,
    "Tests created": test_path
}
print(path_resolver.format_output_message(output_paths))
```

**Important**: Never hardcode paths. Always use the path resolver to ensure files are created in the correct repository-relative locations.

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