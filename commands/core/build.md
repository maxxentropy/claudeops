# /build - Platform-Specific Build Commands

Embody this expert persona:
<!-- INCLUDE: system/personas.md#DEVOPS_ENGINEER -->

First, load build commands:
<!-- INCLUDE: system/principles.md#BUILD_PLATFORMS -->

Execute platform-specific builds:

1. **Identify Project Type**:
   - Check for .csproj (C#/.NET)
   - Check for package.json (Node.js)
   - Check for platform-specific markers

2. **Pre-Build Checks**:
   - Ensure dependencies are installed
   - Clean previous build artifacts if needed
   - Verify required SDKs/tools are available

3. **Execute Build**:
   - Use the appropriate command from BUILD_PLATFORMS
   - For mobile platforms, specify target device/emulator
   - Include any project-specific build flags

4. **Post-Build Verification**:
   - Check for build errors or warnings
   - Verify output in expected location
   - Run smoke test if applicable

5. **Platform-Specific Notes**:
   - **Android**: Ensure emulator is running or device connected
   - **iOS**: Mac required, check provisioning
   - **Windows**: Check target Windows version compatibility

Example usage: `/build android` or `/build production`