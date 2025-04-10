"""
Test Data Generator for API Testing

Utility to generate sample test data for API testing, covering various scenarios and edge cases.
"""

import json
import random
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class TestDataGenerator:
    """Generates sample test data for API testing"""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the test data generator
        
        Args:
            seed: Random seed for reproducible data generation
        """
        if seed is not None:
            random.seed(seed)
        self.faker_available = self._check_faker()
        
    def _check_faker(self) -> bool:
        """Check if Faker is available for enhanced data generation"""
        try:
            import faker
            return True
        except ImportError:
            return False
            
    def generate_users(self, num: int = 50) -> List[Dict[str, Any]]:
        """
        Generate sample user data
        
        Args:
            num: Number of users to generate
            
        Returns:
            List of user dictionaries
        """
        users = []
        
        if self.faker_available:
            from faker import Faker
            fake = Faker()
            
            for i in range(1, num + 1):
                users.append({
                    "id": f"user_{i:03d}",
                    "email": fake.email() if i % 5 != 0 else f"invalid_email_{i}",  # 20% invalid
                    "username": fake.user_name() + str(i),
                    "created_at": fake.date_time_between(start_date="-1y").isoformat(),
                    "is_active": i % 10 != 0,  # 10% inactive
                    "roles": random.choices(["user", "admin", "moderator"], 
                                          weights=[85, 10, 5], k=random.randint(1, 2))
                })
        else:
            # Fallback without Faker
            domains = ["example.com", "test.org", "apitest.io", "example.net"]
            for i in range(1, num + 1):
                users.append({
                    "id": f"user_{i:03d}",
                    "email": f"user{i}@{random.choice(domains)}" if i % 5 != 0 else f"invalid_email_{i}",
                    "username": f"testuser_{i}",
                    "created_at": (datetime.datetime.now() - 
                                 datetime.timedelta(days=random.randint(1, 365))).isoformat(),
                    "is_active": i % 10 != 0,
                    "roles": random.choices(["user", "admin", "moderator"], 
                                          weights=[85, 10, 5], k=random.randint(1, 2))
                })
                
        return users
    
    def generate_products(self, num: int = 100) -> List[Dict[str, Any]]:
        """
        Generate sample product data
        
        Args:
            num: Number of products to generate
            
        Returns:
            List of product dictionaries
        """
        products = []
        
        if self.faker_available:
            from faker import Faker
            fake = Faker()
            
            for _ in range(num):
                products.append({
                    "sku": f"SKU-{fake.unique.bothify(text='??##').upper()}",
                    "name": fake.catch_phrase(),
                    "price": round(random.uniform(1.99, 999.99), 2),
                    "category": random.choice(["electronics", "clothing", "books", "home"]),
                    "stock": random.randint(0, 1000),
                    "tags": [fake.word() for _ in range(random.randint(0, 5))],
                    "metadata": {
                        "weight": f"{random.randint(1, 5000)}g",
                        "dimensions": f"{random.randint(1, 100)}x{random.randint(1, 100)}x{random.randint(1, 100)}cm"
                    }
                })
        else:
            # Fallback without Faker
            product_names = ["Widget", "Gadget", "Tool", "Device", "Accessory"]
            categories = ["electronics", "clothing", "books", "home"]
            tags = ["sale", "new", "featured", "popular", "premium", "limited", "exclusive"]
            
            for i in range(num):
                products.append({
                    "sku": f"SKU-{i:05d}",
                    "name": f"{random.choice(product_names)} {random.randint(1000, 9999)}",
                    "price": round(random.uniform(1.99, 999.99), 2),
                    "category": random.choice(categories),
                    "stock": random.randint(0, 1000),
                    "tags": random.sample(tags, random.randint(0, min(5, len(tags)))),
                    "metadata": {
                        "weight": f"{random.randint(1, 5000)}g",
                        "dimensions": f"{random.randint(1, 100)}x{random.randint(1, 100)}x{random.randint(1, 100)}cm"
                    }
                })
                
        return products
        
    def generate_orders(self, users: List[Dict[str, Any]], products: List[Dict[str, Any]], 
                      num: int = 200) -> List[Dict[str, Any]]:
        """
        Generate sample order data
        
        Args:
            users: List of user dictionaries for association
            products: List of product dictionaries for association
            num: Number of orders to generate
            
        Returns:
            List of order dictionaries
        """
        orders = []
        
        if not users or not products:
            raise ValueError("Users and products lists must not be empty")
        
        statuses = ["pending", "completed", "cancelled", "shipped"]
        
        for i in range(num):
            # Create random items from available products
            items = []
            for _ in range(random.randint(1, 5)):
                product = random.choice(products)
                items.append({
                    "product_id": product["sku"],
                    "quantity": random.randint(1, 5)
                })
                
            # Calculate total based on items and product prices
            total = round(sum([
                item["quantity"] * random.uniform(1.99, 99.99) 
                for item in items
            ]), 2)
                
            # Generate the order
            orders.append({
                "order_id": f"ORD-{i:06d}",
                "user_id": random.choice(users)["id"],
                "items": items,
                "status": random.choice(statuses),
                "total": total,
                "created_at": (datetime.datetime.now() - 
                             datetime.timedelta(days=random.randint(1, 180))).isoformat()
            })
            
        return orders
        
    def generate_security_test_payloads(self) -> Dict[str, List[str]]:
        """
        Generate security test payloads for testing API security
        
        Returns:
            Dictionary of security test payloads by category
        """
        return {
            "sql_injection": [
                "' OR 1=1 --",
                "'; DROP TABLE users --",
                "UNION SELECT username, password FROM users --"
            ],
            "xss_vectors": [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert(1)>",
                "javascript:alert('XSS')"
            ],
            "path_traversal": [
                "../../../../etc/passwd",
                "%2e%2e%2fetc%2fpasswd",
                "....//....//etc/passwd"
            ],
            "malformed_json": [
                '{"key": "value",}',
                '{"key": unquoted}',
                '{"trailing": "comma",}'
            ]
        }
        
    def generate_performance_test_data(self) -> Dict[str, Any]:
        """
        Generate data for performance testing
        
        Returns:
            Dictionary of performance test data
        """
        return {
            "bulk_users": self.generate_users(1000),
            "stress_products": self.generate_products(500),
            "large_payload": {
                "description": "a" * 10_000,
                "items": [{"id": str(i), "value": i*10} for i in range(1000)]
            },
            "edge_case_values": {
                "min_values": {"price": 0.01, "quantity": 1},
                "max_values": {"price": 999999.99, "quantity": 100},
                "special_chars": {
                    "name": "Ŧêßť ɲåɱȅ",
                    "email": "𝕋𝕖𝕤𝕥@𝕖𝕩𝕒𝕞𝕡𝕝𝕖.𝕔𝕠𝕞"
                }
            }
        }
        
    def generate_auth_scenarios(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Generate authentication test scenarios
        
        Returns:
            Dictionary of authentication test scenarios
        """
        return {
            "valid_credentials": [
                {"email": "user1@test.com", "password": "ValidPass123!"},
                {"email": "admin@test.com", "password": "Admin@Secure456"}
            ],
            "invalid_credentials": [
                {"email": "user1@test.com", "password": "wrongpassword"},
                {"email": "nonexistent@test.com", "password": "anypass"}
            ],
            "malformed_auth": [
                {"email": "invalid-email", "password": "short"},
                {"username": "missing_email", "password": "password"}
            ]
        }
        
    def generate_query_combinations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate API query parameter combinations
        
        Returns:
            Dictionary of query parameter combinations
        """
        return {
            "users": [
                {"status": "active", "role": "admin"},
                {"created_after": "2023-01-01", "sort": "-created_at"},
                {"search": "test", "limit": 50, "page": 2}
            ],
            "products": [
                {"category": "electronics", "min_price": 100, "max_price": 500},
                {"tags": "sale", "sort": "price"},
                {"in_stock": True, "limit": 25}
            ]
        }
        
    def generate_all(self, output_dir: str = "test-data") -> Dict[str, Any]:
        """
        Generate all sample data and save to JSON files
        
        Args:
            output_dir: Directory to save generated data
            
        Returns:
            Dictionary containing all generated data
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate all data
        data = {}
        
        # Generate core data
        users = self.generate_users(50)
        products = self.generate_products(100)
        orders = self.generate_orders(users, products, 200)
        
        data.update({
            "users": users,
            "products": products,
            "orders": orders,
            "security_payloads": self.generate_security_test_payloads(),
            "performance_data": self.generate_performance_test_data(),
            "auth_scenarios": self.generate_auth_scenarios(),
            "query_combinations": self.generate_query_combinations()
        })
        
        # Save to JSON files
        for key, value in data.items():
            with open(output_path / f"{key}.json", "w") as f:
                json.dump(value, f, indent=2)
                
        print(f"Generated test data files in '{output_dir}'")
        return data

if __name__ == "__main__":
    generator = TestDataGenerator()
    generator.generate_all() 