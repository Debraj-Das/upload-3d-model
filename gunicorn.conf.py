workers = 3

# Worker class
worker_class = 'gthread'

# Threads per worker
threads = 4

# Max upload size in bytes (5 GB)
limit_request_line = 0         # No limit on request line
limit_request_fields = 32768   # Max headers
limit_request_field_size = 8190
limit_request_body = 10 * 1024 * 1024 * 1024  # 10 GB

# Timeout settings
timeout = 1200  # seconds
