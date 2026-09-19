from fastapi import FastAPI, HTTPException
import connections
import db
import archive.caching_generic as caching_generic
app = FastAPI()
pg  =  db.PostgresCRUD()

@app.get("/{short_code}")
def get_url(short_code: str):
    # Check cache first
    cache = caching_generic.get_redis_data(short_code)
    print(cache)
    if cache:
        return {
            "short_code": short_code,
            "destination": cache.long_url
        }
    # Cache miss -> check database
    else:
        row = pg.get("urls",short_code , "short_code")
    return {
        "short_code": short_code,
        "destination": row[3],
    }


# @app.put("/urls/{short_code}")
# def update_url(short_code: str, data: UpdateURL):
#     # Check that URL exists
#     if short_code not in urls:
#         raise HTTPException(
#             status_code=404,
#             detail="URL not found"
#         )

#     # Update database
#     urls[short_code] = data.destination

#     # Update cache immediately
#     cache[short_code] = data.destination

#     return {
#         "short_code": short_code,
#         "destination": data.destination
#     }


# @app.delete("/urls/{short_code}")
# def delete_url(short_code: str):
#     # Check that URL exists
#     if short_code not in urls:
#         raise HTTPException(
#             status_code=404,
#             detail="URL not found"
#         )

#     del urls[short_code]
#     cache.pop(short_code, None)

#     return {
#         "message": "URL deleted",
#         "short_code": short_code
#     }
