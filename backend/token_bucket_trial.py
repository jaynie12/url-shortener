# THIS IS NOT IMPLEMENTED AT THE MINUTE. PLACE HOLDER FOR NOW 

    # def rate_limiter(self, redis_client):
    #     limiter = TokenBucket(
    #         redis_client=redis_client,
    #         capacity=3,        # 3 requests per min for inital mvp
    #         refill_rate=1,      # Add 1 token per interval
    #         refill_interval=60 # Every 60 seconds
    # )
    #     return limiter


# Increment the token bucket for the given IP address and check if the request is allowed
# Decreament count until 0
# Then if it is 0, return a 429 error code and message to the user and update the expirty timestamp. 
# If the next request comes in after the expiry timestamp, reset the count to 3 and allow the request.

