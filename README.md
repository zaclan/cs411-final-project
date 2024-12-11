## **Overview** 

The Weather Viewing Application is a simple tool to obtain weather data for specific or favorite locations of a user. The user can save their most frequented or favorite locations and access their current, historical, and forecasted weather data.  

**Features:**  

1. **Save Favorite Locations**  

Users can add their favorite locations to their profile. This feature 

reduces time spent finding weather data for a frequently visited location.  

2. **Get Weather for a Favorite Location** 

Displays the current weather data for a favorite location on the user’s 

profile. This  includes the time that the weather was requested, temperature, humidity, windspeed, and precipitation. 

3. **Get Current Weather of all Favorite Locations****  

Displays the current weather data for all favorite locations on the user’s 

profile. This feature helps the user to view the weather information for the locations of their peak interest in one step. 

4. **View all Favorite Locations**  

Users can view a list of all their saved favorite locations. This helps the 

user to quickly browse and manage the list for new additions. 

5. **Get Historical weather of a Favorite**  

Provides historical weather data of a favorite city. User’s can use this 

information to analyse past weather trends or to identify climate change impacts. 

6. **Get Forecast of a Favorite** 

Presents a weather forecast of a favorite city for up to 16 days. This 

includes temperature, precipitation, daylight duration, and wind speed. 

The API uses Docker for containerisation. The user and location data is stored in SQLAlchemy. 

## **Setup Instructions** 

## **Using Docker** 

1. **Build the Docker image:**  
    ```bash
    docker build -t ${IMAGE\_NAME}:${CONTAINER\_TAG}   . 
    ```
2. **Run the Docker Container:** 
    ```bash
    docker run -d \ 

    --name ${IMAGE\_NAME}\_container \ 

    --env-file .env \ 

    -p ${HOST\_PORT}:${CONTAINER\_PORT} \ -v ${DB\_VOLUME\_PATH}:/app/db \ ${IMAGE\_NAME}:${CONTAINER\_TAG} 
    ```
## **Routes Documentation 

## /create-account** 

- **Request Type**: POST 
- **Purpose**: Creates a new user account with a username and password. 
- **Request Body**: 
- username (String): The user's chosen username. 
- password (String): The user's chosen password. 
- **Response Format**: JSON 
- **Success Response Example**: 
- **Code**: 201 

**Content**:
```json 

{ 

    "message": "Account created successfully for user 'newuser123'."
}
```

- **Error Response Example** (e.g., missing fields): 
- **Code**: 400

- **Content**:
  ```json 

{ 

  "error": "Invalid request payload. 'username' and 'password' are required." 

} 
```
- **Error Response Example** (unexpected error): 
- **Code**: 500 

**Content**:
```json 

{ 

    "error": "Internal server error." 

}
```

**Example Request**:
```json 

{** 
            "username": "newuser123", 

            "password": "securepassword" 

} 

**Example Response**:
```json 

{ 

    "message": "Account created successfully for user 'newuser123'." 

}
```

## **/login** 

- **Request Type**: POST 
- **Purpose**: Authenticates a user by verifying the provided username and password. 
- **Request Body**: 
- username (String): The user's username. 
- password (String): The user's password. 
- **Response Format**: JSON 
- **Success Response Example**: 
- **Code**: 200 

**Content**:
```json 

{ 

    "message": "User 'newuser123' authenticated successfully." 

}
```

- **Error Response Example** (e.g., invalid credentials): 
- **Code**: 401 

**Content**:
```json 

{ 

    "error": "Invalid username or password." 

}
```

- **Error Response Example** (unexpected error): 
- **Code**: 500 

**Content**:
```json 

{ 

    "error": "Internal server error." 

}
```

- **Example Request**:
  ```json 

  { 

      "username": "newuser123", 

      "password": "securepassword" 

} 
```
- **Example Response**:
```json 

  { 

      "message": "User 'newuser123' authenticated successfully."**
  }
```

## **/update-password** 

- **Request Type**: POST 
- **Purpose**: Updates a user's password by verifying the current password and setting a new one. 
- **Request Body**: 
- username (String): The username of the user requesting the password change. 
- current\_password (String): The current password of the user to verify their identity. 
- new\_password (String): The new password that the user wants to set. 
- **Response Format**: JSON 
- **Success Response Example**: 
- **Code**: 200 

**Content**:
```json 

{ 

    "message": "Password updated successfully for user       'newuser123'."
}
``` 

- **Error Response Example** (e.g., missing fields): 
- **Code**: 400 

**Content**:
```json 

{ 

    "error": "Invalid request payload. 'username', 'current\_password', and 'new\_password' are required." 

} 
```
- **Error Response Example** (invalid authentication): 
- **Code**: 401 

**Content**:
```json 

{ 

    "error": "Invalid username or password." 

} 
```
- **Error Response Example** (unexpected error): 
- **Code**: 500 

**Content**:
```json 

{ 

    "error": "Internal server error." 

} 
```
- **Example Request**:
  ```json 

  { 

        "username": "newuser123", 

        "current_password": "oldpassword", 

        "new_password": "newsecurepassword" 

} 
```
- **Example Response**:
```json 

  { 

      "message": "Password updated successfully for user 'newuser123'."**
  }
```
## **/api/favorites (POST)** 

- **Request Type**: POST 
- **Purpose**: Adds a new favorite location for a user. 
- **Request Body**: 
- username (String): The username of the user adding the favorite location. 
- password (String): The password of the user to authenticate. 
- location\_name (String): The name of the location to be added to the favorites. 
- **Response Format**: JSON 
- **Success Response Example**: 
- **Code**: 201 

**Content**:
```json 

{ 

    "message": "Favorite location 'Paris' added successfully.", 

    "favorite\_location": { 

    "id": 1, 

    "location\_name": "Paris", 

    "latitude": 48.8566, 

    "longitude": 2.3522 

} 
} 
```
- **Error Response Example** (e.g., missing location\_name): 
- **Code**: 400 

**Content**:
```json 

{ 

    "error": "Invalid request payload. 'location\_name' is required."
} 
```
- **Error Response Example** (authentication failure): 
- **Code**: 401 

**Content**:
```json 

{ 

    "error": "Invalid username or password." 

} 
```
- **Error Response Example** (unexpected error): 
- **Code**: 500 

**Content**:
```json 

{ 

    "error": "Internal server error." 

} 
```
- **Example Request**:
  ```json 

  { 

      "username": "newuser123", 

      "password": "securepassword",       "location_name": "Paris" 

} 
```
- **Example Response**:
```json 

{ 

      "message": "Favorite location 'Paris' added successfully.",   "favorite_location": { 

      "id": 1, 

      "location_name": "Paris", 

      "latitude": 48.8566, 

      "longitude": 2.3522 

  } 

}
```

## **/api/favorites (GET)** 

- **Request Type**: GET 
- **Purpose**: Retrieves all favorite locations for a user. 
- **Query Parameters**: 
- username (String): The username of the user whose favorite locations are being retrieved. 
- password (String): The password of the user for authentication. 
- **Response Format**: JSON 
- **Success Response Example**: 
- **Code**: 200 

**Content**:
```json 

{ 

    "favorites": [ 

      { 

        "id": 1, 

        "location\_name": "Paris", 

        "latitude": 48.8566, 

        "longitude": 2.3522 

  }, 

    { 

        "id": 2, 

        "location\_name": "New York",       "latitude": 40.7128, 

        "longitude": -74.0060 

    } 

  ] 

} 
```
- **Error Response Example** (missing query parameters): 
- **Code**: 400 

**Content**:
```json 

{ 

    "error": "Missing 'username' or 'password' query parameters." 

}
```

- **Error Response Example** (authentication failure): 
- **Code**: 401 

**Content**:
```json 

{ 

    "error": "Invalid username or password." 

} 
```
- **Error Response Example** (unexpected error): 
- **Code**: 500 


**Content**:
```json 

{ 

    "error": "Internal server error."
}
``` 

- **Example Request**:
  ```bash 

  GET /api/favorites?username=newuser123&password=securepassword 
  ```
- **Example Response**:
  ```json 
{ 

    "favorites": [ 

      { 

        "id": 1, 

        "location\_name": "Paris", 

        "latitude": 48.8566, 

        "longitude": 2.3522 

  }, 

    { 

        "id": 2, 

        "location\_name": "New York",       "latitude": 40.7128, 

        "longitude": -74.0060 

    } 

  ] 

  }
  ```

## **/api/favorites/weather (GET)** 

- **Request Type**: GET 
- **Purpose**: Retrieves all favorite locations for a user along with their current weather. 
- **Query Parameters**: 
- username (String): The username of the user whose favorite locations with weather are being retrieved. 
- password (String): The password of the user for authentication. 
- **Response Format**: JSON 
- **Success Response Example**: 

• **Code**: 200 
11 of 21

**Content**:
```json 

{ 

    "favorites": [ 

      { 

        "id": 1, 

        "location\_name": "Paris", 

        "latitude": 48.8566, 

        "longitude": 2.3522, 

        "current\_weather": { 

            "time": "2024-12-10T15:30:00Z"

            "temperature": 22.5

            "humidity": 60 

            "windspeed": 5.5 

            "precipitation": 0.0 

        } 

      }, 

      { 

        "id": 2, 

        "location\_name": "New York", 

        "latitude": 40.7128, 

        "longitude": -74.0060, 

        "current\_weather": { 

              "time": "2024-12-10T15:30:00Z"

              "temperature": 30.6 

              "humidity": 70 

              "windspeed": 6.5 

              "precipitation": 1.0 

        } 

      } 

    ] 

}
```

- **Error Response Example** (missing query parameters): 
- **Code**: 400 

**Content**:
```json 

{ 

    "error": "Missing 'username' or 'password' query parameters."
} 
```


- **Error Response Example** (authentication failure): 
- **Code**: 401 

**Content**:
```json 

{ 

    "error": "Invalid username or password." 

} 
```
- **Error Response Example** (unexpected error): 
- **Code**: 500 

**Content**:
```json 

{ 

    "error": "Internal server error." 

} 
```
- **Example Request**:
  ```bash 

  GET /api/favorites/weather?username=newuser123&password=securepassword 
  ```
- **Example Response**:
```json 

{ 

    "favorites": [ 

      { 

        "id": 1, 

        "location\_name": "Paris", 

        "latitude": 48.8566, 

        "longitude": 2.3522, 

        "current\_weather": { 

            "time": "2024-12-10T15:30:00Z"

            "temperature": 22.5 

            "humidity": 60 

            "windspeed": 5.5 

            "precipitation": 0.0 

        } 

      }, 

      { 

        "id": 2, 

        "location\_name": "New York", 

        "latitude": 40.7128, 

        "longitude": -74.0060, 

        "current\_weather": { 

            "time": "2024-12-10T15:30:00Z"

            "temperature": 30.6 

            "humidity": 70 

            "windspeed": 6.5 

            "precipitation": 1.0 

  }
]

} 
```
## **/api/favorites/int:favorite\_id/weather (GET)** 

- **Request Type**: GET 
- **Purpose**: Retrieves the current weather for a specific favorite location. 
- **Path Parameters**: 
- favorite\_id (int, required): The ID of the favorite location whose weather is being retrieved. 
- **Query Parameters**: 
- username (string, required): The username of the account. 
- password (string, required): The password of the account. 
- **Response Format**: JSON 
- **Success Response Example**: 
- **Code**: 200 

**Content**:
```json 

{ 

    "favorite\_location": { 

        "id": 1, 

        "location\_name": "Paris", 

        "latitude": 48.8566, 

        "longitude": 2.3522, 

        "current\_weather": { 

            "time": "2024-12-10T15:30:00Z" 

            "temperature": 22.5 

            "humidity": 60 

            "windspeed": 5.5 

            "precipitation": 0.0   } 

} 
```
- **Error Response Example** (missing query parameters): 
- **Code**: 400 

**Content**:
```json 

{ 

    "error": "Missing 'username' or 'password' query parameters." 

}
```

- **Error Response Example** (unauthorized access): 
- **Code**: 401 

**Content**:
```json 

{ 

    "error": "Invalid username or password."
} 
```
- **Error Response Example** (favorite location not found): 
- **Code**: 404 

**Content**:
```json 

{ 

    "error": "Favorite location with ID '1' not found."
} 
```
- **Error Response Example** (internal error): 
- **Code**: 500 

**Content**:
```json 

{ 

    "error": "Could not fetch weather data."
} 
```
- **Example Request**:
```bash 

  GET /api/favorites/1/weather?username=newuser123&password=securepassword 
```
**Example Response**:
```json 

{ 

    "favorite\_location": { 

      "id": 1, 

      "location\_name": "Paris", 

      "latitude": 48.8566, 

      "longitude": 2.3522, 

      "current\_weather": { 

              "time": "2024-12-10T15:30:00Z"

              "temperature": 22.5 

              "humidity": 60 

              "windspeed": 5.5 

              "precipitation": 0.0 

  } 

} 
```
## **/api/favorites/int:favorite\_id/historical (GET)** 

- **Request Type**: GET 
- **Purpose**: Retrieves historical weather data for a specific favorite location. 
- **Path Parameters**: 
- favorite\_id (int, required): The ID of the favorite location whose historical weather data is being retrieved. 
- **Query Parameters**: 
- username (string, required): The username of the account. 
- password (string, required): The password of the account. 
- start\_date (string, required): The start date for the historical weather data in 'YYYY-MM-DD' format. 
- end\_date (string, required): The end date for the historical weather data in 'YYYY-MM-DD' format. 
- **Response Format**: JSON 
- **Success Response Example**: 
- **Code**: 200 

**Content**:
```json 

{ 

    "favorite\_location": { 

      "id": 1, 

      "latitude": 48.8566, 

      "longitude": 2.3522 

    }, 

    "historical\_weather": [ 

      { 

        "date": "2024-12-01" 

        "temperature\_2m\_max": 15.2 

        "temperature\_2m\_min": 10.5 

        "apparent\_temperature\_max": 16.8

        "apparent\_temperature\_min": 9.0  

        "daylight\_duration": 9.8  

        "precipitation\_sum": 0.1 

        "precipitation\_probability\_max": 20

        "wind\_speed\_10m\_max": 7.3 

        … 

      } 

    ] 

} 
```
- **Error Response Example** (missing query parameters): 
- **Code**: 400 

**Content**:
```json 

{ 

    "error": "Missing 'username', 'password', 'start\_date', or 'end\_date' query parameters." 

} 
```
- **Error Response Example** (unauthorized access): 
- **Code**: 401 

**Content**:
```json 

{ 

    "error": "Invalid username or password."
}
```
- **Error Response Example** (favorite location not found): 
- **Code**: 404 

**Content**:
```json 

{ 

    "error": "Favorite location with ID '1' not found."
} 
```
- **Error Response Example** (internal error): 
- **Code**: 500 

**Content**:
```json 

{ 

    "error": "Could not fetch historical weather data."
} 
```
- **Example Request**:
```bash 

  GET /api/favorites/1/historical? username=newuser123&password=securepassword&start\_date=2024-12-01&end \_date=2024-12-02 
```
**Example Response**:
```json
{ 

    "favorite\_location": { 

      "id": 1, 

      "latitude": 48.8566, 

      "longitude": 2.3522 

    }, 

    "historical\_weather": [ 

      { 

        "date": "2024-12-01" 

        "temperature\_2m\_max": 15.2 

        "temperature\_2m\_min": 10.5 

        "apparent\_temperature\_max": 16.8

        "apparent\_temperature\_min": 9.0  

        "daylight\_duration": 9.8  

        "precipitation\_sum": 0.1 

        "precipitation\_probability\_max": 20

        "wind\_speed\_10m\_max": 7.3 

        … 

      } 

    ] 

} 
```

## **/api/favorites/int:favorite\_id/forecast (GET)** 

- **Request Type**: GET 
- **Purpose**: Retrieves the weather forecast for a specific favorite location. 
- **Path Parameters**: 
- favorite\_id (int, required): The ID of the favorite location whose weather forecast is being retrieved. 
- **Query Parameters**: 
- username (string, required): The username of the account. 
- password (string, required): The password of the account. 
- days (int, optional): The number of days to retrieve the forecast for (default is 7). 
- **Response Format**: JSON 
- **Success Response Example**: 
- **Code**: 200 

**Content**:
```json 

{ 

    "favorite\_location": [ 

          "id": 123 

          "latitude": 40.7128 

          "longitude": -74.0060  

},  

"historical\_weather": [  

        {  

            "date": "2024-12-01" 

            "temperature\_2m\_max": 15.2 

            "temperature\_2m\_min": 10.5 

            "apparent\_temperature\_max": 16.8 

            "apparent\_temperature\_min": 9.0  

            "daylight\_duration": 9.8 

            "precipitation\_sum": 0.1 

            "precipitation\_probability\_max": 20 

            "wind\_speed\_10m\_max": 7.3  

        }, 
        … 

    ] 

} 
```
- **Error Response Example** (missing query parameters): 
- **Code**: 400 

**Content**:
```json 

{ 

    "error": "Missing 'username' or 'password' query parameters."
} 
```
- **Error Response Example** (unauthorized access): 
- **Code**: 401 

**Content**:
```json 

{ 

    "error": "Invalid username or password."
} 
```
- **Error Response Example** (favorite location not found): 
- **Code**: 404 

**Content**:
```json 

{ 

    "error": "Favorite location with ID '1' not found."
} 
```
- **Error Response Example** (internal error): 
- **Code**: 500 

**Content**:
```json 

{ 

    "error": "Could not fetch weather forecast data."
} 
```
- **Example Request**:
```bash 

  GET /api/favorites/1/forecast? username=newuser123&password=securepassword&days=5 
```
- **Example Response**:
```json
{ 

    "favorite\_location": [ 

          "id": 123 

          "latitude": 40.7128 

          "longitude": -74.0060  

},  

"historical\_weather": [  

        {  

            "date": "2024-12-01" 

            "temperature\_2m\_max": 15.2 

            "temperature\_2m\_min": 10.5 

            "apparent\_temperature\_max": 16.8 

            "apparent\_temperature\_min": 9.0  

            "daylight\_duration": 9.8 

            "precipitation\_sum": 0.1 

            "precipitation\_probability\_max": 20 

            "wind\_speed\_10m\_max": 7.3  

        }, 
        … 

    ] 

} 
```

## **/api/health** 

- **Request Type:** GET 
- **Purpose:** Verifies if the service is running and healthy. 
- **Request Body:** None 
- **Response Format:** JSON 
- **Success Response Example:** 
  - Code: 200 
  - Content:
    ```json 

      { "status": "healthy" } 
    ```
- **Example Request:** 

  No request body needed for this endpoint. 

- **Example Response:**
  ```json 

  { 
              "status": "healthy"
  }
  ```

## **Testing** 

**Unit Tests** 

Unit tests are ran to ensure each feature works as expected:

pytest tests/

**Smoke Tests** 

Smoke tests are ran to make sure that important features are working accurately: 

sh smoktest.sh

## **Dependencies** 

- **Python libraries:**  
  - Flask
  - Migrate
  - request
  - response
  - make\_response
  - jsonify
  - pytest
  - python-dotenv
  - BadRequest
  - Unsuthorized
  - NotFound
  - SQLAlchemy
- **External API:**  
  - [Forecast API](https://open-meteo.com/en/docs) 
  - [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
