#!/usr/bin/env python3
"""
Script to add UUID validation to Phase 2 routes that are missing it.
"""

import os
import re
from pathlib import Path

def add_uuid_validation_to_route_function(content: str, function_name: str, param_name: str) -> str:
    """Add UUID validation to a specific route function."""
    # Pattern to find the function definition
    pattern = rf'(async def {function_name}\([^)]*{param_name}: str[^)]*\):\s*\n)(\s*"""[^"]*"""\s*\n)?(\s*if not tenant_context\.restaurant_id:)'
    
    def replace_func(match):
        func_def = match.group(1)
        docstring = match.group(2) or ""
        validation_line = match.group(3)
        
        # Extract indentation from the validation line
        indent = re.match(r'\s*', validation_line).group()
        
        # Add UUID validation
        uuid_validation = f'{indent}# Validate UUID format\n{indent}validate_uuid({param_name}, "{param_name} ID")\n{indent}\n'
        
        return func_def + docstring + uuid_validation + validation_line
    
    return re.sub(pattern, replace_func, content)

def add_uuid_import_and_function(content: str) -> str:
    """Add UUID import and validation function to a file."""
    # Check if uuid import already exists
    if 'import uuid' in content:
        return content
        
    # Add uuid import after existing imports
    import_pattern = r'(from app\.shared\.auth\.deps import[^\n]*\n)'
    if re.search(import_pattern, content):
        content = re.sub(import_pattern, r'\1import uuid\n', content)
    
    # Check if validation function already exists
    if 'def validate_uuid(' in content:
        return content
    
    # Add validation function after router definition
    router_pattern = r'(router = APIRouter\([^)]*\)\n)'
    validation_function = '''

def validate_uuid(uuid_string: str, field_name: str = "ID") -> str:
    """Validate UUID format and return the string."""
    try:
        uuid.UUID(uuid_string)
        return uuid_string
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format"
        )
'''
    
    if re.search(router_pattern, content):
        content = re.sub(router_pattern, r'\1' + validation_function, content)
    
    return content

def process_file(file_path: Path):
    """Process a single route file to add UUID validation."""
    print(f"Processing {file_path.name}...")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Add import and validation function
    content = add_uuid_import_and_function(content)
    
    # Define routes and their parameter names that need validation
    routes_to_fix = []
    
    if 'reservations.py' in str(file_path):
        routes_to_fix = [
            ('update_reservation', 'reservation_id'),
            ('cancel_reservation', 'reservation_id'),
            ('checkin_reservation', 'reservation_id'),
            ('assign_table_to_reservation', 'reservation_id'),
            ('mark_reservation_no_show', 'reservation_id'),
        ]
    elif 'waitlist.py' in str(file_path):
        routes_to_fix = [
            ('get_waitlist_entry', 'waitlist_id'),
            ('update_waitlist_entry', 'waitlist_id'),
            ('remove_from_waitlist', 'waitlist_id'),
            ('notify_waitlist_customer', 'waitlist_id'),
            ('mark_waitlist_seated', 'waitlist_id'),
        ]
    elif 'public.py' in str(file_path):
        routes_to_fix = [
            ('get_public_availability', 'restaurant_id'),
            ('create_public_reservation', 'restaurant_id'),
            ('join_public_waitlist', 'restaurant_id'),
            ('get_public_reservation_status', 'restaurant_id'),
            ('cancel_public_reservation', 'restaurant_id'),
            ('cancel_public_reservation', 'reservation_id'),
            ('get_public_waitlist_status', 'restaurant_id'),
            ('get_public_restaurant_info', 'restaurant_id'),
        ]
    
    # Apply validation to each route
    for func_name, param_name in routes_to_fix:
        content = add_uuid_validation_to_route_function(content, func_name, param_name)
    
    # Write back if changed
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"  ✅ Updated {file_path.name}")
    else:
        print(f"  ⏭️  No changes needed for {file_path.name}")

def main():
    """Main function to process all route files."""
    base_path = Path("/Users/bi_sapkota/personal_projects/rms/app/modules/tables/routes")
    
    files_to_process = [
        base_path / "reservations.py",
        base_path / "waitlist.py", 
        base_path / "public.py"
    ]
    
    print("🔧 Adding UUID validation to Phase 2 routes...")
    
    for file_path in files_to_process:
        if file_path.exists():
            process_file(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    
    print("✅ UUID validation update complete!")

if __name__ == "__main__":
    main()