BASE_URL="http://localhost:5000/"

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/api/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}
create_user() {
  echo "Creating a new user..."
  response=$(curl -s -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')

  # Check the response for the success message
  echo "$response" | grep -q "Account created successfully for user 'testuser'."
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user. Response: $response"
    exit 1
  fi
}

add_favorite_location() {
  echo "Adding a favorite location..."
  curl -s -X POST "$BASE_URL/api/favorites" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password456", "location_name":"New York"}' | grep -q '"message": "Favorite location '\''New York'\'' added successfully."'
  if [ $? -eq 0 ]; then
    echo "Favorite location added successfully."
  else
    echo "Failed to add favorite location."
    exit 1
  fi
}

login_user() {
  local username="$1"
  local password="$2"
  
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")

  # Check the response for the success message
  echo "$response" | grep -q "User '$username' authenticated successfully."
  if [ $? -eq 0 ]; then
    echo "User logged in successfully."
  else
    echo "Failed to log in user. Response: $response"
    exit 1
  fi
}



update_user_password() {
  echo "Updating user password..."
  response=$(curl -s -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "current_password":"password123", "new_password":"password456"}')

  # Check the response for the success message
  echo "$response" | grep -q "Password updated successfully for user 'testuser'."
  if [ $? -eq 0 ]; then
    echo "Password updated successfully."
  else
    echo "Failed to update password. Response: $response"
    exit 1
  fi
}

get_favorites() {
  echo "Retrieving all favorite locations..."
  response=$(curl -s -X GET "$BASE_URL/api/favorites?username=testuser&password=password456")

  # Check the response for the list of favorites
  echo "$response" | grep -q '"favorites":'
  if [ $? -eq 0 ]; then
    echo "Favorites retrieved successfully."
    echo "$response" 
  else
    echo "Failed to retrieve favorites. Response: $response"
    exit 1
  fi
}

get_favorites_with_weather() {
  echo "Retrieving all favorite locations with weather..."
  response=$(curl -s -X GET "$BASE_URL/api/favorites/weather?username=testuser&password=password456")

  # Check the response for the list of favorites with weather
  echo "$response" | grep -q '"favorites":'
  if [ $? -eq 0 ]; then
    echo "Favorites with weather retrieved successfully."
    echo "$response"  # Print the raw response
  else
    echo "Failed to retrieve favorites with weather. Response: $response"
    exit 1
  fi
}

get_weather_for_favorite() {
  local favorite_id="$1"
  
  echo "Retrieving weather for favorite location with ID: $favorite_id..."
  response=$(curl -s -X GET "$BASE_URL/api/favorites/$favorite_id/weather?username=testuser&password=password456")

  # Check the response for the weather data
  echo "$response" | grep -q '"current_weather":'
  if [ $? -eq 0 ]; then
    echo "Weather for favorite location retrieved successfully."
    echo "$response"  
  else
    echo "Failed to retrieve weather for favorite location. Response: $response"
    exit 1
  fi
}

get_historical_weather_for_favorite() {
  local favorite_id="$1"
  local start_date="$2"
  local end_date="$3"

  echo "Retrieving historical weather for favorite location with ID: $favorite_id..."
  response=$(curl -s -X GET "$BASE_URL/api/favorites/$favorite_id/historical?username=testuser&password=password456&start_date=$start_date&end_date=$end_date")

  # Check the response for the historical weather data
  echo "$response" | grep -q '"historical_weather":'
  if [ $? -eq 0 ]; then
    echo "Historical weather for favorite location retrieved successfully."
    echo "$response"  
  else
    echo "Failed to retrieve historical weather for favorite location. Response: $response"
    exit 1
  fi
}

get_forecast_for_favorite() {
  local favorite_id="$1"
  local days="$2"

  echo "Retrieving forecast for favorite location with ID: $favorite_id..."
  response=$(curl -s -X GET "$BASE_URL/api/favorites/$favorite_id/forecast?username=testuser&password=password456&days=$days")

  # Check the response for the forecast data
  echo "$response" | grep -q '"weather_forecast":'
  if [ $? -eq 0 ]; then
    echo "Forecast for favorite location retrieved successfully."
    echo "$response"  
  else
    echo "Failed to retrieve forecast for favorite location. Response: $response"
    exit 1
  fi
}


# Run the tests
check_health
create_user
login_user testuser password123
update_user_password
login_user testuser password456
add_favorite_location
get_favorites
get_favorites_with_weather
get_weather_for_favorite 1  # favorite ID is 1
get_historical_weather_for_favorite 1 "2024-12-01" "2024-12-10"  # Example dates
get_forecast_for_favorite 1 7  # Get a 7-day forecast for favorite ID 1

echo "All tests passed successfully!"

