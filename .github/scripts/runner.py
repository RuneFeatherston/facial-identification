#!/usr/bin/env python3
"""
Integration test runner for GitHub Actions.

Handles Docker Compose orchestration, service health checking,
and proper cleanup for integration testing.
"""

import subprocess
import time
import requests
import sys
import os
from contextlib import contextmanager
from pathlib import Path
import structlog

# Load environment variables from .env file (scripts directory first, then root)
try:
    from dotenv import load_dotenv
    # Try to load from scripts directory first
    scripts_env = Path(__file__).parent / '.env'
    if scripts_env.exists():
        load_dotenv(scripts_env)
    else:
        # Fallback to root directory
        load_dotenv()
except ImportError:
    # dotenv not installed - just use environment variables
    pass

# Configure structured logging with proper level filtering
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
    # Set log level based on context
)

# Set up logger with appropriate level
import logging
logging.basicConfig(level=logging.INFO)  # Default to INFO level
logger = structlog.get_logger(__name__)


class IntegrationRunner:
    """Orchestrates integration testing with Docker Compose."""
    
    def __init__(self, context='ci'):
        """Initialize runner with context-specific settings.
        
        Args:
            context: 'ci' for GitHub Actions, 'local' for developer machines
        """
        self.context = context
        
        # Load configuration from environment variables with defaults
        self.gateway_url = os.getenv('GATEWAY_BASE_URL', 'http://localhost:8080')
        self.ml_url = os.getenv('ML_BASE_URL', 'http://localhost:8000')
        self.health_timeout = int(os.getenv('HEALTH_CHECK_TIMEOUT', '120'))
        self.health_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '2'))
        
        self.services = {
            'gateway': {
                'url': f"{self.gateway_url}/health",
                'name': 'gateway-service'
            },
            'ml': {
                'url': f"{self.ml_url}/health", 
                'name': 'ml-service'
            }
        }
        
        # Context-specific configuration
        if context == 'ci':
            self.logs_dir = Path('logs')
            self.verbose_on_success = False
            self.cleanup_aggressive = True
        else:  # local
            self.logs_dir = Path('.integration-logs')
            self.verbose_on_success = True  # Show more info locally
            self.cleanup_aggressive = False  # Keep containers for debugging
        
        logger.info(f"🎯 Integration runner initialized for {context} context")
        # Log configuration
        logger.info(f"🔧 Gateway URL: {self.gateway_url}")
        logger.info(f"🔧 ML URL: {self.ml_url}")
    
    def run_command_with_logging(self, cmd, description):
        """Run command with context-aware output - CI vs local behavior."""
        logger.info(f"🔧 {description}...")
        
        # Run command and capture all output
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Success handling depends on context
            if self.context == 'local' and self.verbose_on_success:
                # Local: Show some output for transparency
                logger.info(f"✅ {description} completed successfully")
                if result.stdout.strip():
                    # Show last few lines of output locally
                    stdout_lines = result.stdout.strip().split('\n')
                    if len(stdout_lines) > 3:
                        logger.info(f"Last few lines: ...{stdout_lines[-2]}")
                        logger.info(f"                {stdout_lines[-1]}")
            else:
                # CI: Clean output only
                logger.info(f"✅ {description} completed successfully")
        else:
            # Failure: Always log everything for debugging
            self.logs_dir.mkdir(exist_ok=True)
            log_file = self.logs_dir / f"{description.lower().replace(' ', '_')}_failure.log"
            
            # Write comprehensive failure log
            with open(log_file, 'w') as f:
                f.write(f"=== FAILURE LOG: {description} ===\n")
                f.write(f"Context: {self.context}\n")
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write(f"Exit Code: {result.returncode}\n")
                f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"STDOUT:\n{result.stdout}\n\n")
                f.write(f"STDERR:\n{result.stderr}\n")
            
            # Show failure in console + point to detailed log
            logger.error(f"❌ {description} failed (exit code: {result.returncode})")
            logger.error(f"Full debugging info saved to: {log_file}")
            
            # Show preview of error for immediate context
            if result.stderr.strip():
                preview = result.stderr.strip()[:300]
                logger.error(f"Error preview: {preview}{'...' if len(result.stderr) > 300 else ''}")
        
        return result
    
    def run(self):
        """Main entry point for integration testing."""
        logger.info("🚀 Starting integration test runner")
        
        try:
            with self.docker_services():
                return self.run_api_tests()
        except Exception as e:
            logger.error(f"❌ Integration testing failed: {e}")
            return 1
    
    @contextmanager
    def docker_services(self):
        """Context manager for Docker Compose lifecycle."""
        try:
            self.start_services()
            self.wait_for_health()
            logger.info("✅ All services ready for testing")
            yield
        except Exception as e:
            logger.error(f"❌ Service startup failed: {e}")
            self.collect_failure_logs()
            raise
        finally:
            self.cleanup_services()
    
    def start_services(self):
        """Start services with Docker Compose."""
        cmd = ['docker-compose']
        
        # Add custom compose file if specified
        docker_compose_file = os.getenv('DOCKER_COMPOSE_FILE', 'docker-compose.yml')
        if docker_compose_file != 'docker-compose.yml':
            cmd.extend(['-f', docker_compose_file])
        
        # Add up command with build args
        cmd.extend(['up', '-d'])
        docker_build_args = os.getenv('DOCKER_BUILD_ARGS', '')
        if '--build' in docker_build_args:
            cmd.append('--build')
        
        result = self.run_command_with_logging(
            cmd,
            "Starting services with Docker Compose"
        )
        
        if result.returncode != 0:
            raise RuntimeError("Docker Compose startup failed")
    
    def wait_for_health(self, timeout=None):
        """Wait for all services to become healthy."""
        if timeout is None:
            timeout = int(os.getenv('HEALTH_CHECK_TIMEOUT', '120'))
            
        logger.info(f"⏳ Waiting for services to be ready (timeout: {timeout}s)...")
        
        for service_name, config in self.services.items():
            self._wait_for_service_health(service_name, config, timeout)
    
    def _wait_for_service_health(self, service_name, config, timeout):
        """Wait for a specific service to become healthy."""
        start_time = time.time()
        url = config['url']
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ {service_name} is healthy")
                    return
            except requests.RequestException as e:
                logger.debug(f"Waiting for {service_name}: {e}")
                
            time.sleep(2)
        
        # Timeout reached
        logger.error(f"❌ {service_name} failed to become healthy within {timeout}s")
        raise TimeoutError(f"{service_name} health check timeout")
    
    def run_api_tests(self):
        """Run the actual API integration tests."""
        env = os.environ.copy()
        env.update({
            'GATEWAY_BASE_URL': 'http://localhost:8080',
            'ML_BASE_URL': 'http://localhost:8000'
        })
        
        result = self.run_command_with_logging(
            ['make', 'test-api'],
            "Running API contract tests against live services"
        )
        
        return result.returncode
    
    def collect_failure_logs(self):
        """Collect service logs when failures occur."""
        logger.info("📋 Collecting service logs for debugging...")
        
        self.logs_dir.mkdir(exist_ok=True)
        
        # Collect individual service logs
        for service_name, config in self.services.items():
            log_file = self.logs_dir / f"{config['name']}.log"
            
            try:
                result = subprocess.run(
                    ['docker-compose', 'logs', config['name']],
                    capture_output=True,
                    text=True
                )
                
                with open(log_file, 'w') as f:
                    f.write(result.stdout)
                    
                logger.info(f"📋 Collected logs: {log_file}")
                
            except Exception as e:
                logger.warning(f"Failed to collect logs for {service_name}: {e}")
        
        # Collect all service logs
        try:
            result = subprocess.run(
                ['docker-compose', 'logs'],
                capture_output=True,
                text=True
            )
            
            with open(self.logs_dir / 'all-services.log', 'w') as f:
                f.write(result.stdout)
                
            logger.info("📋 Collected all service logs")
            
        except Exception as e:
            logger.warning(f"Failed to collect all service logs: {e}")
    
    def cleanup_services(self):
        """Clean up Docker resources with context-aware aggressiveness."""
        # Stop and remove containers
        self.run_command_with_logging(
            ['docker-compose', 'down', '-v', '--remove-orphans'],
            "Stopping and removing Docker containers"
        )
        
        if self.cleanup_aggressive:
            # CI: Aggressive cleanup to prevent resource leaks
            self.run_command_with_logging(
                ['docker', 'system', 'prune', '-f'],
                "Cleaning up unused Docker resources"
            )
        else:
            # Local: Gentler cleanup, keep images for faster rebuilds
            logger.info("🔧 Skipping Docker system prune in local context")
            logger.info("💡 Run 'docker system prune -f' manually if needed")


def run_service_tests(context='ci'):
    """Run service tests (build, lint, unit tests) without Docker."""
    logger.info("🚀 Starting service tests pipeline...")
    
    services = ['frontend', 'gateway-service', 'ml-service']
    failed_services = []
    
    # Step 1: Build all services
    logger.info("📦 Step 1/3: Building all services...")
    for service in services:
        logger.info(f"Building {service}...")
        result = subprocess.run(['make', '-C', service, 'build'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Build failed for {service}", 
                        stdout=result.stdout, stderr=result.stderr)
            failed_services.append(f"{service}:build")
        else:
            logger.info(f"✅ {service} built successfully")
    
    # Step 2: Lint all services  
    logger.info("🧹 Step 2/3: Linting all services...")
    for service in services:
        logger.info(f"Linting {service}...")
        result = subprocess.run(['make', '-C', service, 'lint'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Lint failed for {service}",
                        stdout=result.stdout, stderr=result.stderr)
            failed_services.append(f"{service}:lint")
        else:
            logger.info(f"✅ {service} passed lint checks")
    
    # Step 3: Test all services
    logger.info("🧪 Step 3/3: Running unit tests for all services...")
    for service in services:
        logger.info(f"Testing {service}...")
        result = subprocess.run(['make', '-C', service, 'test'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Tests failed for {service}",
                        stdout=result.stdout, stderr=result.stderr)
            failed_services.append(f"{service}:test")
        else:
            logger.info(f"✅ {service} tests passed")
    
    # Summary
    if failed_services:
        logger.error("❌ Service tests failed!", failed_operations=failed_services)
        return 1
    else:
        logger.info("🎉 All service tests completed successfully!")
        logger.info("✅ Build, lint, and unit tests passed for all services")
        return 0


def run_individual_operation(mode, context='local'):
    """Run individual operations (setup, build, test, lint, format, clean) for all services."""
    services = {
        'frontend': 'node',
        'gateway-service': 'go',
        'ml-service': 'python'
    }
    
    mode_info = {
        'setup': ('🔧', 'Setting up'),
        'build': ('📦', 'Building'),
        'test': ('🧪', 'Testing'),
        'lint': ('🧹', 'Linting'),
        'format': ('✨', 'Formatting'),
        'clean': ('🗑️', 'Cleaning')
    }
    
    # Map generic operations to language-specific targets
    target_mapping = {
        'setup': {'node': 'node-install', 'go': 'go-install', 'python': 'python-install-dev'},
        'build': {'node': 'node-build', 'go': 'go-build', 'python': None},  # Python doesn't need build
        'test': {'node': 'node-test', 'go': 'go-test', 'python': 'python-test'},
        'lint': {'node': 'node-lint', 'go': 'go-lint', 'python': 'python-lint-score'},
        'format': {'node': 'node-format', 'go': 'go-fmt', 'python': 'python-format'},
        'clean': {'node': 'node-clean', 'go': 'go-clean', 'python': 'python-clean'}
    }
    
    icon, action = mode_info.get(mode, ('🔧', f'Running {mode}'))
    logger.info(f"{icon} {action} all services...")
    
    failed_services = []
    
    # Special handling for setup
    if mode == 'setup':
        logger.info("Installing runner script dependencies...")
        result = subprocess.run(['pip', 'install', '-r', '.github/scripts/requirements.txt'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Failed to install runner dependencies", 
                        stdout=result.stdout, stderr=result.stderr)
            return 1
        else:
            logger.debug("Runner dependencies installed", stdout=result.stdout)
        
        logger.info("Setting up API test dependencies...")
        result = subprocess.run(['make', '-C', 'tests/api', 'setup'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Failed to setup API tests",
                        stdout=result.stdout, stderr=result.stderr)
            return 1
        else:
            logger.debug("API test dependencies setup completed", stdout=result.stdout)
    
    # Run operation for each service
    for service, language in services.items():
        logger.info(f"{action} {service}...")
        
        # Get the language-specific target
        target = target_mapping.get(mode, {}).get(language)
        if target is None:
            if mode == 'build' and language == 'python':
                logger.info(f"✅ {service} {mode} completed (no build step needed for Python)")
                continue
            else:
                logger.warning(f"No {mode} target defined for {service} ({language})")
                continue
            
        result = subprocess.run(['make', '-C', service, target],
                              capture_output=True, text=True)
            
        if result.returncode != 0:
            logger.error(f"{action} failed for {service}",
                        stdout=result.stdout, stderr=result.stderr)
            failed_services.append(service)
        else:
            logger.info(f"✅ {service} {mode} completed")
            # Log subprocess output at DEBUG level (hidden by default)
            logger.debug(f"{service} {mode} output", stdout=result.stdout, stderr=result.stderr)
    
    if failed_services:
        logger.error(f"❌ {action} failed for services!", failed_services=failed_services)
        return 1
    else:
        logger.info(f"🎉 {action} completed successfully for all services!")
        return 0


def run_service_target(service, target, context='local'):
    """Run specific target for specific service."""
    logger.info(f"🎯 Running {target} for {service}...")
    
    result = subprocess.run(['make', '-C', service, target],
                          capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"{target} failed for {service}",
                    stdout=result.stdout, stderr=result.stderr)
        return 1
    else:
        logger.info(f"✅ {service} {target} completed successfully")
        return 0


def run_api_tests(context='local'):
    """Run API tests using the tests/api Makefile."""
    logger.info("🧪 Running API contract tests...")
    
    result = subprocess.run(['make', '-C', 'tests/api', 'test'],
                          capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("API tests failed",
                    stdout=result.stdout, stderr=result.stderr)
        return 1
    else:
        logger.info("✅ API tests completed successfully")
        return 0


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test orchestrator and integration runner')
    parser.add_argument('--context', choices=['ci', 'local'], default='ci',
                       help='Execution context: ci (GitHub Actions) or local (developer)')
    parser.add_argument('--mode', choices=['integration', 'service-tests', 'pipeline', 'setup', 'build', 'test', 'lint', 'format', 'clean', 'test-api', 'service'], 
                       default='integration',
                       help='Mode: integration (Docker+API tests), service-tests (build+lint+unit), setup/build/test/lint/format/clean (individual operations)')
    parser.add_argument('--service', help='Service name for service-specific operations')
    parser.add_argument('--target', help='Target for service-specific operations')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose output (show subprocess logs)')
    
    args = parser.parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Verbose mode enabled - showing subprocess output")
    
    if args.mode == 'integration':
        runner = IntegrationRunner(context=args.context)
        exit_code = runner.run()
    elif args.mode in ['service-tests', 'pipeline']:
        exit_code = run_service_tests(args.context)
    elif args.mode in ['setup', 'build', 'test', 'lint', 'format', 'clean']:
        exit_code = run_individual_operation(args.mode, args.context)
    elif args.mode == 'service':
        if not args.service or not args.target:
            logger.error("Service mode requires --service and --target arguments")
            sys.exit(1)
        exit_code = run_service_target(args.service, args.target, args.context)
    elif args.mode == 'test-api':
        exit_code = run_api_tests(args.context)
    
    sys.exit(exit_code)
