"""
Phase file parser for extracting metadata and dependencies.

This module parses phase markdown files to extract phase metadata,
dependencies, file references, and expected outputs.
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from models.parallel_execution import PhaseInfo


@dataclass
class ParsedPhaseData:
    """Raw parsed data from a phase file."""
    phase_id: str
    name: str
    dependencies: List[str]
    outputs: List[str]
    file_references: List[str]
    estimated_time: float
    description: str
    raw_content: str


class PhaseParser:
    """Parser for PRD phase markdown files."""
    
    # Regex patterns for extracting metadata
    PHASE_ID_PATTERN = re.compile(r'^#\s*Phase\s+(\d+)', re.MULTILINE | re.IGNORECASE)
    PHASE_NAME_PATTERN = re.compile(r'^#\s*Phase\s+\d+:\s*(.+)$', re.MULTILINE | re.IGNORECASE)
    DEPENDENCIES_PATTERN = re.compile(r'^##\s*Dependencies?:\s*(.+)$', re.MULTILINE | re.IGNORECASE)
    TIME_PATTERN = re.compile(r'(?:Estimated\s+)?Time:\s*([\d.]+)\s*(?:hours?)?', re.IGNORECASE)
    OUTPUTS_PATTERN = re.compile(r'^##\s*(?:Expected\s+)?Outputs?:?\s*$', re.MULTILINE | re.IGNORECASE)
    FILE_PATH_PATTERN = re.compile(r'[`"\']?(/[\w\-./]+\.\w+)[`"\']?')
    CODE_BLOCK_PATTERN = re.compile(r'```[\w]*\n(.*?)\n```', re.DOTALL)
    
    def __init__(self):
        """Initialize the phase parser."""
        self._cache: Dict[str, ParsedPhaseData] = {}
    
    def parse_phase_file(self, filepath: str) -> PhaseInfo:
        """
        Parse a phase markdown file and extract metadata.
        
        Args:
            filepath: Path to the phase markdown file
            
        Returns:
            PhaseInfo object with extracted metadata
            
        Raises:
            ValueError: If required metadata is missing or invalid
            FileNotFoundError: If the file doesn't exist
        """
        filepath = str(Path(filepath).resolve())
        
        # Check cache first
        if filepath in self._cache:
            parsed = self._cache[filepath]
            return self._create_phase_info(parsed)
        
        # Read file content
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Phase file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the content
        parsed = self._parse_content(content, filepath)
        
        # Cache the result
        self._cache[filepath] = parsed
        
        return self._create_phase_info(parsed)
    
    def _parse_content(self, content: str, filepath: str) -> ParsedPhaseData:
        """Parse the markdown content to extract metadata."""
        # Extract phase ID
        phase_id = self._extract_phase_id(content, filepath)
        
        # Extract phase name
        name = self._extract_phase_name(content, phase_id)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(content)
        
        # Extract estimated time
        estimated_time = self._extract_time(content)
        
        # Extract file references
        file_references = self._extract_file_references(content)
        
        # Extract expected outputs
        outputs = self._extract_outputs(content)
        
        # Extract description (first paragraph after title)
        description = self._extract_description(content)
        
        return ParsedPhaseData(
            phase_id=phase_id,
            name=name,
            dependencies=dependencies,
            outputs=outputs,
            file_references=file_references,
            estimated_time=estimated_time,
            description=description,
            raw_content=content
        )
    
    def _extract_phase_id(self, content: str, filepath: str) -> str:
        """Extract phase ID from content or filename."""
        # Try to extract from content
        match = self.PHASE_ID_PATTERN.search(content)
        if match:
            return f"phase-{match.group(1)}"
        
        # Fallback to filename
        filename = Path(filepath).stem
        if filename.startswith('phase-'):
            return filename
        
        # Generate from filename
        return f"phase-{filename}"
    
    def _extract_phase_name(self, content: str, phase_id: str) -> str:
        """Extract human-readable phase name."""
        match = self.PHASE_NAME_PATTERN.search(content)
        if match:
            return match.group(1).strip()
        
        # Fallback to phase ID
        return phase_id.replace('-', ' ').title()
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract phase dependencies."""
        match = self.DEPENDENCIES_PATTERN.search(content)
        if not match:
            return []
        
        deps_text = match.group(1).strip()
        
        # Handle "None" or similar
        if deps_text.lower() in ['none', 'n/a', '-', '']:
            return []
        
        # Parse comma-separated list
        dependencies = []
        for dep in deps_text.split(','):
            dep = dep.strip()
            # Extract phase references (e.g., "Phase 1", "phase-1")
            phase_match = re.search(r'phase[-\s]?(\d+)', dep, re.IGNORECASE)
            if phase_match:
                dependencies.append(f"phase-{phase_match.group(1)}")
            elif dep and not dep.lower() in ['none', 'n/a']:
                # Keep as-is if it's already a valid phase ID
                dependencies.append(dep)
        
        return dependencies
    
    def _extract_time(self, content: str) -> float:
        """Extract estimated time in hours."""
        match = self.TIME_PATTERN.search(content)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        
        # Default to 1 hour
        return 1.0
    
    def _extract_file_references(self, content: str) -> List[str]:
        """Extract all file paths mentioned in the content."""
        file_refs = set()
        
        # Extract from code blocks
        code_blocks = self.CODE_BLOCK_PATTERN.findall(content)
        for block in code_blocks:
            # Look for file paths in code
            paths = self.FILE_PATH_PATTERN.findall(block)
            file_refs.update(paths)
        
        # Extract from regular text
        # Remove code blocks first
        text_content = self.CODE_BLOCK_PATTERN.sub('', content)
        paths = self.FILE_PATH_PATTERN.findall(text_content)
        file_refs.update(paths)
        
        # Filter and normalize paths
        normalized = []
        for path in file_refs:
            # Skip URLs and non-file paths
            if path.startswith('/') and '.' in path:
                # Normalize the path
                normalized.append(path)
        
        return sorted(normalized)
    
    def _extract_outputs(self, content: str) -> List[str]:
        """Extract expected output files."""
        outputs = []
        
        # Find outputs section
        match = self.OUTPUTS_PATTERN.search(content)
        if not match:
            # Fallback: look for file references that might be outputs
            return self._infer_outputs_from_content(content)
        
        # Extract content after outputs header
        start_pos = match.end()
        # Find next section header
        next_section = re.search(r'^##\s', content[start_pos:], re.MULTILINE)
        if next_section:
            outputs_text = content[start_pos:start_pos + next_section.start()]
        else:
            outputs_text = content[start_pos:]
        
        # Parse list items
        list_items = re.findall(r'^\s*[-*]\s*(.+)$', outputs_text, re.MULTILINE)
        for item in list_items:
            # Extract file paths from item
            paths = self.FILE_PATH_PATTERN.findall(item)
            outputs.extend(paths)
            
            # Also check for descriptive paths
            if '.py' in item or '.md' in item or '.yaml' in item:
                # Try to extract a path-like string
                path_match = re.search(r'[/\w\-]+\.\w+', item)
                if path_match:
                    outputs.append(path_match.group(0))
        
        return sorted(set(outputs))
    
    def _infer_outputs_from_content(self, content: str) -> List[str]:
        """Infer output files from content when no explicit outputs section."""
        outputs = []
        
        # Look for "will create", "generates", "produces" patterns
        create_patterns = [
            r'(?:will\s+)?create[sd]?\s+[`"\']?([/\w\-./]+\.\w+)[`"\']?',
            r'generat(?:e[sd]?|ing)\s+[`"\']?([/\w\-./]+\.\w+)[`"\']?',
            r'produc(?:e[sd]?|ing)\s+[`"\']?([/\w\-./]+\.\w+)[`"\']?',
            r'(?:Files?\s+to\s+Create|Expected\s+Files?).*?([/\w\-./]+\.\w+)',
        ]
        
        for pattern in create_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            outputs.extend(matches)
        
        return sorted(set(outputs))
    
    def _extract_description(self, content: str) -> str:
        """Extract phase description from content."""
        # Remove title
        content_lines = content.split('\n')
        
        # Skip title and find first paragraph
        in_paragraph = False
        description_lines = []
        
        for line in content_lines:
            # Skip headers
            if line.strip().startswith('#'):
                if in_paragraph:
                    break
                continue
            
            # Skip empty lines before content
            if not in_paragraph and not line.strip():
                continue
            
            # Start collecting description
            if line.strip() and not in_paragraph:
                in_paragraph = True
            
            if in_paragraph:
                if not line.strip() and description_lines:
                    # End of first paragraph
                    break
                if line.strip():
                    description_lines.append(line.strip())
        
        description = ' '.join(description_lines)
        
        # Truncate if too long
        if len(description) > 200:
            description = description[:197] + '...'
        
        return description
    
    def _create_phase_info(self, parsed: ParsedPhaseData) -> PhaseInfo:
        """Create PhaseInfo object from parsed data."""
        return PhaseInfo(
            id=parsed.phase_id,
            name=parsed.name,
            dependencies=parsed.dependencies,
            outputs=parsed.outputs,
            estimated_time=parsed.estimated_time,
            description=parsed.description
        )
    
    def extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from phase content."""
        return self._extract_dependencies(content)
    
    def extract_file_references(self, content: str) -> List[str]:
        """Extract file references from phase content."""
        return self._extract_file_references(content)