# Mobile App Scaffold Command - Prism Edition

🎯 **COMMAND**: /mobile-scaffold | 📋 **WORKFLOW**: Workflow | 👤 **PERSONAS**: Default

Create a complete MAUI mobile application using Prism framework with modular architecture.

## Path Resolution
Mobile app files will be created in a repository-relative project directory, automatically resolved from any working directory.

**Implementation Note:**
```python
# Import path resolution utilities
import sys
import os
sys.path.insert(0, os.path.expanduser('~/.claude'))
from system.utils import path_resolver

# Create project structure
project_name = "MyMobileApp"  # From user input
lib_dir = path_resolver.ensure_directory('lib')
project_root = lib_dir / project_name
project_root.mkdir(exist_ok=True)

# Create module directories
modules_dir = project_root / 'Modules'
(modules_dir / 'Authentication').mkdir(parents=True, exist_ok=True)
(modules_dir / 'Core').mkdir(parents=True, exist_ok=True)
(modules_dir / 'Infrastructure').mkdir(parents=True, exist_ok=True)
(project_root / 'Tests').mkdir(exist_ok=True)

# Define file paths
maui_program = project_root / 'MauiProgram.cs'
auth_module = modules_dir / 'Authentication' / 'AuthenticationModule.cs'

# After creating files, format output
output_paths = {
    "Project created": project_root,
    "MauiProgram.cs": maui_program,
    "Authentication module": auth_module,
    "Modules directory": modules_dir
}
print(path_resolver.format_output_message(output_paths))
```

**Important**: Never hardcode paths. Always use the path resolver to ensure the mobile app is created in the correct repository-relative location.

## Steps:

1. Create the Prism MAUI project structure:
   - Generate MAUI project with Prism.DryIoc template
   - Remove MAUI Shell references (not using Shell navigation)
   - Set up modular folder structure:
     - Core module (shared interfaces, models)
     - Infrastructure module (services, data access)
     - Feature modules (Login, Dashboard, Settings, etc.)

2. Configure Prism application:
   ```csharp
   // MauiProgram.cs - Configure Prism container
   builder.UsePrism(prism =>
   {
       prism.RegisterTypes(RegisterTypes)
            .ConfigureModuleCatalog(ConfigureModuleCatalog)
            .OnInitialized(OnInitialized);
   });
   ```

3. Set up Prism modules:
   - Create IModule implementations for each feature
   - Register ViewModels and Views in each module
   - Configure module dependencies
   - Set up module initialization

4. Implement Prism navigation:
   - Use INavigationService for all navigation
   - Set up deep linking with Prism navigation
   - Configure navigation parameters passing
   - Implement INavigationAware on ViewModels

5. Create base classes:
   - BaseViewModel inheriting from BindableBase
   - Implement INavigationAware, IDestructible
   - Common navigation methods
   - Error handling and busy state management

6. Set up dependency injection:
   - Register services in MauiProgram
   - Use constructor injection in ViewModels
   - Register platform-specific services
   - Configure service lifetimes appropriately

7. Configure Prism regions (if needed):
   - Set up region adapters
   - Define region names
   - Implement region navigation

8. Data and service layer:
   - Repository pattern with interfaces
   - API services using Refit
   - Local database with SQLite
   - Implement IPageDialogService for dialogs

9. Essential Prism packages:
   - Prism.DryIoc.Maui
   - Prism.Plugin.Popups (for popup navigation)
   - DryIoc.Microsoft.DependencyInjection

10. Create sample modules:
    - Authentication module (Login, Register)
    - Main module (Dashboard, Home)
    - Settings module
    - About module

11. Module structure example:
    ```
    Modules/
    ├── Authentication/
    │   ├── Views/
    │   ├── ViewModels/
    │   ├── Services/
    │   └── AuthenticationModule.cs
    ├── Main/
    │   ├── Views/
    │   ├── ViewModels/
    │   ├── Services/
    │   └── MainModule.cs
    ```

12. Navigation examples:
    ```csharp
    // Navigate with parameters
    await _navigationService.NavigateAsync("MainPage", 
        new NavigationParameters { { "userId", userId } });
    
    // Modal navigation
    await _navigationService.NavigateAsync("LoginPage", useModalNavigation: true);
    
    // Deep linking
    await _navigationService.NavigateAsync("/MainPage/DetailPage?id=123");
    ```

Remember to:
- Use Prism's EventAggregator for module communication
- Implement IActiveAware for active view tracking
- Use Prism behaviors for view logic
- Follow Prism naming conventions (ViewNamePage, ViewNamePageViewModel)
- Register all navigation paths in App.xaml.cs