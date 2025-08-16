#!/usr/bin/env python3
"""
Generate All Test Data

Orchestrates the generation of all test data for RMS API testing.
Runs all generators in the proper sequence: organizations → restaurants → users → menu data.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient


class ComprehensiveDataGenerator:
    """Orchestrates generation of all test data"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.generation_results = {}
        
    def print_header(self, title: str, emoji: str = "🏗️"):
        """Print formatted section header"""
        print(f"\n{'=' * 60}")
        print(f"{emoji}  {title}")
        print(f"{'=' * 60}")
        
    def print_step(self, step: str, status: str = "RUNNING"):
        """Print generation step with status"""
        status_icons = {
            "RUNNING": "🔄",
            "SUCCESS": "✅",
            "FAILED": "❌",
            "SKIPPED": "⏭️"
        }
        icon = status_icons.get(status, "🔄")
        print(f"{icon} {step}")
        
    async def check_api_health(self) -> bool:
        """Check if API is available before starting generation"""
        
        self.print_step("Checking API availability", "RUNNING")
        
        try:
            async with APITestClient(self.base_url) as client:
                response = await client.get("/health")
                if response.status_code == 200:
                    self.print_step("API is available and healthy", "SUCCESS")
                    return True
                else:
                    self.print_step(f"API health check failed: HTTP {response.status_code}", "FAILED")
                    return False
                    
        except Exception as e:
            self.print_step(f"Cannot connect to API: {e}", "FAILED")
            return False
            
    async def run_generator_script(self, script_name: str, description: str) -> bool:
        """Run a generator script and capture results"""
        
        script_path = Path(__file__).parent / script_name
        
        if not script_path.exists():
            self.print_step(f"{description} - Script not found", "FAILED")
            return False
            
        self.print_step(f"{description}", "RUNNING")
        
        try:\n            import subprocess\n            \n            # Run the generator script\n            start_time = time.time()\n            result = subprocess.run(\n                [sys.executable, str(script_path)],\n                capture_output=True,\n                text=True,\n                cwd=project_root\n            )\n            \n            execution_time = time.time() - start_time\n            \n            if result.returncode == 0:\n                self.print_step(f\"{description} completed ({execution_time:.1f}s)\", \"SUCCESS\")\n                \n                # Store results\n                self.generation_results[script_name] = {\n                    \"success\": True,\n                    \"execution_time\": execution_time,\n                    \"stdout\": result.stdout,\n                    \"stderr\": result.stderr\n                }\n                \n                # Print key output lines\n                output_lines = result.stdout.split('\\n')\n                success_lines = [line for line in output_lines if '✅' in line or 'Successfully generated' in line]\n                for line in success_lines[-3:]:  # Show last 3 success lines\n                    if line.strip():\n                        print(f\"   {line.strip()}\")\n                        \n                return True\n                \n            else:\n                self.print_step(f\"{description} failed\", \"FAILED\")\n                \n                # Store failure results\n                self.generation_results[script_name] = {\n                    \"success\": False,\n                    \"execution_time\": execution_time,\n                    \"stdout\": result.stdout,\n                    \"stderr\": result.stderr,\n                    \"return_code\": result.returncode\n                }\n                \n                # Print error details\n                if result.stderr:\n                    print(f\"   Error: {result.stderr.strip()}\")\n                    \n                return False\n                \n        except Exception as e:\n            self.print_step(f\"{description} error: {e}\", \"FAILED\")\n            \n            self.generation_results[script_name] = {\n                \"success\": False,\n                \"execution_time\": 0,\n                \"error\": str(e)\n            }\n            \n            return False\n            \n    async def run_all_generators(self, skip_organizations: bool = False) -> dict:\n        \"\"\"Run all data generators in sequence\"\"\"\n        \n        generators = [\n            (\"generate_organizations.py\", \"Generating Organizations\", skip_organizations),\n            (\"generate_restaurants.py\", \"Generating Restaurants\", False),\n            (\"generate_users.py\", \"Generating Users\", False),\n            (\"generate_menu_data.py\", \"Generating Menu Data\", False)\n        ]\n        \n        results = {}\n        overall_success = True\n        \n        for script_name, description, skip in generators:\n            if skip:\n                self.print_step(f\"{description} - Skipped (organizations auto-created)\", \"SKIPPED\")\n                results[script_name] = {\"success\": True, \"skipped\": True}\n                continue\n                \n            success = await self.run_generator_script(script_name, description)\n            results[script_name] = success\n            \n            if not success:\n                overall_success = False\n                print(f\"⚠️  {description} failed, but continuing with other generators...\")\n                \n            # Add delay between generators\n            await asyncio.sleep(2)\n            \n        return results\n        \n    def print_generation_summary(self, results: dict):\n        \"\"\"Print comprehensive generation summary\"\"\"\n        \n        self.print_header(\"Data Generation Summary\", \"📊\")\n        \n        total_generators = len(results)\n        successful_generators = sum(1 for success in results.values() if success)\n        \n        print(f\"\\n🎯 Overall Results:\")\n        print(f\"   Total Generators: {total_generators}\")\n        print(f\"   Successful: {successful_generators}\")\n        print(f\"   Failed: {total_generators - successful_generators}\")\n        print(f\"   Success Rate: {(successful_generators/total_generators)*100:.1f}%\")\n        \n        print(f\"\\n📋 Generator Details:\")\n        \n        generator_names = {\n            \"generate_organizations.py\": \"Organizations\",\n            \"generate_restaurants.py\": \"Restaurants\", \n            \"generate_users.py\": \"Users\",\n            \"generate_menu_data.py\": \"Menu Data\"\n        }\n        \n        for script_name, success in results.items():\n            name = generator_names.get(script_name, script_name)\n            \n            if script_name in self.generation_results:\n                result_data = self.generation_results[script_name]\n                \n                if result_data.get(\"skipped\"):\n                    print(f\"   ⏭️  {name}: Skipped\")\n                elif result_data[\"success\"]:\n                    exec_time = result_data[\"execution_time\"]\n                    print(f\"   ✅ {name}: Success ({exec_time:.1f}s)\")\n                else:\n                    exec_time = result_data.get(\"execution_time\", 0)\n                    print(f\"   ❌ {name}: Failed ({exec_time:.1f}s)\")\n            else:\n                status = \"Success\" if success else \"Failed\"\n                print(f\"   {'✅' if success else '❌'} {name}: {status}\")\n                \n        # Print next steps\n        if successful_generators > 0:\n            print(f\"\\n🚀 Next Steps:\")\n            print(f\"   • Run comprehensive API tests: python run_comprehensive_tests.py full\")\n            print(f\"   • Test individual operations: python run_comprehensive_tests.py read\")\n            print(f\"   • Verify data in API documentation: http://localhost:8000/docs\")\n        else:\n            print(f\"\\n❌ Data generation failed. Check API server and try again.\")\n            \n    async def cleanup_generated_files(self):\n        \"\"\"Clean up generated JSON files\"\"\"\n        \n        generated_files = [\n            \"generated_organizations.json\",\n            \"generated_restaurants.json\",\n            \"generated_users.json\", \n            \"generated_menus.json\"\n        ]\n        \n        print(f\"\\n🧹 Cleaning up generated files...\")\n        \n        for filename in generated_files:\n            file_path = Path(__file__).parent / filename\n            if file_path.exists():\n                try:\n                    file_path.unlink()\n                    print(f\"   🗑️  Removed: {filename}\")\n                except Exception as e:\n                    print(f\"   ❌ Failed to remove {filename}: {e}\")\n                    \n    async def run_comprehensive_generation(self, skip_organizations: bool = True):\n        \"\"\"Run the complete data generation process\"\"\"\n        \n        start_time = time.time()\n        \n        self.print_header(\"RMS Comprehensive Test Data Generation\", \"🏗️\")\n        \n        print(f\"Target API: {self.base_url}\")\n        print(f\"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\")\n        \n        try:\n            # Check API health first\n            if not await self.check_api_health():\n                print(f\"\\n❌ API is not available. Please start the RMS API server first:\")\n                print(f\"   uv run uvicorn app.main:app --reload --port 8000\")\n                return False\n                \n            # Run all generators\n            results = await self.run_all_generators(skip_organizations)\n            \n            # Print summary\n            total_time = time.time() - start_time\n            print(f\"\\n⏱️  Total Generation Time: {total_time:.2f} seconds\")\n            \n            self.print_generation_summary(results)\n            \n            # Return overall success\n            return sum(results.values()) > 0\n            \n        except KeyboardInterrupt:\n            print(f\"\\n⚠️  Generation interrupted by user\")\n            return False\n        except Exception as e:\n            print(f\"\\n❌ Generation process failed: {e}\")\n            return False\n\n\nasync def main():\n    \"\"\"Main entry point for comprehensive data generation\"\"\"\n    \n    import argparse\n    \n    parser = argparse.ArgumentParser(description=\"Generate all RMS test data\")\n    parser.add_argument(\"--base-url\", default=\"http://localhost:8000\", help=\"API base URL\")\n    parser.add_argument(\"--include-organizations\", action=\"store_true\", \n                       help=\"Include organization generation (usually auto-created)\")\n    parser.add_argument(\"--cleanup\", action=\"store_true\", \n                       help=\"Clean up generated JSON files after completion\")\n    \n    args = parser.parse_args()\n    \n    generator = ComprehensiveDataGenerator(args.base_url)\n    \n    try:\n        # Run comprehensive generation\n        success = await generator.run_comprehensive_generation(\n            skip_organizations=not args.include_organizations\n        )\n        \n        # Optional cleanup\n        if args.cleanup:\n            await generator.cleanup_generated_files()\n            \n        if success:\n            print(f\"\\n🎉 Data generation completed successfully!\")\n            print(f\"\\n💡 Try running comprehensive tests:\")\n            print(f\"   cd tests/api_tester\")\n            print(f\"   python run_comprehensive_tests.py full\")\n        else:\n            print(f\"\\n💥 Data generation completed with errors\")\n            sys.exit(1)\n            \n    except Exception as e:\n        print(f\"❌ Fatal error: {e}\")\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    asyncio.run(main())"