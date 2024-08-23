import redis

try:
    client = redis.Redis(
        host="10.223.134.248",
        port=6379,
        decode_responses=True,
        socket_timeout=10,
        socket_keepalive=True
    )
    if client:
        print("db is connected")
except (redis.ConnectionError, redis.TimeoutError) as se:
    raise ConnectionError("db is not connecting: " + str(se))

def del_caching_data(session_id, filter_value):
    key = f'{session_id}:translation'
    with client.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                pipe.multi()
                
                if pipe.hexists(key, filter_value):
                    pipe.hdel(key, filter_value) 
                    pipe.execute()
                    return 1  
                else:
                    return -1 
            
            except (redis.RedisError) as err:
                raise Exception(f"Error retrieving value: {err}")

def get_caching_data(session_id, filter_value):
    key = f'{session_id}:translation'
    with client.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                pipe.multi()
                pipe.hget(key, filter_value)
                result = pipe.execute() 
                value = result[0]

                if value:
                    return value
                else:
                    return None
            
            except (redis.RedisError) as err:
                raise Exception(f"Error retrieving value: {err}")

def get_all_caching_data(session_id):
    key = f'{session_id}:translation'
    with client.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                pipe.multi()
                pipe.hgetall(key)
                result = pipe.execute()

                all_data = result[0]

                return [{"english": k, "turkish": v} for k, v in all_data.items()]
            except (redis.RedisError) as err:
                raise Exception(f'Error retrieving all values: {err}')

def set_caching_data(session_id, new_data):
    key = f'{session_id}:translation'
    with client.pipeline() as pipe:
        while True:
            try:
                pipe.watch(key)
                pipe.multi()

                if new_data:
                    english_value = new_data['english']
                    turkish_value = new_data['turkish']
                   

                    pipe.hset(key, english_value, turkish_value)
          
                    pipe.expire(key, 48 * 3600)
                    pipe.execute()
                    print(pipe.hgetall(key))  
                break
            except (redis.RedisError) as err:
                raise Exception(f"Error setting data: {err}")


