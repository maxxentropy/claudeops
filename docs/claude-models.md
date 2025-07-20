# Claude Model Reference Guide

## Current Claude Models (as of January 2025)

### Claude 4 Family (Released May 2025)

#### Claude Opus 4
- **Model ID**: `claude-opus-4-20250514`
- **Alias**: `claude-opus-4-0`
- **Pricing**: $15 input / $75 output per million tokens
- **Key Features**:
  - Most capable model
  - Best coding model (72.5% on SWE-bench, 43.2% on Terminal-bench)
  - Sustained performance on long-running tasks
  - Can work continuously for several hours
  - Extended thinking capability (beta)

#### Claude Sonnet 4
- **Model ID**: `claude-sonnet-4-20250514`
- **Alias**: `claude-sonnet-4-0`
- **Pricing**: $3 input / $15 output per million tokens
- **Key Features**:
  - Balanced capability and performance
  - Powers GitHub Copilot coding agent
  - Available to free users
  - Extended thinking capability (beta)

### Claude 3.7 Family

#### Claude Sonnet 3.7
- **Model ID**: `claude-3-7-sonnet-20250219`
- **Latest enhancement of the 3.x line**
- **Improved reasoning capabilities**

### Claude 3.5 Family

#### Claude Sonnet 3.5
- **Model ID**: `claude-3-5-sonnet-20241022`
- **Fast and very capable**
- **Good balance of speed and performance**

#### Claude Haiku 3.5
- **Model ID**: `claude-3-5-haiku-20241022`
- **Fastest and most efficient**
- **Best for high-volume, simple tasks**

## Configuration Examples

### Claude Code Settings
```json
{
  "model": "claude-opus-4-20250514"  // For maximum capability
}
```

### Environment Variables
```bash
# macOS/Linux
export CLAUDE_MODEL="claude-opus-4-20250514"

# Windows PowerShell
[Environment]::SetEnvironmentVariable("CLAUDE_MODEL", "claude-opus-4-20250514", "User")
```

## Model Selection Guide

### Use Claude Opus 4 when:
- Working on complex coding tasks
- Need sustained multi-hour work sessions
- Require the highest reasoning capability
- Building sophisticated applications
- Performance is more important than cost

### Use Claude Sonnet 4 when:
- Need a balance of capability and cost
- Working on general development tasks
- Want access to extended thinking
- Budget is a consideration

### Use Claude 3.5 Sonnet when:
- Need fast responses
- Working on well-defined tasks
- Want proven stability

### Use Claude 3.5 Haiku when:
- Processing high volumes
- Simple, repetitive tasks
- Cost optimization is critical
- Speed is paramount

## Extended Thinking (Beta)

For Claude 4 models, you can enable extended thinking:

### API Header
```
interleaved-thinking-2025-05-14
```

This provides:
- Deeper reasoning on complex problems
- Step-by-step thought process visibility
- Better handling of multi-step tasks

## Migration Notes

### From Claude 3 to Claude 4
- API calls work without modification
- New refusal stop reason for safety
- Text editor tool updates
- Extended thinking capability added
- Cache prompts up to 1 hour

### Model Naming Convention
- Format: `claude-[family]-[version]-[date]`
- Example: `claude-opus-4-20250514`
- Snapshot dates ensure consistency across platforms

## Best Practices

1. **Always specify exact model versions** in production
2. **Test model changes** in development first
3. **Monitor costs** when using Opus models
4. **Use aliases** (`-0` suffix) for latest stable version
5. **Enable extended thinking** for complex reasoning tasks

## Quick Reference

```yaml
# Most Capable
claude-opus-4-20250514

# Best Balance
claude-sonnet-4-20250514

# Fast & Capable
claude-3-5-sonnet-20241022

# Fastest
claude-3-5-haiku-20241022
```