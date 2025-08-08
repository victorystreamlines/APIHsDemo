#!/usr/bin/env python3
"""Load testing script for User Management System API.

This script uses Locust to simulate multiple users interacting with the API
to test performance, scalability, and identify bottlenecks.

Usage:
    python scripts/load_test.py --users 100 --spawn-rate 10 --run-time 300s
    
Features:
- Simulates realistic user behavior
- Tests all CRUD operations
- Includes authentication flows
- Measures response times and error rates
- Generates detailed performance reports
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from typing import Any

from locust import HttpUser, between, events, task
from locust.env import Environment
from locust.log import setup_logging
from locust.stats import stats_printer, stats_writer


class UserManagementUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 5)  # Wait 1-5 seconds between requests
    
    def on_start(self):
        """Initialize user session."""
        self.auth_token = None
        self.user_ids = []
        self.login()
    
    def login(self):
        """Authenticate user to get JWT token."""
        credentials = random.choice([
            {"username": "admin", "password": "admin123"},
            {"username": "demo", "password": "demo123"},
            {"username": "user", "password": "user123"},
        ])
        
        with self.client.post(
            "/api/v1/auth/login",
            json=credentials,
            catch_response=True,
            name="Login"
        ) as response:
            if response.status_code == 200:
                self.auth_token = response.json()["access_token"]
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code}")
    
    @property
    def auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    @task(5)
    def list_users(self):
        """List users with pagination and search."""
        params = {
            "page": random.randint(1, 3),
            "limit": random.choice([10, 25, 50]),
            "sort_by": random.choice(["name", "email", "created_at"]),
            "sort_order": random.choice(["asc", "desc"]),
        }
        
        # Sometimes add search query
        if random.random() < 0.3:
            params["search"] = random.choice(["user", "test", "john", "admin"])
        
        with self.client.get(
            "/api/v1/users/",
            params=params,
            catch_response=True,
            name="List Users"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "items" in data:
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"List users failed: {response.status_code}")
    
    @task(2)
    def create_user(self):
        """Create a new user."""
        user_data = {
            "name": f"Test User {random.randint(1000, 9999)}",
            "email": f"test{random.randint(1000, 9999)}@example.com",
            "phone": f"+1{random.randint(1000000000, 9999999999)}",
        }
        
        with self.client.post(
            "/api/v1/users/",
            json=user_data,
            headers=self.auth_headers,
            catch_response=True,
            name="Create User"
        ) as response:
            if response.status_code == 201:
                data = response.json()
                if data.get("success") and "data" in data:
                    self.user_ids.append(data["data"]["id"])
                    response.success()
                else:
                    response.failure("Invalid response format")
            elif response.status_code == 409:
                # Email already exists - this is acceptable in load testing
                response.success()
            else:
                response.failure(f"Create user failed: {response.status_code}")
    
    @task(3)
    def get_user(self):
        """Get a specific user by ID."""
        if not self.user_ids:
            # Use a random ID if we don't have any created users
            user_id = random.randint(1, 100)
        else:
            user_id = random.choice(self.user_ids)
        
        with self.client.get(
            f"/api/v1/users/{user_id}",
            catch_response=True,
            name="Get User"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    response.success()
                else:
                    response.failure("Invalid response format")
            elif response.status_code == 404:
                # User not found - acceptable in load testing
                response.success()
            else:
                response.failure(f"Get user failed: {response.status_code}")
    
    @task(1)
    def update_user(self):
        """Update an existing user."""
        if not self.user_ids:
            return  # Skip if no users created
        
        user_id = random.choice(self.user_ids)
        update_data = {
            "name": f"Updated User {random.randint(1000, 9999)}",
        }
        
        with self.client.put(
            f"/api/v1/users/{user_id}",
            json=update_data,
            headers=self.auth_headers,
            catch_response=True,
            name="Update User"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Invalid response format")
            elif response.status_code == 404:
                response.success()  # User might have been deleted
            else:
                response.failure(f"Update user failed: {response.status_code}")
    
    @task(1)
    def delete_user(self):
        """Delete a user."""
        if not self.user_ids:
            return  # Skip if no users created
        
        user_id = self.user_ids.pop(0)  # Remove from our list
        
        with self.client.delete(
            f"/api/v1/users/{user_id}",
            headers=self.auth_headers,
            catch_response=True,
            name="Delete User"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Invalid response format")
            elif response.status_code == 404:
                response.success()  # User might have been already deleted
            else:
                response.failure(f"Delete user failed: {response.status_code}")
    
    @task(1)
    def get_statistics(self):
        """Get user statistics."""
        with self.client.get(
            "/api/v1/users/stats/summary",
            catch_response=True,
            name="Get Statistics"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    response.success()
                else:
                    response.failure("Invalid response format")
            else:
                response.failure(f"Get statistics failed: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Check application health."""
        with self.client.get(
            "/health",
            catch_response=True,
            name="Health Check"
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    response.success()
                else:
                    response.failure("Service not healthy")
            else:
                response.failure(f"Health check failed: {response.status_code}")


def run_load_test(
    host: str,
    users: int,
    spawn_rate: int,
    run_time: str,
    output_dir: str = "load_test_results"
) -> None:
    """Run load test with specified parameters."""
    # Setup logging
    setup_logging("INFO")
    
    # Create environment
    env = Environment(user_classes=[UserManagementUser], host=host)
    
    # Setup statistics
    env.create_local_runner()
    
    # Setup result collection
    stats_history = []
    
    @events.request.add_listener
    def on_request(request_type, name, response_time, response_length, exception, **kwargs):
        """Collect request statistics."""
        stats_history.append({
            "timestamp": events.locust.core.time.time(),
            "request_type": request_type,
            "name": name,
            "response_time": response_time,
            "response_length": response_length,
            "exception": str(exception) if exception else None,
        })
    
    # Start load test
    print(f"🚀 Starting load test against {host}")
    print(f"👥 Users: {users}")
    print(f"📈 Spawn rate: {spawn_rate} users/second")
    print(f"⏱️  Duration: {run_time}")
    print("-" * 50)
    
    env.runner.start(users, spawn_rate=spawn_rate)
    
    # Run for specified time
    import time
    
    # Parse run time
    if run_time.endswith('s'):
        duration = int(run_time[:-1])
    elif run_time.endswith('m'):
        duration = int(run_time[:-1]) * 60
    else:
        duration = int(run_time)
    
    time.sleep(duration)
    
    # Stop test
    env.runner.stop()
    
    # Generate report
    generate_performance_report(env.stats, stats_history, output_dir)


def generate_performance_report(stats, stats_history, output_dir: str) -> None:
    """Generate detailed performance report."""
    import os
    from datetime import datetime
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate summary report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_requests": stats.total.num_requests,
            "total_failures": stats.total.num_failures,
            "average_response_time": stats.total.avg_response_time,
            "min_response_time": stats.total.min_response_time,
            "max_response_time": stats.total.max_response_time,
            "requests_per_second": stats.total.current_rps,
            "failure_rate": stats.total.fail_ratio,
        },
        "endpoints": {}
    }
    
    # Add endpoint-specific statistics
    for name, endpoint_stats in stats.entries.items():
        if name != "Aggregated":
            report["endpoints"][name] = {
                "requests": endpoint_stats.num_requests,
                "failures": endpoint_stats.num_failures,
                "avg_response_time": endpoint_stats.avg_response_time,
                "min_response_time": endpoint_stats.min_response_time,
                "max_response_time": endpoint_stats.max_response_time,
                "failure_rate": endpoint_stats.fail_ratio,
            }
    
    # Save report
    report_file = os.path.join(output_dir, "performance_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Save detailed statistics
    stats_file = os.path.join(output_dir, "detailed_stats.json")
    with open(stats_file, "w") as f:
        json.dump(stats_history, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE REPORT")
    print("=" * 50)
    print(f"Total Requests: {report['summary']['total_requests']}")
    print(f"Total Failures: {report['summary']['total_failures']}")
    print(f"Failure Rate: {report['summary']['failure_rate']:.2%}")
    print(f"Average Response Time: {report['summary']['average_response_time']:.2f}ms")
    print(f"Min Response Time: {report['summary']['min_response_time']:.2f}ms")
    print(f"Max Response Time: {report['summary']['max_response_time']:.2f}ms")
    print(f"Requests/Second: {report['summary']['requests_per_second']:.2f}")
    
    print("\n📈 ENDPOINT PERFORMANCE:")
    for endpoint, stats in report["endpoints"].items():
        print(f"  {endpoint}:")
        print(f"    Requests: {stats['requests']}")
        print(f"    Avg Time: {stats['avg_response_time']:.2f}ms")
        print(f"    Failures: {stats['failures']} ({stats['failure_rate']:.2%})")
    
    print(f"\n📁 Reports saved to: {output_dir}")
    
    # Performance recommendations
    print("\n🔧 PERFORMANCE RECOMMENDATIONS:")
    
    if report['summary']['failure_rate'] > 0.01:  # >1% failure rate
        print("  ⚠️  High failure rate detected. Check error logs and server capacity.")
    
    if report['summary']['average_response_time'] > 1000:  # >1 second
        print("  ⚠️  High response times. Consider optimizing database queries or adding caching.")
    
    if report['summary']['requests_per_second'] < 50:  # <50 RPS
        print("  ⚠️  Low throughput. Consider scaling horizontally or optimizing bottlenecks.")
    
    if report['summary']['max_response_time'] > 5000:  # >5 seconds
        print("  ⚠️  Very slow requests detected. Investigate timeout issues.")
    
    if report['summary']['failure_rate'] == 0 and report['summary']['average_response_time'] < 200:
        print("  ✅ Excellent performance! The API is handling load well.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Load test User Management System API")
    parser.add_argument("--host", default="http://localhost:8000", help="Target host")
    parser.add_argument("--users", type=int, default=10, help="Number of concurrent users")
    parser.add_argument("--spawn-rate", type=int, default=2, help="Users spawned per second")
    parser.add_argument("--run-time", default="60s", help="Test duration (e.g., 60s, 5m)")
    parser.add_argument("--output-dir", default="load_test_results", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        run_load_test(
            host=args.host,
            users=args.users,
            spawn_rate=args.spawn_rate,
            run_time=args.run_time,
            output_dir=args.output_dir,
        )
    except KeyboardInterrupt:
        print("\n🛑 Load test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Load test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()