#include <WiFiS3.h>
#include "Arduino_LED_Matrix.h"

#define SECRET_SSID "CU_YJu9"  // Replace with your WiFi SSID
#define SECRET_PASS "mgqdngzq"  // Replace with your WiFi password

char ssid[] = SECRET_SSID;  // Your network SSID
char pass[] = SECRET_PASS;  // Your network password

WiFiServer server(80);  // Set up the web server on port 80

#define MAX_Y 8
#define MAX_X 12
#define TURN_DELAY 200  // Delay between each turn in milliseconds
#define TURNS_MAX 60    // Maximum number of turns before reset
#define NO_CHANGES_RESET 4  // Number of turns without changes before resetting
#define MAX_PATTERNS 4

unsigned long previousMillis = 0;
const long interval = 10000;  // Interval for sending LED matrix state to client (10 seconds)

int turns = 0; 
int noChanges = 0; 
uint8_t grid[MAX_Y][MAX_X] = {0}; 
int currentPattern = 0;

boolean cGrids[][MAX_Y][MAX_X] = {
    { /* Glider */
        {0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        {0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        {1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
    }
};

ArduinoLEDMatrix matrix;

void setup() {
  Serial.begin(9600);
  matrix.begin();

  // Initialize WiFi
  connectToWiFi();
  
  resetGrid();
  displayGrid();
  server.begin();
}

void loop() {
  unsigned long currentMillis = millis();

  // Check if 10 seconds have passed to send the LED matrix state to client
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    sendLEDMatrixState();
  }

  // Game of Life logic
  delay(TURN_DELAY);
  playGoL();  // Play a turn of the Game of Life
  turns++;

  if (noChanges > NO_CHANGES_RESET || turns > TURNS_MAX) {
    resetGrid();  // Reset if no changes for several turns or max turns reached
  }

  displayGrid();  // Display the new grid state
}

// Function to play one turn of Conway's Game of Life
void playGoL() {
  boolean newGrid[MAX_Y][MAX_X] = {0};
  int changes = 0;

  for (int y = 0; y < MAX_Y; y++) {
    for (int x = 0; x < MAX_X; x++) {
      int neighbors = countNeighbours(y, x);
      if (grid[y][x] == 1) {
        newGrid[y][x] = (neighbors == 2 || neighbors == 3) ? 1 : 0;  // Live cell stays alive
      } else {
        newGrid[y][x] = (neighbors == 3) ? 1 : 0;  // Dead cell becomes alive
      }

      // Check if there are changes
      if (newGrid[y][x] != grid[y][x]) {
        changes++;
      }
    }
  }

  // Update the grid with the new state
  for (int y = 0; y < MAX_Y; y++) {
    for (int x = 0; x < MAX_X; x++) {
      grid[y][x] = newGrid[y][x];
    }
  }

  // If no changes, increase noChanges counter
  if (changes == 0) {
    noChanges++;
  } else {
    noChanges = 0;
  }
}

// Count neighbors for a given cell
int countNeighbours(int y, int x) {
  int count = 0;
  for (int i = -1; i <= 1; i++) {
    for (int j = -1; j <= 1; j++) {
      if (i == 0 && j == 0) continue;  // Skip the cell itself
      int ny = y + i;
      int nx = x + j;
      if (ny >= 0 && ny < MAX_Y && nx >= 0 && nx < MAX_X) {
        count += grid[ny][nx];
      }
    }
  }
  return count;
}

// Function to send the current LED matrix state to the connected client
void sendLEDMatrixState() {
  WiFiClient client = server.available();
  if (client) {
    String ledMatrixState = "";
    for (int y = 0; y < MAX_Y; y++) {
      for (int x = 0; x < MAX_X; x++) {
        ledMatrixState += String(grid[y][x]) + " ";
      }
      ledMatrixState += "\n";
    }

    // Send the LED matrix state to the client
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println("Connection: close");
    client.println();
    client.println(ledMatrixState);
    client.stop();  // Close the connection

    Serial.println("LED Matrix state sent to client:");
    Serial.println(ledMatrixState);
  }
}

// Reset the grid to a predefined pattern
void resetGrid() {
  noChanges = 0;
  turns = 0;
  for (int y = 0; y < MAX_Y; y++) {
    for (int x = 0; x < MAX_X; x++) {
      grid[y][x] = cGrids[currentPattern][y][x];
    }
  }
  currentPattern = (currentPattern + 1) % MAX_PATTERNS;
}

// Display the grid on the LED matrix
void displayGrid() {
  matrix.renderBitmap(grid, MAX_Y, MAX_X);
}

// Connect to WiFi network
void connectToWiFi() {
  Serial.print("Connecting to ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    Serial.println("Failed to connect to WiFi. Retrying...");
    delay(10000);
  }
  Serial.println("Connected to WiFi");
  Serial.print("Server IP address: ");
  Serial.println(WiFi.localIP());
}
