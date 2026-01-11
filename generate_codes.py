from license_manager import generate_activation_code

codes = [
    "CHARTINK-001",
    "CHARTINK-002",
    "CHARTINK-003",
    "CHARTINK-004",
]

for code in codes:
    generate_activation_code(code)
    print("Generated:", code)
