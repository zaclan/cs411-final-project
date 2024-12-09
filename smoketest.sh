BASE_URL="http://localhost:5000/api"

check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}
get_weather() {
  city=$1

  echo "Fetching weather data for city: $city..."
  response=$(curl -s -X GET "$BASE_URL/weather?city=$city")

  if echo "$response" | grep -q '"temperature"'; then
    echo "Weather data retrieved successfully for city: $city."
    if [ "$ECHO_JSON" = true ]; then
      echo "Weather JSON for $city:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch weather data for city: $city."
    exit 1
  fi
}

check_health
get_weather "London"
echo "All tests passed successfully!"
