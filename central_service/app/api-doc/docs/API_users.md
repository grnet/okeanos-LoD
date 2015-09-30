# User-related API calls


## Get user count


### API Call

| API call | Endpoint |
| --- | --- |
|Count users| **GET /api/users/count** |

### Example API call

`curl -X GET 'http://<hostname>/api/users/count'`

### Response

```json
{
  "status": {
    "short_description": "Lambda Users count on ~okeanos infrastructure.",
    "code": 200
  },
  "data": {
    "count": "count of active users"
  }
}
```