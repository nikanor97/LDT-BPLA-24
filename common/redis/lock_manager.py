import time


class RedisLockManager:
    def __init__(self, client, lock_name, lock_timeout):
        self.client = client
        self.lock_name = lock_name
        self.lock_timeout = lock_timeout
        self.lock_key = f"lock:{lock_name}"
        self.lock_value = None

    def acquire_lock(self):
        self.lock_value = str(time.time() + self.lock_timeout + 1)

        if self.client.set(self.lock_key, self.lock_value, nx=True, px=self.lock_timeout):
            return True
        else:
            # Проверка истекшей блокировки
            current_value = self.client.get(self.lock_key)
            if current_value and float(current_value) < time.time():
                old_value = self.client.getset(self.lock_key, self.lock_value)
                if old_value == current_value:
                    return True

        return False

    def release_lock(self):
        if self.lock_value:
            current_value = self.client.get(self.lock_key)
            if current_value and current_value.decode('utf-8') == self.lock_value:
                self.client.delete(self.lock_key)

    def __enter__(self):
        if not self.acquire_lock():
            raise RuntimeError("Cannot acquire lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release_lock()
